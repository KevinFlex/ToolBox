"""
scripts/lbc_login.py
Sauvegarde les cookies leboncoin exportés via Cookie-Editor (Firefox/Chrome).

Utilisation :
1. Ouvre Firefox et connecte-toi à leboncoin
2. Clique sur l'icône Cookie-Editor → Export → copie le JSON
3. Lance ce script : python scripts/lbc_login.py
4. Colle le JSON quand demandé, puis Entrée deux fois
"""

import json
import sys
from pathlib import Path

COOKIES_FILE = Path(__file__).resolve().parents[1] / "data" / "processed" / "lbc_cookies.json"


def main():
    print("=" * 55)
    print("  Sauvegarde session leboncoin — Cookie-Editor")
    print("=" * 55)
    print()
    print("Colle le JSON exporté depuis Cookie-Editor,")
    print("puis appuie deux fois sur Entrée :")
    print()

    lines = []
    try:
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
    except EOFError:
        pass

    raw = "\n".join(lines).strip()
    if not raw:
        print("❌ Aucun contenu collé.")
        sys.exit(1)

    try:
        cookies = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ JSON invalide : {e}")
        sys.exit(1)

    if not isinstance(cookies, list):
        print("❌ Le JSON doit être une liste de cookies.")
        sys.exit(1)

    # Vérifie qu'on a bien le cookie datadome
    names = [c.get("name") for c in cookies]
    if "datadome" not in names:
        print("⚠️  Cookie 'datadome' absent — assure-toi d'être sur leboncoin.fr avant d'exporter.")

    COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    # Normalise le format pour notre scraper
    normalized = [{"name": c["name"], "value": c["value"], "domain": c.get("domain", ".leboncoin.fr")} for c in cookies]
    with open(COOKIES_FILE, "w") as f:
        json.dump(normalized, f, indent=2)

    print()
    print(f"✅ {len(cookies)} cookies sauvegardés → {COOKIES_FILE}")
    print()
    print("Tu peux maintenant lancer la recherche leboncoin depuis Streamlit.")


if __name__ == "__main__":
    main()
