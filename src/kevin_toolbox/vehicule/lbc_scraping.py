"""
Module véhicule — lbc_scraping.py

Récupère les annonces de véhicules utilitaires depuis leboncoin.fr.

Stratégie : session authentifiée via cookies exportés depuis Firefox (extension Cookie-Editor).
Le cookie `datadome` contourne la protection anti-bot, mais il est lié à la session Firefox
et expire rapidement. Il faut le renouveler depuis le PC utilisateur avant chaque scraping.

Critères de recherche :
  - Modèles : Trafic, Jumpy, Expert  (recherches séparées)
  - Prix max : 10 000 €
  - Zone     : 180 km autour de Montpellier (34000, lat/lon : 43.6117 / 3.8767)
  - Tri      : par date (plus récent en premier)

Critères rédhibitoires (post-traitement) :
  - Kilométrage > 250 000 km
  - Prix > 10 000 €

Fichier cookies : data/processed/lbc_cookies.json
  → Exporter depuis Firefox Cookie-Editor, puis exécuter scripts/lbc_login.py

Renouvellement cookies :
  1. Firefox → leboncoin.fr (connecté)
  2. Cookie-Editor → Export → copier JSON
  3. python scripts/lbc_login.py → coller JSON → Entrée×2
"""

import json
import re
import time
from pathlib import Path
from typing import Optional

import requests

from .scraping import Annonce

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

COOKIES_PATH = Path(__file__).resolve().parents[3] / "data" / "processed" / "lbc_cookies.json"

BASE_URL = "https://www.leboncoin.fr"
# Coordonnées Montpellier + rayon 180 km (en mètres pour leboncoin)
LOCATION_PARAM = "Montpellier_34000__43.6117_3.8767_180000"

MAX_PRICE_EUR   = 10_000
MAX_KM          = 250_000
MAX_PAGES       = 3      # 30 annonces par page × 3 = 90 max par modèle
DELAY_SECONDS   = 2      # Politesse inter-requêtes

SEARCH_TERMS = ["trafic fourgon", "jumpy fourgon", "expert fourgon"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
        "Gecko/20100101 Firefox/124.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
}


# ---------------------------------------------------------------------------
# Gestion des cookies
# ---------------------------------------------------------------------------

def load_cookies(path: Path = COOKIES_PATH) -> dict:
    """
    Charge les cookies depuis le fichier JSON exporté par Cookie-Editor.

    Cookie-Editor exporte une liste d'objets avec les champs :
      name, value, domain, path, secure, httpOnly, sameSite, expirationDate, ...

    Retourne un dict {name: value} compatible requests.Session.cookies.update().

    Raises FileNotFoundError si le fichier n'existe pas (cookies non configurés).
    Raises ValueError si le format JSON est inattendu.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Fichier cookies introuvable : {path}\n"
            "→ Ouvre Firefox, va sur leboncoin.fr, exporte tes cookies avec Cookie-Editor,\n"
            "  puis lance : python scripts/lbc_login.py"
        )

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError(f"Fichier cookies vide : {path}")

    data = json.loads(raw)

    # Cookie-Editor peut exporter une liste ou un dict racine
    if isinstance(data, list):
        return {c["name"]: c["value"] for c in data if "name" in c and "value" in c}
    elif isinstance(data, dict):
        # Format simplifié {name: value} déjà prêt
        return data
    else:
        raise ValueError(f"Format de cookies inattendu dans {path}")


# ---------------------------------------------------------------------------
# Helpers de parsing
# ---------------------------------------------------------------------------

def _build_search_url(search_text: str, page: int = 1) -> str:
    """
    Construit l'URL de recherche leboncoin.

    Catégorie 2 = Voitures.
    Le filtre de localisation inclut rayon 180 km autour de Montpellier.
    """
    text_encoded = requests.utils.quote(search_text)
    return (
        f"{BASE_URL}/recherche"
        f"?category=2"
        f"&text={text_encoded}"
        f"&locations={LOCATION_PARAM}"
        f"&price=max-{MAX_PRICE_EUR}"
        f"&sort=time"
        f"&order=desc"
        f"&page={page}"
    )


def _parse_km(text: Optional[str]) -> Optional[int]:
    """Extrait la valeur numérique depuis '151 000 km' → 151000."""
    if not text:
        return None
    digits = re.sub(r"\D", "", str(text))
    return int(digits) if digits else None


def _parse_price(text: Optional[str]) -> Optional[int]:
    """Extrait la valeur numérique depuis '5 500 €' → 5500."""
    if not text:
        return None
    digits = re.sub(r"\D", "", str(text))
    return int(digits) if digits else None


def _extract_annonces_from_page(html: str) -> list[dict]:
    """
    Extrait les annonces depuis le HTML leboncoin.

    Leboncoin embarque ses données dans un script JSON `window.__NEXT_DATA__`
    (même pattern qu'AutoScout24). On préfère ça au parsing HTML fragile.
    """
    match = re.search(
        r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    if match:
        try:
            data = json.loads(match.group(1))
            props = data.get("props", {}).get("pageProps", {})
            ads = props.get("searchData", {}).get("ads", [])
            if not ads:
                ads = props.get("ads", [])
            return ads
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    return []


def _ad_to_annonce(ad: dict) -> Optional[Annonce]:
    """
    Convertit un objet annonce leboncoin (NEXT_DATA) en objet Annonce.

    Structure typique d'un ad leboncoin :
    {
      "list_id": 12345,
      "subject": "Renault Trafic L2H1 ...",
      "url": "https://www.leboncoin.fr/voitures/12345.htm",
      "price": [5000],
      "location": {"city": "Montpellier", "zipcode": "34000", ...},
      "attributes": [
        {"key": "mileage", "value": "151000", ...},
        {"key": "regdate", "value": "2015-01-01", ...},
        ...
      ],
      "images": {"urls": ["https://..."], ...},
      "first_publication_date": "2024-06-01 10:00:00",
      "body": "Description...",
    }
    """
    try:
        url = ad.get("url") or f"{BASE_URL}/voitures/{ad.get('list_id')}.htm"

        # Prix
        price_list = ad.get("price", [])
        price = int(price_list[0]) if price_list else None

        # Localisation
        loc = ad.get("location", {}) or {}
        city = loc.get("city") or loc.get("city_label")

        # Attributs clés (mileage, année, carburant, boîte)
        attrs = {a["key"]: a.get("value_label") or a.get("value")
                 for a in ad.get("attributes", []) if "key" in a}

        mileage_km = _parse_km(attrs.get("mileage"))
        year_str = attrs.get("regdate") or attrs.get("vehicle_damage_year", "")
        year = int(str(year_str)[:4]) if year_str and str(year_str)[:4].isdigit() else None
        fuel = attrs.get("fuel")
        gearbox = attrs.get("gearbox")

        # Date de publication (pour scoring récence)
        pub_date = ad.get("first_publication_date")  # "2024-06-01 10:00:00"

        title = ad.get("subject", "")
        description = ad.get("body", "")

        # Stockage date dans description si pas de champ dédié dans Annonce
        if pub_date and description is not None:
            description = f"[pub:{pub_date}] {description}"

        return Annonce(
            url=url,
            source="leboncoin",
            title=title,
            price_eur=price,
            mileage_km=mileage_km,
            year=year,
            city=city,
            fuel=fuel,
            gearbox=gearbox,
            description=description,
            # distance_km: calculée en post-traitement par geocoding.py
        )
    except Exception as e:
        print(f"[lbc_scraping] Erreur parsing annonce : {e}")
        return None


# ---------------------------------------------------------------------------
# Scraper principal
# ---------------------------------------------------------------------------

def fetch_leboncoin(
    search_terms: list[str] = SEARCH_TERMS,
    max_pages: int = MAX_PAGES,
    cookies_path: Path = COOKIES_PATH,
) -> list[Annonce]:
    """
    Récupère les annonces leboncoin pour les termes de recherche donnés.

    Args:
        search_terms: Liste de termes à rechercher (ex: ["trafic fourgon", "jumpy fourgon"])
        max_pages: Nombre de pages max par terme (30 annonces/page)
        cookies_path: Chemin vers le fichier JSON de cookies Cookie-Editor

    Returns:
        Liste d'Annonce dédoublonnées (par URL), filtrées sur prix et km.

    Raises:
        FileNotFoundError: Si les cookies ne sont pas configurés.
        RuntimeError: Si leboncoin retourne une page Datadome (cookies expirés).
    """
    # Chargement des cookies — peut lever FileNotFoundError
    cookies = load_cookies(cookies_path)

    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(cookies)

    all_annonces: list[Annonce] = []
    seen_urls: set[str] = set()

    for term in search_terms:
        print(f"[leboncoin] Recherche : '{term}'")

        for page in range(1, max_pages + 1):
            url = _build_search_url(term, page)
            print(f"  page {page} → {url}")

            try:
                resp = session.get(url, timeout=20)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"[leboncoin] Erreur réseau ({term} p{page}) : {e}")
                break

            # Détection blocage Datadome
            if "datadome" in resp.text.lower() and "captcha" in resp.text.lower():
                raise RuntimeError(
                    "Leboncoin a retourné une page Datadome (cookies expirés ou invalides).\n"
                    "→ Renouvelle les cookies depuis Firefox :\n"
                    "  1. Firefox → leboncoin.fr (connecté)\n"
                    "  2. Cookie-Editor → Export → copier JSON\n"
                    "  3. python scripts/lbc_login.py → coller → Entrée×2"
                )

            ads = _extract_annonces_from_page(resp.text)
            if not ads:
                print(f"  → Aucune annonce extraite (fin de pagination ou structure inattendue)")
                break

            page_count = 0
            for ad in ads:
                annonce = _ad_to_annonce(ad)
                if annonce is None:
                    continue

                # Dédoublonnage
                if annonce.url in seen_urls:
                    continue
                seen_urls.add(annonce.url)

                # Filtres rédhibitoires
                if annonce.price_eur is not None and annonce.price_eur > MAX_PRICE_EUR:
                    continue
                if annonce.mileage_km is not None and annonce.mileage_km > MAX_KM:
                    continue

                all_annonces.append(annonce)
                page_count += 1

            print(f"  → {page_count} annonces retenues (page {page})")
            time.sleep(DELAY_SECONDS)

    print(f"\n[leboncoin] Total unique retenu : {len(all_annonces)} annonces")
    return all_annonces


# ---------------------------------------------------------------------------
# Test rapide en ligne de commande
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    try:
        annonces = fetch_leboncoin()
        for a in annonces[:10]:
            print(f"{a.title} | {a.price_eur}€ | {a.mileage_km} km | {a.city}")
    except (FileNotFoundError, RuntimeError) as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        sys.exit(1)
