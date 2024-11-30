import requests
from config.settings import DEXHUNTER_API_URL, DEXHUNTER_HEADERS

class DexHunterService:
    @staticmethod
    def get_trending(period="5m"):
        """Get trending pairs from DexHunter"""
        url = f"{DEXHUNTER_API_URL}/swap/trending"
        payload = {
            "sort": "VOLUME_AMOUNT",
            "period": period
        }

        try:
            response = requests.post(url, json=payload, headers=DEXHUNTER_HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_swap_estimate(amount_in, token_in, token_out, slippage=5):
        """Get swap estimate from DexHunter"""
        url = f"{DEXHUNTER_API_URL}/swap/estimate"
        payload = {
            "amount_in": float(amount_in),
            "token_in": token_in,
            "token_out": token_out,
            "slippage": slippage,
            "blacklisted_dexes": ["CERRA", "MUESLISWAP", "GENIUS"]
        }

        try:
            response = requests.post(url, json=payload, headers=DEXHUNTER_HEADERS)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"