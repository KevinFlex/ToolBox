# Filtres — Module Véhicule Utilitaire

> Ce fichier est la source de vérité des filtres actifs sur l'interface.
> Il est mis à jour automatiquement quand tu modifies un filtre depuis Streamlit.
> Tu peux aussi l'éditer manuellement — les changements seront pris en compte au prochain lancement.

---

## Filtres actifs

```yaml
- id: prix_max
  label: Prix max (€)
  type: slider
  min: 500
  max: 20000
  default: 5500
  step: 100
  actif: true
  description: Budget maximum pour l'achat du véhicule.
- id: km_max
  label: Kilométrage max (km)
  type: slider
  min: 50000
  max: 350000
  default: 220000
  step: 10000
  actif: true
  description: Kilométrage maximum acceptable. Au-delà, risque mécanique plus élevé.
- id: dist_max
  label: Distance max de Montpellier (km)
  type: slider
  min: 50
  max: 800
  default: 300
  step: 25
  actif: true
  description: Rayon de recherche autour de Montpellier. Au-delà, le déplacement pour
    voir le véhicule n'est plus rentable.
- id: score_min
  label: Score minimum
  type: slider
  min: 0
  max: 10
  default: 5
  step: 1
  actif: true
  description: Filtre les annonces en dessous d'un score de pertinence. Le score tient
    compte du prix, du km, du modèle et de la distance.
- id: modeles
  label: Modèles
  type: multiselect
  options:
  - Trafic
  - Jumpy
  - Expert
  default:
  - Trafic
  - Jumpy
  - Expert
  actif: true
  description: Modèles de fourgons ciblés. Trafic, Jumpy et Expert sont les références
    pour un usage artisan/couchage à 1,72 m.
```
