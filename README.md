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
│   └── streamlit_app.py
│         L'interface que tu ouvres dans le navigateur. Elle lit la base de données
│         locale et affiche les annonces en cartes ou tableau. C'est ici que tu
│         choisis les filtres, lances une nouvelle recherche (AutoScout24 et/ou
│         leboncoin), et consultes le détail d'une annonce.
│
├── src/kevin_toolbox/
│   │     Tout le code Python. Organisé par module métier — chaque sous-dossier
│   │     correspond à un sujet (véhicule, immo, finance, quotidien).
│   │
│   ├── core/
│   │   │     Briques partagées par tous les modules.
│   │   │
│   │   ├── paths.py
│   │   │     Centralise les chemins vers data/, docs/, etc.
│   │   │     Évite d'avoir des chemins écrits en dur à plusieurs endroits.
│   │   │
│   │   ├── filters.py
│   │   │     Lit et écrit les filtres paramétrables depuis docs/utilitaire/filtres.md
│   │   │     (format YAML dans Markdown). C'est le pont entre l'interface Streamlit
│   │   │     et le fichier .md — si tu changes un filtre dans l'UI, il est mis à
│   │   │     jour dans le fichier, et inversement.
│   │   │
│   │   ├── logging_setup.py
│   │   │     Configure les logs pour voir ce qui se passe lors d'une exécution
│   │   │     (erreurs, infos, debug). Utilisé par tous les autres modules.
│   │   │
│   │   └── utils.py
│   │         Petites fonctions réutilisables : nettoyage de texte, conversions, etc.
│   │
│   ├── vehicule/
│   │   │     Module le plus avancé. Gère toute la recherche de fourgons utilitaires :
│   │   │     collecte des annonces, calcul de distance, scoring, stockage.
│   │   │
│   │   ├── scraping.py
│   │   │     Récupère les annonces sur AutoScout24 via leur JSON embarqué (__NEXT_DATA__).
│   │   │     Stratégie : recherche nationale sans code postal (bug AS24 : zip + kmto = 0
│   │   │     résultats), puis filtre de distance appliqué en Python après coup.
│   │   │
│   │   ├── lbc_scraping.py
│   │   │     Récupère les annonces sur leboncoin. Utilise les cookies exportés depuis
│   │   │     Firefox (extension Cookie-Editor) pour passer le filtre anti-bot Datadome.
│   │   │     Important : le cookie datadome est lié à ton IP Firefox — il ne fonctionne
│   │   │     que depuis ton PC, pas depuis un serveur distant.
│   │   │
│   │   ├── scoring.py
│   │   │     Attribue un score à chaque annonce selon les critères définis dans
│   │   │     docs/utilitaire/filtres.md :
│   │   │       +3  modèle cible (Trafic, Jumpy, Expert)
│   │   │       +2  fourgon tôlé / vide
│   │   │       +2  prix ≤ 5 500 €
│   │   │       +2  annonce récente (< 30 jours)
│   │   │       +2  distance ≤ 80 km de Montpellier
│   │   │       +1  distance ≤ 180 km
│   │   │       +1  kilométrage entre 100 000 et 220 000 km
│   │   │       -3  mots rédhibitoires (épave, accidenté, pour pièces...)
│   │   │
│   │   ├── geocoding.py
│   │   │     Calcule la distance à vol d'oiseau entre Montpellier et la ville de
│   │   │     chaque annonce. Utilise l'API OpenStreetMap (Nominatim) — gratuit,
│   │   │     sans clé API, avec mise en cache pour ne pas surcharger le service.
│   │   │
│   │   ├── storage.py
│   │   │     Sauvegarde les annonces dans vehicule.db (SQLite).
│   │   │     Gère les doublons : si une annonce existe déjà (même URL), elle met à
│   │   │     jour last_seen sans dupliquer. Stocke aussi first_seen pour savoir
│   │   │     depuis combien de temps une annonce est en ligne.
│   │   │
│   │   ├── entretien.py
│   │   │     Checklist de points à vérifier avant de se déplacer voir un véhicule
│   │   │     (carrosserie, moteur, boîte, papiers, historique...).
│   │   │
│   │   ├── carburant.py
│   │   │     Suivi des pleins : date, litres, prix, kilométrage.
│   │   │     Calcule la consommation moyenne au fil du temps.
│   │   │
│   │   └── amenagement.py
│   │         Suivi des aménagements prévus ou réalisés sur le véhicule
│   │         (isolation, lit, étagères...) avec coût estimé et réel.
│   │
│   ├── immobilier/       (module en attente — stubs vides)
│   │   ├── scraping.py   À coder : recherche d'annonces immo
│   │   ├── scoring.py    À coder : critères immo (surface, prix/m², quartier)
│   │   ├── geocoding.py  À coder : distance aux transports, commerces
│   │   └── reports.py    À coder : synthèse et export
│   │
│   ├── finance/          (module en attente — stubs vides)
│   │   ├── budget.py     À coder : budget mensuel
│   │   ├── cashflow.py   À coder : entrées / sorties
│   │   └── estimations.py  À coder : projections financières
│   │
│   └── quotidien/        (module en attente — stubs vides)
│       ├── meteo.py      À coder : météo du jour
│       ├── reminders.py  À coder : rappels
│       └── heures.py     À coder : suivi du temps de travail
│
├── data/
│   ├── processed/
│   │   ├── vehicule.db        Base SQLite locale. Toutes les annonces sont ici,
│   │   │                       avec leur score, leur distance, et leurs dates.
│   │   │                       Non versionné dans git (données locales).
│   │   └── lbc_cookies.json   Cookies Firefox pour leboncoin (Cookie-Editor).
│   │                           Non versionné dans git — données sensibles de session.
│   │                           À renouveler via scripts/lbc_login.py quand leboncoin bloque.
│   ├── raw/                   Données brutes non traitées (réservé pour plus tard).
│   └── references/            Fichiers de référence : grilles de prix, barèmes...
│
├── docs/
│   │     Documentation métier, pas technique. Ce que tu veux retenir sur tes
│   │     projets — pas comment le code fonctionne, mais pourquoi ces choix.
│   │
│   ├── utilitaire/
│   │   ├── README.md     Note complète sur le module véhicule : stratégie, bugs
│   │   │                  connus (AS24, Datadome), comment s'en servir.
│   │   └── filtres.md    Source de vérité pour les filtres Streamlit.
│   │                      Modifié depuis l'interface → mis à jour ici en YAML.
│   ├── utilitaire.md     Critères de sélection personnels, checklist avant visite.
│   ├── immobilier.md     À remplir quand tu attaqueras ce module.
│   ├── quotidien.md      À remplir.
│   └── roadmap.md        Ce qui est prévu.
│
├── scripts/
│   │     Scripts à lancer manuellement depuis le terminal.
│   │
│   ├── lbc_login.py       Importe les cookies Cookie-Editor dans lbc_cookies.json.
│   │                       À relancer à chaque fois que leboncoin bloque (cookie expiré) :
│   │                         1. Firefox → leboncoin.fr (connecté)
│   │                         2. Cookie-Editor → Export → copier JSON
│   │                         3. python scripts/lbc_login.py → coller → Entrée×2
│   │
│   ├── update_daily.sh    Mise à jour quotidienne (AutoScout24 + vérification drivers).
│   ├── export_reports.py  Export des annonces en CSV ou PDF.
│   └── deploy_streamlit.sh  Déploiement vers Streamlit Cloud.
│
├── tests/
│   │     Tests automatisés — vérifient que le code ne casse pas quand on modifie.
│   ├── test_vehicule.py
│   ├── test_immobilier.py
│   ├── test_finance.py
│   └── test_quotidien.py
│
├── requirements.txt    Liste des bibliothèques Python à installer
│                        (requests, beautifulsoup4, streamlit, pandas, pyyaml...).
├── pyproject.toml      Configuration du package Python (nom, version, build system).
├── Makefile            Raccourcis : `make install`, `make run`, `make test`.
└── .gitignore          Fichiers exclus de git : données sensibles, cache Python,
                         base SQLite, cookies de session.
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
