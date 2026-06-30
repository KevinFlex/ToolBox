"""
scripts/lbc_login.py
Se connecte à un Chrome existant en mode debug pour récupérer les cookies leboncoin.
Contourne Datadome car on utilise le vrai Chrome de l'utilisateur.

Étapes :
1. Fermer tous les Chrome ouverts
2. Lancer Chrome en mode debug avec la commande indiquée
3. Se connecter à leboncoin dans ce Chrome
4. Lancer ce script pour sauvegarder la session
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

COOKIES_FILE = Path(__file__).resolve().parents[1] / "data" / "processed" / "lbc_cookies.json"
DEBUG_URL = "http://localhost:9222"


async def main():
    print("=" * 60)
    print("  Récupération session leboncoin depuis Chrome existant")
    print("=" * 60)
    print()
    print("PRÉREQUIS : Chrome doit être lancé en mode debug.")
    print()
    print("Si ce n'est pas encore fait, ferme tous les Chrome")
    print("et lance cette commande dans un autre PowerShell :")
    print()
    print('  & "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"')
    print('    --remote-debugging-port=9222')
    print('    --user-data-dir="C:\\Users\\kevin\\AppData\\Local\\Google\\Chrome\\User Data"')
    print()
    print("Connecte-toi à leboncoin dans ce Chrome.")
    print()
    input("Appuie sur Entrée quand tu es connecté à leboncoin...")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(DEBUG_URL)
        except Exception as e:
            print()
            print(f"❌ Impossible de se connecter à Chrome : {e}")
            print()
            print("Vérifie que Chrome est bien lancé avec --remote-debugging-port=9222")
            return

        # Récupère le contexte existant (ta vraie session Chrome)
        contexts = browser.contexts
        if not contexts:
            print("❌ Aucun contexte trouvé dans Chrome.")
            return

        ctx = contexts[0]
        cookies = await ctx.cookies("https://www.leboncoin.fr")

        if not cookies:
            print("❌ Aucun cookie leboncoin trouvé. Es-tu bien connecté sur leboncoin ?")
            return

        COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=2)

        print()
        print(f"✅ Session sauvegardée — {len(cookies)} cookies leboncoin")
        print(f"   Fichier : {COOKIES_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
