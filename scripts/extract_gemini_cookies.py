import browser_cookie3
import configparser
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.conf')

# Try to extract Gemini cookies from Chrome
cookies = browser_cookie3.chrome(domain_name="google.com")
psid = None
psidts = None
for cookie in cookies:
    if cookie.name == "__Secure-1PSID":
        psid = cookie.value
    if cookie.name == "__Secure-1PSIDTS":
        psidts = cookie.value

if not psid or not psidts:
    print("Could not find Gemini cookies. Make sure you are logged in to Gemini in Chrome.")
    exit(1)

# Update config.conf
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding='utf-8')
if 'Cookies' not in config:
    config['Cookies'] = {}
config['Cookies']['gemini_cookie_1PSID'] = psid
config['Cookies']['gemini_cookie_1PSIDTS'] = psidts
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    config.write(f)
print("Gemini cookies updated in config.conf!")
