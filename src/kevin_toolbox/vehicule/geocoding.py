"""
Module véhicule — geocoding.py
Calcule la distance routière approximative entre Montpellier et la ville d'une annonce.
Utilise l'API Nominatim (OpenStreetMap) — gratuite, sans clé API.

Règles d'utilisation Nominatim :
- 1 requête par seconde maximum
- User-Agent obligatoire avec nom du projet
"""

import time
import math
import requests
from functools import lru_cache

# Coordonnées de Montpellier (point de référence)
MONTPELLIER_LAT = 43.6117
MONTPELLIER_LNG = 3.8767

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "kevin-toolbox/0.1 (kevin.vegiotti@gmail.com)"
}

# Cache en mémoire pour éviter les requêtes répétées sur la même ville
_cache: dict[str, tuple[float, float] | None] = {}


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance à vol d'oiseau en km entre deux coordonnées GPS (formule Haversine)."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def geocode_city(city: str, country: str = "France") -> tuple[float, float] | None:
    """
    Retourne les coordonnées (lat, lng) d'une ville via Nominatim.
    Retourne None si la ville n'est pas trouvée.
    """
    if not city:
        return None

    cache_key = f"{city.lower()},{country.lower()}"
    if cache_key in _cache:
        return _cache[cache_key]

    params = {
        "q": f"{city}, {country}",
        "format": "json",
        "limit": 1,
        "addressdetails": 0,
    }

    try:
        time.sleep(1.1)  # Respect de la limite Nominatim : 1 req/s
        r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        results = r.json()
        if results:
            lat = float(results[0]["lat"])
            lng = float(results[0]["lon"])
            _cache[cache_key] = (lat, lng)
            return (lat, lng)
    except Exception as e:
        print(f"[geocoding] Erreur pour {city!r} : {e}")

    _cache[cache_key] = None
    return None


def distance_from_montpellier(city: str) -> float | None:
    """
    Retourne la distance à vol d'oiseau en km entre Montpellier et la ville donnée.
    Retourne None si la ville ne peut pas être géocodée.
    """
    coords = geocode_city(city)
    if coords is None:
        return None
    lat, lng = coords
    return round(_haversine(MONTPELLIER_LAT, MONTPELLIER_LNG, lat, lng), 1)


def enrich_distances(annonces: list) -> list:
    """
    Enrichit une liste d'Annonces avec la distance Montpellier → ville.
    Utilise le champ distance_km existant si déjà renseigné.
    """
    for annonce in annonces:
        if annonce.distance_km is None and annonce.city:
            dist = distance_from_montpellier(annonce.city)
            if dist is not None:
                annonce.distance_km = dist
                print(f"[geocoding] {annonce.city} → {dist} km de Montpellier")
    return annonces
