"""
Module véhicule — carburant.py
Suivi de la consommation et des pleins.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Plein:
    date: date
    km_compteur: int
    litres: float
    prix_litre: float
    station: Optional[str] = None

    @property
    def cout_total(self) -> float:
        return round(self.litres * self.prix_litre, 2)


def consommation_moyenne(pleins: list[Plein]) -> Optional[float]:
    """Retourne la consommation moyenne en L/100 km sur la liste de pleins."""
    if len(pleins) < 2:
        return None
    km_parcourus = pleins[-1].km_compteur - pleins[0].km_compteur
    litres_total = sum(p.litres for p in pleins[1:])  # le 1er plein est le point de départ
    if km_parcourus == 0:
        return None
    return round((litres_total / km_parcourus) * 100, 2)


def cout_aux_100(pleins: list[Plein]) -> Optional[float]:
    """Retourne le coût moyen en € pour 100 km."""
    if len(pleins) < 2:
        return None
    km_parcourus = pleins[-1].km_compteur - pleins[0].km_compteur
    cout_total = sum(p.cout_total for p in pleins[1:])
    if km_parcourus == 0:
        return None
    return round((cout_total / km_parcourus) * 100, 2)
