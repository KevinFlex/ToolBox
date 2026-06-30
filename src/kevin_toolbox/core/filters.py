"""
core/filters.py
Lecture et écriture des filtres depuis/vers les fichiers docs/<module>/filtres.md.
Chaque module a son propre fichier filtres.md — source de vérité des paramètres UI.

Format du bloc YAML dans le .md :
```yaml
- id: prix_max
  label: "Prix max (€)"
  type: slider        # slider | multiselect | toggle
  min: 500
  max: 20000
  default: 5500
  step: 100
  actif: true
  description: "..."
```
"""

import re
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

BASE_DIR = Path(__file__).resolve().parents[3]
DOCS_DIR = BASE_DIR / "docs"


def _filtres_path(module: str) -> Path:
    """Retourne le chemin du fichier filtres.md d'un module."""
    return DOCS_DIR / module / "filtres.md"


def _extract_yaml(content: str) -> str:
    """Extrait le bloc YAML du fichier .md (entre les balises ```yaml ... ```)."""
    match = re.search(r"```yaml\n(.*?)```", content, re.DOTALL)
    return match.group(1) if match else ""


def _replace_yaml(content: str, new_yaml: str) -> str:
    """Remplace le bloc YAML dans le contenu .md."""
    return re.sub(
        r"(```yaml\n)(.*?)(```)",
        f"```yaml\n{new_yaml}```",
        content,
        flags=re.DOTALL,
    )


def load_filtres(module: str) -> list[dict]:
    """
    Charge les filtres depuis docs/<module>/filtres.md.
    Retourne une liste de dicts, un par filtre.
    Retourne une liste vide si le fichier n'existe pas.
    """
    path = _filtres_path(module)
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")
    yaml_block = _extract_yaml(content)
    if not yaml_block:
        return []

    if yaml is None:
        raise ImportError("PyYAML est requis : pip install pyyaml")

    filtres = yaml.safe_load(yaml_block)
    return filtres if isinstance(filtres, list) else []


def save_filtres(module: str, filtres: list[dict]) -> None:
    """
    Sauvegarde les filtres dans docs/<module>/filtres.md.
    Préserve tout le contenu Markdown existant, remplace uniquement le bloc YAML.
    """
    if yaml is None:
        raise ImportError("PyYAML est requis : pip install pyyaml")

    path = _filtres_path(module)
    if not path.exists():
        raise FileNotFoundError(f"Fichier filtres introuvable : {path}")

    content = path.read_text(encoding="utf-8")
    new_yaml = yaml.dump(filtres, allow_unicode=True, sort_keys=False, default_flow_style=False)
    new_content = _replace_yaml(content, new_yaml)
    path.write_text(new_content, encoding="utf-8")


def update_filtre(module: str, filtre_id: str, **kwargs) -> None:
    """
    Met à jour un ou plusieurs champs d'un filtre par son id.
    Ex : update_filtre("utilitaire", "prix_max", default=6000, actif=True)
    """
    filtres = load_filtres(module)
    for f in filtres:
        if f.get("id") == filtre_id:
            f.update(kwargs)
            break
    save_filtres(module, filtres)


def get_filtre(module: str, filtre_id: str) -> dict | None:
    """Retourne un filtre spécifique par son id."""
    for f in load_filtres(module):
        if f.get("id") == filtre_id:
            return f
    return None
