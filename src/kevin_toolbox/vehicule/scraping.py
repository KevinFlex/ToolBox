"""
Module véhicule — scraping.py
Récupère les annonces de véhicules utilitaires sur leboncoin, paruvendu, lacentrale.
Les résultats bruts sont retournés sous forme de liste de dicts.
"""

import requests
from dataclasses import dataclass, field
from typing import Optional


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


# Paramètres de recherche par défaut
SEARCHES = [
    {"source": "leboncoin", "query": "trafic montpellier"},
    {"source": "leboncoin", "query": "jumpy montpellier"},
    {"source": "leboncoin", "query": "expert montpellier"},
    {"source": "paruvendu", "query": "utilitaire montpellier"},
    {"source": "lacentrale", "query": "utilitaire montpellier"},
]

MAX_PRICE = 5500
MIN_KM = 100_000
MAX_KM = 220_000
MAX_DISTANCE_KM = 80
COORD_MONTPELLIER = (43.6117, 3.8767)


def fetch_leboncoin(query: str) -> list[Annonce]:
    """
    Placeholder — leboncoin ne dispose pas d'API publique officielle.
    À remplacer par une solution headless (Playwright) ou un service tiers.
    Retourne une liste vide pour l'instant.
    """
    # TODO: implémenter avec Playwright ou une lib tierce (ex: lbc-api)
    print(f"[leboncoin] Recherche : {query!r} — non implémenté (API privée)")
    return []


def fetch_paruvendu(query: str) -> list[Annonce]:
    """
    Placeholder — paruvendu.
    À implémenter selon les possibilités d'accès (HTML ou API).
    """
    print(f"[paruvendu] Recherche : {query!r} — non implémenté")
    return []


def fetch_lacentrale(query: str) -> list[Annonce]:
    """
    Placeholder — lacentrale.
    À implémenter selon les possibilités d'accès.
    """
    print(f"[lacentrale] Recherche : {query!r} — non implémenté")
    return []


FETCHERS = {
    "leboncoin": fetch_leboncoin,
    "paruvendu": fetch_paruvendu,
    "lacentrale": fetch_lacentrale,
}


def run_searches(searches: list[dict] = SEARCHES) -> list[Annonce]:
    """Lance toutes les recherches et retourne la liste consolidée d'annonces."""
    results: list[Annonce] = []
    for search in searches:
        source = search["source"]
        query = search["query"]
        fetcher = FETCHERS.get(source)
        if fetcher:
            annonces = fetcher(query)
            results.extend(annonces)
        else:
            print(f"[scraping] Source inconnue : {source!r}")
    return results
