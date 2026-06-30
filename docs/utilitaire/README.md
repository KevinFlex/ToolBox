# kevin-toolbox — Note de projet

*Dernière mise à jour : juin 2026*

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
│   ├── utilitaire.md         ← Tes critères de sélection de véhicule, checklist avant visite
│   ├── immobilier.md         ← À remplir quand tu attaqueras ce module
│   ├── quotidien.md          ← À remplir
│   └── roadmap.md            ← Ce qui est prévu
│
├── tests/                    ← Tests automatisés (à développer)
├── scripts/                  ← Scripts utilitaires (export, déploiement...)
│
├── requirements.txt          ← Liste des bibliothèques Python nécessaires
├── pyproject.toml            ← Configuration du package Python
└── Makefile                  ← Raccourcis de commandes (install, test, run)
```

---

## Comment lancer l'interface

```powershell
# Dans le dossier du projet
$env:PYTHONPATH = "src"
python -m streamlit run app/streamlit_app.py
```

L'interface s'ouvre dans ton navigateur sur `http://localhost:8501`.

---

## Comment fonctionne le module véhicule

1. **Recherche** — `scraping.py` interroge AutoScout24 et récupère les annonces de Trafic, Jumpy et Expert sous 6 500 €
2. **Distance** — `geocoding.py` calcule à vol d'oiseau la distance entre Montpellier et la ville de chaque annonce, via OpenStreetMap (gratuit, sans clé API)
3. **Score** — `scoring.py` attribue des points selon les critères de `docs/utilitaire.md` :
   - +3 si c'est un modèle cible (Trafic, Jumpy, Expert)
   - +2 si le prix est ≤ 5 500 €
   - +2 si le km est entre 100 000 et 220 000
   - +2 si fourgon tôlé / vide
   - +1 si dans les 80 km de Montpellier
   - -3 si mots rédhibitoires (épave, accidenté, pour pièces...)
4. **Stockage** — `storage.py` sauvegarde tout dans `data/processed/vehicule.db` avec la date de première et dernière vue
5. **Interface** — `streamlit_app.py` lit la base et affiche les annonces avec filtres paramétrables

---

## Branches Git

| Branche | Rôle |
|---|---|
| `main` | Version stable, ne jamais casser |
| `dev` | Intégration — ce qui sera bientôt sur main |
| `app/utilitaire` | Branche de développement du module véhicule |

**Workflow** : on code sur `app/utilitaire` → on merge dans `dev` pour tester → quand c'est stable, on merge `dev` dans `main`.

---

## Ce qui reste à faire (roadmap)

- [ ] Module immobilier — scraping annonces immo, scoring, carte
- [ ] Module finance — budget mensuel, cashflow, estimations
- [ ] Module quotidien — météo, rappels, suivi heures
- [ ] Alertes nouvelles annonces véhicule par email/notification
- [ ] Déploiement Streamlit Cloud pour accès depuis n'importe où

---

*Projet personnel de Kévin Vegiotti — usage privé*
