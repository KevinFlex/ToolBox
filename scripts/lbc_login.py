"""
scripts/lbc_login.py

Enregistre les cookies leboncoin exportés depuis Cookie-Editor (Firefox).

Usage :
  1. Ouvre Firefox et va sur https://www.leboncoin.fr (connecté à ton compte)
  2. Ouvre Cookie-Editor → Export → copie le JSON
  3. Depuis le dossier racine du projet :

       python scripts/lbc_login.py

  4. Colle le JSON exporté (Ctrl+V), puis appuie sur Entrée deux fois
  5. Les cookies sont sauvegardés dans data/processed/lbc_cookies.json

Le fichier est ignoré par git (.gitignore couvre data/processed/*).
Il doit être renouvelé à chaque session leboncoin (le cookie datadome expire vite).
"""

import json
import sys
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "lbc_cookies.json"


def main() -> None:
    print("=" * 60)
    print("  leboncoin Cookie-Editor — import des cookies")
    print("=" * 60)
    print()
    print("Colle le JSON exporté par Cookie-Editor ci-dessous,")
    print("puis appuie sur Entrée deux fois :")
    print()

    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except EOFError:
        pass  # stdin fermé proprement (ex: echo JSON | python lbc_login.py)

    raw = "\n".join(lines).strip()
    if not raw:
        print("[ERREUR] Aucun JSON collé.", file=sys.stderr)
        sys.exit(1)

    # Validation JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"[ERREUR] JSON invalide : {e}", file=sys.stderr)
        sys.exit(1)

    # Normalisation : accepte liste Cookie-Editor OU dict {name: value}
    if isinstance(data, list):
        if not all("name" in c and "value" in c for c in data):
            print("[ERREUR] Le JSON ne ressemble pas à un export Cookie-Editor.", file=sys.stderr)
            sys.exit(1)
        names = [c["name"] for c in data]
        if "datadome" not in names:
            print("[ATTENTION] Cookie 'datadome' absent — leboncoin risque de bloquer les requêtes.")
    elif isinstance(data, dict):
        if "datadome" not in data:
            print("[ATTENTION] Cookie 'datadome' absent — leboncoin risque de bloquer les requêtes.")
    else:
        print("[ERREUR] Format inattendu (ni liste ni dict).", file=sys.stderr)
        sys.exit(1)

    # Sauvegarde
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"Cookies sauvegardés dans : {OUTPUT_PATH}")
    if isinstance(data, list):
        print(f"  {len(data)} cookies enregistrés")
    else:
        print(f"  {len(data)} clés enregistrées")
    print()
    print("Tu peux maintenant relancer le scraper leboncoin depuis Streamlit.")


if __name__ == "__main__":
    main()
