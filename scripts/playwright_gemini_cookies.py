import asyncio
from playwright.async_api import async_playwright
import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.conf')

async def extract_gemini_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        print("[Playwright] Opening Gemini login page...")
        await page.goto("https://gemini.google.com/")
        print("[Playwright] Please log in to Gemini in the opened browser window.")
        input("Press Enter here after you have logged in and see the Gemini chat interface...")
        cookies = await context.cookies()
        print("[Playwright] All cookies after login:")
        for cookie in cookies:
            print(f"  {cookie['name']} (domain: {cookie['domain']}): {cookie['value'][:8]}... (len={len(cookie['value'])})")
        psid = None
        psidts = None
        for cookie in cookies:
            if cookie['name'] == '__Secure-1PSID':
                psid = cookie['value']
            if cookie['name'] == '__Secure-1PSIDTS':
                psidts = cookie['value']
        await browser.close()
        if not psid or not psidts:
            print("[Playwright] Could not find Gemini cookies. Make sure you are logged in and see the chat interface.")
            return False
        # Update config.conf
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH, encoding='utf-8')
        if 'Cookies' not in config:
            config['Cookies'] = {}
        config['Cookies']['gemini_cookie_1PSID'] = psid
        config['Cookies']['gemini_cookie_1PSIDTS'] = psidts
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            config.write(f)
        print("[Playwright] Gemini cookies updated in config.conf!")
        return True

if __name__ == "__main__":
    asyncio.run(extract_gemini_cookies())
