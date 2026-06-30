"""
scripts/lbc_login.py
Ouvre un navigateur Chromium visible pour se connecter à leboncoin manuellement.
Sauvegarde les cookies de session dans data/processed/lbc_cookies.json.
À lancer une seule fois (ou quand la session expire).
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

COOKIES_FILE = Path(__file__).resolve().parents[1] / "data" / "processed" / "lbc_cookies.json"


async def main():
    print("=" * 55)
    print("  Connexion leboncoin — sauvegarde de session")
    print("=" * 55)
    print()
    print("1. Un navigateur Chromium va s'ouvrir.")
    print("2. Connecte-toi à ton compte leboncoin.")
    print("3. Une fois connecté, reviens ici et appuie sur Entrée.")
    print()
    input("Appuie sur Entrée pour ouvrir le navigateur...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="fr-FR",
            viewport={"width": 1280, "height": 800},
        )
        page = await ctx.new_page()
        await page.goto("https://www.leboncoin.fr/", wait_until="domcontentloaded")

        print()
        print("Navigateur ouvert. Connecte-toi à leboncoin.")
        print("Quand tu es connecté, reviens ici.")
        print()
        input("Appuie sur Entrée une fois connecté pour sauvegarder la session...")

        # Sauvegarde des cookies
        cookies = await ctx.cookies()
        COOKIES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=2)

        print()
        print(f"✅ Session sauvegardée ({len(cookies)} cookies)")
        print(f"   Fichier : {COOKIES_FILE}")
        print()
        print("Tu peux fermer le navigateur.")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
