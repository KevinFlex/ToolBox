"""
Module véhicule — scoring.py
Attribue un score à chaque annonce selon les critères définis dans docs/utilitaire.md.

Critères positifs :
  +3  Modèle cible (Trafic, Jumpy, Expert)
  +2  Prix ≤ 5 500 €
  +2  Kilométrage entre 100 000 et 220 000 km
  +2  Fourgon tôlé / vide (mots-clés dans le titre ou description)
  +1  Dans un rayon de 80 km autour de Montpellier

Critères négatifs :
  -3  Mots-clés rédhibitoires (accidenté, épave, pour pièces, boîte cassée...)
"""

from .scraping import Annonce

# Modèles prioritaires issus de docs/utilitaire.md
KEY_MODELS = [
    "trafic", "jumpy", "expert",
]

# Mots indiquant un fourgon vide, adapté au couchage et à l'usage artisan
POSITIVE_WORDS = [
    "fourgon", "tôlé", "tole", "vide", "utilitaire",
]

# Mots rédhibitoires
BAD_WORDS = [
    "accidenté", "accidente", "épave", "epave",
    "pour pièces", "pour pieces", "boîte cassée", "boite cassee",
    "non roulant", "à réparer", "a reparer",
]

MAX_PRICE = 5_500
MIN_KM = 100_000
MAX_KM = 220_000
MAX_DISTANCE_KM = 80


def score_annonce(annonce: Annonce) -> Annonce:
    """Calcule et affecte le score d'une annonce. Retourne l'annonce enrichie."""
    text = " ".join(filter(None, [annonce.title, annonce.description])).lower()
    score = 0

    # Modèle cible
    if any(m in text for m in KEY_MODELS):
        score += 3

    # Prix
    if annonce.price_eur is not None and annonce.price_eur <= MAX_PRICE:
        score += 2

    # Kilométrage
    if annonce.mileage_km is not None and MIN_KM <= annonce.mileage_km <= MAX_KM:
        score += 2

    # Fourgon vide / tôlé
    if any(w in text for w in POSITIVE_WORDS):
        score += 2

    # Proximité Montpellier
    if annonce.distance_km is not None and annonce.distance_km <= MAX_DISTANCE_KM:
        score += 1

    # Pénalités
    if any(w in text for w in BAD_WORDS):
        score -= 3

    annonce.score = score
    return annonce


def score_all(annonces: list[Annonce]) -> list[Annonce]:
    """Score toutes les annonces et les retourne triées par score décroissant."""
    scored = [score_annonce(a) for a in annonces]
    return sorted(scored, key=lambda a: a.score or 0, reverse=True)
