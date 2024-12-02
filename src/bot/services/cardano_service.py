import requests
import koios_api
from config.settings import KOIOS_API_URL, KOIOS_HEADERS, COINGECKO_API_URL

class CardanoService:
    @staticmethod
    def get_cardano_tip():
        """Get the latest block information"""
        try:
            tip = koios_api.get_tip()
            return tip[0] if tip else None
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_ada_price(asset_list=None):
        """Get both ADA price from CoinGecko and asset information from Koios"""
        if asset_list is None:
            asset_list = [["750900e4999ebe0d58f19b634768ba25e525aaf12403bfe8fe130501", "424f4f4b"]]

        try:
            # Get asset info from Koios
            koios_response = requests.post(
                f"{KOIOS_API_URL}/asset_info",
                json={"_asset_list": asset_list},
                headers=KOIOS_HEADERS
            )
            koios_response.raise_for_status()
            asset_info = koios_response.json()

            # Get price info from CoinGecko
            price_response = requests.get(
                f"{COINGECKO_API_URL}/simple/price",
                params={
                    "ids": "cardano",
                    "vs_currencies": "usd",
                    "include_24hr_vol": "true",
                    "include_market_cap": "true"
                }
            )
            price_response.raise_for_status()
            price_data = price_response.json()

            return {
                "asset_info": asset_info,
                "price_data": price_data.get("cardano", {})
            }
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_epoch_info(epoch_no=None):
        try:
            epoch_info = koios_api.get_epoch_info(int(epoch_no))
            if not epoch_info or not isinstance(epoch_info, list):
               return "Error: Invalid response from API"

            return epoch_info[0] if epoch_info else None
        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    def get_address_info(address):
        """Get address information"""
        try:
            address_info = koios_api.get_address_info([address])
            return address_info[0] if address_info else None
        except Exception as e:
            return f"Error: {str(e)}"

