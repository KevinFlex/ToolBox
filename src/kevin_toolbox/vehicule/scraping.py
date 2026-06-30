"""
Module véhicule — scraping.py

Récupère les annonces de véhicules utilitaires depuis AutoScout24 (FR).
Source retenue : AutoScout24 expose ses données via __NEXT_DATA__ JSON embarqué,
contrairement à leboncoin/lacentrale qui bloquent les requêtes automatisées (Datadome).

Modèles ciblés  : Renault Trafic, Citroën Jumpy, Peugeot Expert
Budget          : ≤ 5 500 €
Kilométrage     : 100 000 – 220 000 km
Zone            : 150 km autour de Montpellier (34000)
"""

import re
import time
import requests
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# Modèle de données
# ---------------------------------------------------------------------------

@dataclass
class Annonce:
    url: str
    source: str
    title: str
    price_eur: Optional[int] = None
    mileage_km: Optional[int] = None
    year: Optional[int] = None
    city: Optional[str] = None
    fuel: Optional[str] = None
    gearbox: Optional[str] = None
    description: Optional[str] = None
    distance_km: Optional[float] = None
    score: Optional[float] = None
    image_url: Optional[str] = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://www.autoscout24.fr"

MODELS = [
    ("renault", "trafic"),
    ("citroen", "jumpy"),
    ("peugeot", "expert"),
]

MAX_PRICE   = 5_500
MIN_KM      = 100_000
MAX_KM      = 220_000
ZIP_CODE    = "34000"
MAX_DIST_KM = 150   # Filtre de distance appliqué en post-traitement (si distance disponible)
MAX_PAGES   = 5     # Limite de pages par modèle
PRICE_FETCH = 6_500 # Prix max pour la requête (plus large que MAX_PRICE pour avoir du volume)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_url(make: str, model: str, page: int = 1) -> str:
    """
    Construit l'URL de recherche AutoScout24.

    Comportement observé sur AS24 FR :
    - zip seul   : retourne les annonces avec distance calculée, mais peu de résultats
    - zip + kmto : vide complètement les résultats (bug AS24)
    - sans zip   : retourne tous les résultats FR, distance non calculée

    Stratégie retenue : recherche nationale sans zip, filtres km/distance en post-traitement.
    """
    return (
        f"{BASE_URL}/lst/{make}/{model}"
        f"?atype=C&cy=F"
        f"&priceto={PRICE_FETCH}"
        f"&sort=price&ustate=N%2CU"
        f"&page={page}"
    )


def _parse_km(mileage_str: Optional[str]) -> Optional[int]:
    """Extrait la valeur numérique d'une chaîne comme '151 000 km'."""
    if not mileage_str:
        return None
    digits = re.sub(r"\D", "", mileage_str)
    return int(digits) if digits else None


def _parse_listings(html: str) -> list[dict]:
    """Extrait la liste d'annonces depuis le JSON __NEXT_DATA__ embarqué."""
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html, re.DOTALL
    )
    if not match:
        return []
    import json
    try:
        data = json.loads(match.group(1))
        return data["props"]["pageProps"].get("listings", []) or []
    except (json.JSONDecodeError, KeyError):
        return []


def _item_to_annonce(item: dict) -> Optional[Annonce]:
    """Convertit un item brut AutoScout24 en objet Annonce."""
    try:
        v     = item.get("vehicle", {}) or {}
        price = item.get("price", {}) or {}
        loc   = item.get("location", {}) or {}

        price_raw = price.get("priceRaw")
        mileage   = _parse_km(v.get("mileageInKm"))
        title     = f"{v.get('make', '')} {v.get('model', '')} {v.get('modelVersionInput', '')}".strip()
        url       = BASE_URL + item.get("url", "")

        # Première image disponible
        images = item.get("images") or []
        image_url = images[0] if images else None

        return Annonce(
            url         = url,
            source      = "autoscout24",
            title       = title,
            price_eur   = int(price_raw) if price_raw is not None else None,
            mileage_km  = mileage,
            year        = v.get("firstRegistrationYear"),
            city        = loc.get("city"),
            fuel        = v.get("fuel"),
            gearbox     = v.get("transmission"),
            distance_km = loc.get("distanceToSearchLocationInKm"),
            image_url   = image_url,
        )
    except Exception as e:
        print(f"[scraping] Erreur parsing item : {e}")
        return None


# ---------------------------------------------------------------------------
# Fetchers
# ---------------------------------------------------------------------------

def fetch_autoscout24(make: str, model: str, max_pages: int = MAX_PAGES, max_dist_km: float = MAX_DIST_KM) -> list[Annonce]:
    """Récupère les annonces AutoScout24 pour un couple make/model, avec pagination et filtre de distance."""
    annonces: list[Annonce] = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, max_pages + 1):
        url = _build_url(make, model, page)
        try:
            r = session.get(url, timeout=15)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"[autoscout24] Erreur requête ({make}/{model} p{page}) : {e}")
            break

        items = _parse_listings(r.text)
        if not items:
            break  # Plus de résultats

        for item in items:
            annonce = _item_to_annonce(item)
            if annonce:
                # Filtre km en post-traitement
                if annonce.mileage_km is not None and annonce.mileage_km > MAX_KM:
                    continue
                # Filtre prix strict
                if annonce.price_eur is not None and annonce.price_eur > MAX_PRICE:
                    continue
                # Filtre distance si disponible
                if annonce.distance_km is not None and annonce.distance_km > max_dist_km:
                    continue
                annonces.append(annonce)

        print(f"[autoscout24] {make}/{model} — page {page} : {len(items)} annonces")
        time.sleep(1)  # Politesse

    return annonces


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def run_searches(models: list[tuple] = MODELS) -> list[Annonce]:
    """Lance la recherche sur tous les modèles et retourne la liste consolidée."""
    all_annonces: list[Annonce] = []
    for make, model in models:
        results = fetch_autoscout24(make, model)
        print(f"  → {len(results)} annonces pour {make}/{model}")
        all_annonces.extend(results)
    # Dédoublonnage par URL
    seen = set()
    unique = []
    for a in all_annonces:
        if a.url not in seen:
            seen.add(a.url)
            unique.append(a)
    print(f"\n[scraping] Total unique : {len(unique)} annonces")
    return unique


if __name__ == "__main__":
    annonces = run_searches()
    for a in annonces[:5]:
        print(f"{a.title} | {a.price_eur}€ | {a.mileage_km} km | {a.city} ({a.distance_km} km)")
