# ToolBox
Gestionnaire d'outils du quotidien, recherche avancée pour projets concrets.

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
