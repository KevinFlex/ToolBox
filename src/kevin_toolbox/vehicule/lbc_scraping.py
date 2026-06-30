"""
Module véhicule — lbc_scraping.py
Scraper leboncoin via cookies de session (Cookie-Editor).

Cookies requis : data/processed/lbc_cookies.json
Pour renouveler les cookies : ouvrir Firefox, se connecter à leboncoin,
exporter via Cookie-Editor, remplacer le fichier.

Critères de filtre (rédhibitoires — éliminés avant stockage) :
  - Prix > 10 000 €
  - Kilométrage > 250 000 km
  - Mots clés : épave, accidenté, pour pièces, non roulant...

Recherches : Trafic, Jumpy, Expert — rayon 180 km autour de Montpellier
"""

import re
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from .scraping import Annonce

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL      = "https://www.leboncoin.fr"
COOKIES_FILE  = Path(__file__).resolve().parents[3] / "data" / "processed" / "lbc_cookies.json"

MAX_PRICE     = 10_000
MAX_KM        = 250_000
MAX_DIST_KM   = 180
MAX_PAGES     = 5

# Coordonnées Montpellier (rayon en mètres pour l'URL leboncoin)
LAT           = 43.6117
LNG           = 3.8767
RADIUS_M      = 180_000  # 180 km

SEARCHES = [
    "trafic fourgon",
    "jumpy fourgon",
    "expert fourgon",
    "trafic tôlé",
    "jumpy tôlé",
    "expert tôlé",
]

BAD_WORDS = [
    "épave", "epave", "accidenté", "accidente",
    "pour pièces", "pour pieces", "non roulant",
    "à réparer", "a reparer", "boîte cassée",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Referer": "https://www.leboncoin.fr/",
}


# ---------------------------------------------------------------------------
# Gestion des cookies
# ---------------------------------------------------------------------------

def _load_cookies() -> requests.cookies.RequestsCookieJar:
    """Charge les cookies depuis le fichier JSON."""
    if not COOKIES_FILE.exists():
        raise FileNotFoundError(
            f"Fichier cookies introuvable : {COOKIES_FILE}\n"
            "Lance scripts/lbc_login.py pour renouveler la session."
        )
    with open(COOKIES_FILE) as f:
        cookies_raw = json.load(f)

    jar = requests.cookies.RequestsCookieJar()
    for c in cookies_raw:
        jar.set(c["name"], c["value"], domain=c.get("domain", ".leboncoin.fr"), path="/")
    return jar


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _build_url(query: str, page: int = 1) -> str:
    return (
        f"{BASE_URL}/recherche"
        f"?category=2"
        f"&text={requests.utils.quote(query)}"
        f"&locations=Montpellier_34000__{LAT}_{LNG}_{RADIUS_M}"
        f"&price=max-{MAX_PRICE}"
        f"&page={page}"
    )


def _parse_km(attrs: list) -> int | None:
    """Extrait le kilométrage depuis les attributs leboncoin."""
    for attr in attrs:
        if attr.get("key") == "mileage":
            val = attr.get("value_label", "") or ""
            digits = re.sub(r"\D", "", val)
            return int(digits) if digits else None
    return None


def _parse_fuel(attrs: list) -> str | None:
    for attr in attrs:
        if attr.get("key") == "fuel":
            return attr.get("value_label")
    return None


def _parse_gearbox(attrs: list) -> str | None:
    for attr in attrs:
        if attr.get("key") == "gearbox":
            return attr.get("value_label")
    return None


def _item_to_annonce(item: dict) -> Annonce | None:
    """Convertit un item brut leboncoin en Annonce."""
    try:
        attrs     = item.get("attributes") or []
        subject   = item.get("subject", "")
        body      = item.get("body", "")
        text      = f"{subject} {body}".lower()

        # Filtre rédhibitoire — mots clés
        if any(w in text for w in BAD_WORDS):
            return None

        price_list = item.get("price") or []
        price      = int(price_list[0]) if price_list else None

        # Filtre rédhibitoire — prix
        if price and price > MAX_PRICE:
            return None

        mileage = _parse_km(attrs)

        # Filtre rédhibitoire — kilométrage
        if mileage and mileage > MAX_KM:
            return None

        # Image principale
        images    = item.get("images", {})
        img_urls  = images.get("urls") or images.get("urls_large") or []
        image_url = img_urls[0] if img_urls else (images.get("thumb_url") or images.get("small_url"))

        # Ville
        loc       = item.get("location") or {}
        city      = loc.get("city") or loc.get("city_label")

        # Date de publication
        pub_date  = item.get("first_publication_date", "")

        return Annonce(
            url         = item.get("url", f"{BASE_URL}/ad/voitures/{item.get('list_id')}"),
            source      = "leboncoin",
            title       = subject,
            price_eur   = price,
            mileage_km  = mileage,
            year        = None,  # leboncoin ne l'expose pas directement dans la liste
            city        = city,
            fuel        = _parse_fuel(attrs),
            gearbox     = _parse_gearbox(attrs),
            description = body[:500] if body else pub_date,
            image_url   = image_url,
        )
    except Exception as e:
        print(f"[lbc] Erreur parsing item : {e}")
        return None


def _fetch_page(session: requests.Session, query: str, page: int) -> list[dict]:
    """Récupère une page de résultats leboncoin."""
    url = _build_url(query, page)
    try:
        r = session.get(url, timeout=15)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"[lbc] Erreur requête ({query} p{page}) : {e}")
        return []

    match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        r.text, re.DOTALL
    )
    if not match:
        print(f"[lbc] Pas de __NEXT_DATA__ pour {query!r} p{page} — session expirée ?")
        return []

    try:
        data = json.loads(match.group(1))
        ads = (
            data.get("props", {})
                .get("pageProps", {})
                .get("searchData", {})
                .get("ads", [])
        )
        return ads or []
    except (json.JSONDecodeError, KeyError):
        return []


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def fetch_leboncoin(searches: list[str] = SEARCHES, max_pages: int = MAX_PAGES) -> list[Annonce]:
    """
    Lance toutes les recherches leboncoin et retourne les annonces filtrées.
    Nécessite data/processed/lbc_cookies.json valide.
    """
    jar = _load_cookies()
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(jar)

    all_annonces: list[Annonce] = []
    seen_ids: set[str] = set()

    for query in searches:
        for page in range(1, max_pages + 1):
            items = _fetch_page(session, query, page)
            if not items:
                break

            new = 0
            for item in items:
                uid = str(item.get("list_id", ""))
                if uid in seen_ids:
                    continue
                seen_ids.add(uid)

                annonce = _item_to_annonce(item)
                if annonce:
                    all_annonces.append(annonce)
                    new += 1

            print(f"[lbc] {query!r} p{page} : {len(items)} items, {new} retenus")
            time.sleep(2)  # Politesse — leboncoin est sensible

        time.sleep(1)

    print(f"\n[lbc] Total : {len(all_annonces)} annonces après filtrage")
    return all_annonces
