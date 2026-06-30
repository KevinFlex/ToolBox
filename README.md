# ToolBox
Gestionnaire d'outils du quotidien, recherche avancée pour projets concrets.

---

## C'est quoi ce projet ?

**kevin-toolbox** est ton gestionnaire d'outils personnels. L'idée de base : automatiser les petites tâches du quotidien qui prennent du temps — chercher un véhicule, suivre ses finances, gérer l'entretien de sa voiture, etc.

Pour l'instant, le module le plus avancé est le **module véhicule utilitaire**, qui permet de rechercher, scorer et comparer des annonces de fourgons (Trafic, Jumpy, Expert) autour de Montpellier.

---

## Arborescence expliquée

```
ToolBox/
│
├── app/
│   └── streamlit_app.py      ← L'interface visuelle. C'est ce que tu lances dans ton navigateur.
│                               Elle lit la base de données et affiche les annonces en cartes ou tableau.
│
├── src/kevin_toolbox/        ← Tout le code Python du projet
│   │
│   ├── core/                 ← Briques communes (chemins, logs, utilitaires)
│   │
│   ├── vehicule/             ← Module le plus avancé — recherche de fourgons
│   │   ├── scraping.py       ← Va chercher les annonces sur AutoScout24
│   │   ├── lbc_scraping.py   ← Va chercher les annonces sur leboncoin (via cookies Firefox)
│   │   ├── scoring.py        ← Attribue un score à chaque annonce (prix, km, modèle, distance)
│   │   ├── geocoding.py      ← Calcule la distance entre Montpellier et la ville de l'annonce
│   │   ├── storage.py        ← Sauvegarde tout dans une base SQLite locale
│   │   ├── entretien.py      ← Checklist de vérification avant de se déplacer voir un véhicule
│   │   ├── carburant.py      ← Suivi des pleins et consommation
│   │   └── amenagement.py    ← Suivi des aménagements prévus/réalisés
│   │
│   ├── immobilier/           ← Module en attente — recherche d'annonces immo
│   ├── finance/              ← Module en attente — budget, cashflow
│   └── quotidien/            ← Module en attente — météo, rappels, heures
│
├── data/
│   ├── raw/                  ← Données brutes (non traitées)
│   ├── processed/
│   │   └── vehicule.db       ← Ta base SQLite locale — toutes tes annonces sont ici
│   └── references/           ← Fichiers de référence (grilles, barèmes...)
│
├── docs/                     ← Documentation métier (pas technique)
│   ├── utilitaire/README.md  ← Note complète sur le module véhicule
│   ├── utilitaire.md         ← Tes critères de sélection, checklist avant visite
│   ├── immobilier.md         ← À remplir quand tu attaqueras ce module
│   ├── quotidien.md          ← À remplir
│   └── roadmap.md            ← Ce qui est prévu
│
├── tests/                    ← Tests automatisés (à développer)
├── scripts/                  ← Scripts utilitaires (export, déploiement...)
│   └── lbc_login.py          ← Import des cookies leboncoin depuis Cookie-Editor
│
├── requirements.txt          ← Liste des bibliothèques Python nécessaires
├── pyproject.toml            ← Configuration du package Python
└── Makefile                  ← Raccourcis de commandes (install, test, run)
```

---

## Documentation par module

Chaque module a sa propre note explicative : comment ça fonctionne, pourquoi ces choix techniques, et comment s'en servir.

| Module | Note explicative |
|---|---|
| 🚐 Véhicule utilitaire | [`docs/utilitaire/README.md`](docs/utilitaire/README.md) |
| 🏠 Immobilier | `docs/immobilier/` *(à venir)* |
| 💰 Finance | `docs/finance/` *(à venir)* |
| 📅 Quotidien | `docs/quotidien/` *(à venir)* |

---

## Lancer l'interface

```powershell
$env:PYTHONPATH = "src"
python -m streamlit run app/streamlit_app.py
```

---

## Branches

| Branche | Rôle |
|---|---|
| `main` | Version stable |
| `dev` | Intégration avant mise en prod |
| `app/utilitaire` | Développement module véhicule |

---

## Ce qui reste à faire (roadmap)

- [ ] Module immobilier — scraping annonces immo, scoring, carte
- [ ] Module finance — budget mensuel, cashflow, estimations
- [ ] Module quotidien — météo, rappels, suivi heures
- [ ] Fiches quotidiennes de révision — cartes mémo dans `app/quotidien/`
- [ ] Déploiement Streamlit Cloud pour accès depuis n'importe où

---

*Projet personnel de Kévin Vegiotti — usage privé*
