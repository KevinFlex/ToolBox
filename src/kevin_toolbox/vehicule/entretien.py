"""
Module véhicule — entretien.py
Checklist de vérification avant déplacement, basée sur docs/utilitaire.md.
Permet de générer un rapport de points à vérifier pour une annonce donnée.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChecklistItem:
    categorie: str
    question: str
    reponse: Optional[str] = None
    ok: Optional[bool] = None


# Checklist issue de docs/utilitaire.md
CHECKLIST_AVANT_DEPLACEMENT: list[ChecklistItem] = [
    ChecklistItem(
        categorie="Carrosserie",
        question="Photo du plancher arrière nu et des passages de roue (rouille ?) ?",
    ),
    ChecklistItem(
        categorie="Dimensions",
        question="Longueur utile mesurée au sol (pas 'à vue') — suffisant pour dormir à 1,72 m ?",
    ),
    ChecklistItem(
        categorie="Administratif",
        question="Contrôle technique récent (< 6 mois) ?",
    ),
    ChecklistItem(
        categorie="Mécanique",
        question="Facture distribution / courroie accessoires disponible ?",
    ),
    ChecklistItem(
        categorie="Mécanique",
        question="Facture embrayage disponible ?",
    ),
    ChecklistItem(
        categorie="Mécanique",
        question="Facture injecteurs disponible ?",
    ),
    ChecklistItem(
        categorie="Électrique",
        question="Voyant moteur allumé au tableau de bord ?",
    ),
    ChecklistItem(
        categorie="Électrique",
        question="Voyant airbag allumé au tableau de bord ?",
    ),
    ChecklistItem(
        categorie="Électrique",
        question="Photo compartiment moteur (état général, fuites) ?",
    ),
    ChecklistItem(
        categorie="Électrique",
        question="Photo boîtier fusibles (état, fils bricolés) ?",
    ),
]


def afficher_checklist() -> None:
    """Affiche la checklist dans le terminal."""
    print("\n=== Checklist avant déplacement — Véhicule utilitaire ===\n")
    categorie_courante = ""
    for i, item in enumerate(CHECKLIST_AVANT_DEPLACEMENT, 1):
        if item.categorie != categorie_courante:
            print(f"\n[{item.categorie}]")
            categorie_courante = item.categorie
        statut = "✅" if item.ok is True else ("❌" if item.ok is False else "⬜")
        print(f"  {statut} {i}. {item.question}")
    print()


def rapport_checklist(annonce_title: str = "") -> str:
    """Retourne un rapport texte de la checklist pour une annonce donnée."""
    lignes = [f"Checklist — {annonce_title}", "=" * 50]
    for item in CHECKLIST_AVANT_DEPLACEMENT:
        statut = "OK" if item.ok is True else ("NOK" if item.ok is False else "?")
        reponse = f" → {item.reponse}" if item.reponse else ""
        lignes.append(f"[{statut}] [{item.categorie}] {item.question}{reponse}")
    return "\n".join(lignes)


if __name__ == "__main__":
    afficher_checklist()
