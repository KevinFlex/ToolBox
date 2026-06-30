"""
Module véhicule — amenagement.py
Suivi des aménagements réalisés ou planifiés sur le véhicule.
Usage : d'abord vide (transport/couchage), puis aménagement artisan progressif.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from enum import Enum


class Statut(str, Enum):
    PLANIFIE = "planifié"
    EN_COURS = "en cours"
    REALISE = "réalisé"


@dataclass
class Amenagement:
    nom: str
    description: str
    statut: Statut = Statut.PLANIFIE
    cout_eur: Optional[float] = None
    date_realisation: Optional[date] = None
    notes: Optional[str] = None


# Liste de référence des aménagements typiques pour un utilitaire artisan
AMENAGEMENTS_TYPE: list[Amenagement] = [
    Amenagement(
        nom="Isolation phonique et thermique",
        description="Laine de mouton ou Thinsulate sur parois et plancher.",
        statut=Statut.PLANIFIE,
    ),
    Amenagement(
        nom="Revêtement de sol",
        description="Contreplaqué + linoléum ou dalle caoutchouc.",
        statut=Statut.PLANIFIE,
    ),
    Amenagement(
        nom="Couchage",
        description="Plate-forme en contreplaqué, longueur utile ≥ 1,80 m, rangement dessous.",
        statut=Statut.PLANIFIE,
    ),
    Amenagement(
        nom="Étagères / casiers outils",
        description="Étagères latérales en alu ou bois pour rangement matériel artisan.",
        statut=Statut.PLANIFIE,
    ),
    Amenagement(
        nom="Prise 220V / batterie auxiliaire",
        description="Batterie de service + convertisseur pour outillage électrique.",
        statut=Statut.PLANIFIE,
    ),
]


def budget_total(amenagements: list[Amenagement]) -> float:
    """Retourne le budget total estimé des aménagements avec un coût renseigné."""
    return sum(a.cout_eur for a in amenagements if a.cout_eur is not None)


def afficher_suivi(amenagements: list[Amenagement] = AMENAGEMENTS_TYPE) -> None:
    """Affiche le suivi des aménagements dans le terminal."""
    print("\n=== Suivi aménagements véhicule ===\n")
    for a in amenagements:
        cout = f"{a.cout_eur} €" if a.cout_eur else "—"
        print(f"  [{a.statut.value.upper()}] {a.nom} ({cout})")
        print(f"    {a.description}")
    print(f"\nBudget estimé total : {budget_total(amenagements)} €\n")
