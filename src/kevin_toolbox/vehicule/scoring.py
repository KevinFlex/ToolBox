"""
Module véhicule — scoring.py
Attribue un score à chaque annonce selon les critères définis.

Critères positifs :
  +3  Modèle cible (Trafic, Jumpy, Expert)
  +2  Fourgon tôlé / vide
  +2  Prix ≤ 5 500 €
  +2  Annonce < 30 jours
  +2  Distance ≤ 80 km de Montpellier
  +1  Distance entre 80 et 180 km
  +1  Kilométrage entre 100 000 et 220 000 km

Critères négatifs :
  -3  Mots rédhibitoires (épave, accidenté, pour pièces...)
"""

from datetime import datetime, timezone
from .scraping import Annonce

KEY_MODELS = ["trafic", "jumpy", "expert"]

POSITIVE_WORDS = ["fourgon", "tôlé", "tole", "vide", "utilitaire"]

BAD_WORDS = [
    "épave", "epave", "accidenté", "accidente",
    "pour pièces", "pour pieces", "non roulant",
    "à réparer", "a reparer", "boîte cassée", "boite cassee",
]

PRICE_GOOD    = 5_500
MIN_KM_GOOD   = 100_000
MAX_KM_GOOD   = 220_000
DIST_CLOSE    = 80
DIST_FAR      = 180
RECENT_DAYS   = 30


def _is_recent(description: str | None) -> bool:
    """
    Détecte si l'annonce a moins de 30 jours.
    leboncoin stocke la date de publication dans le champ description (first_publication_date).
    AutoScout24 ne fournit pas ce champ — retourne False par défaut.
    """
    if not description:
        return False
    # Format leboncoin : "2026-05-29 23:18:39"
    try:
        pub = datetime.strptime(description[:19], "%Y-%m-%d %H:%M:%S")
        pub = pub.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - pub).days <= RECENT_DAYS
    except (ValueError, TypeError):
        return False


def score_annonce(annonce: Annonce) -> Annonce:
    """Calcule et affecte le score d'une annonce. Retourne l'annonce enrichie."""
    text = " ".join(filter(None, [annonce.title, annonce.description])).lower()
    score = 0

    # Modèle cible
    if any(m in text for m in KEY_MODELS):
        score += 3

    # Fourgon tôlé / vide
    if any(w in text for w in POSITIVE_WORDS):
        score += 2

    # Prix
    if annonce.price_eur is not None and annonce.price_eur <= PRICE_GOOD:
        score += 2

    # Annonce récente (< 30 jours)
    if _is_recent(annonce.description):
        score += 2

    # Distance
    if annonce.distance_km is not None:
        if annonce.distance_km <= DIST_CLOSE:
            score += 2
        elif annonce.distance_km <= DIST_FAR:
            score += 1

    # Kilométrage dans la plage idéale
    if annonce.mileage_km is not None and MIN_KM_GOOD <= annonce.mileage_km <= MAX_KM_GOOD:
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
