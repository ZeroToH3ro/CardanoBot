import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('API_KEY_TELEGRAM')

# API Configuration
DEXHUNTER_API_URL = "https://api-us.dexhunterv3.app"
KOIOS_API_URL = "https://api.koios.rest/api/v1"
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

# Default Headers
DEXHUNTER_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

KOIOS_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json"
}