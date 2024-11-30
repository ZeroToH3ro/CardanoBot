import telebot
import requests
from dotenv import load_dotenv
import os
import koios_api

load_dotenv()

BOT_TOKEN = os.getenv('API_KEY_TELEGRAM')
bot = telebot.TeleBot(BOT_TOKEN)


# DexHunter Functions
def get_trending(period="5m"):
    """Get trending pairs from DexHunter"""
    url = "https://api-us.dexhunterv3.app/swap/trending"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    payload = {
        "sort": "VOLUME_AMOUNT",
        "period": period
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


def get_swap_estimate(amount_in, token_in, token_out, slippage=5):
    """Get swap estimate from DexHunter"""
    url = "https://api-us.dexhunterv3.app/swap/estimate"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }

    payload = {
        "amount_in": float(amount_in),
        "token_in": token_in,
        "token_out": token_out,
        "slippage": slippage,
        "blacklisted_dexes": ["CERRA", "MUESLISWAP", "GENIUS"]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"


# koios_api API Functions
def get_cardano_tip():
    """Get the latest block information"""
    try:
        tip = koios_api.get_tip()
        return tip[0] if tip else None
    except Exception as e:
        return f"Error: {str(e)}"


def get_ada_price(asset_list=None):
    """Get both ADA price from CoinGecko and asset information from Koios"""
    # Koios API call
    koios_url = "https://api.koios.rest/api/v1/asset_info"
    koios_headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }

    # Use provided asset_list or default if none provided
    if asset_list is None:
        koios_payload = {
            "_asset_list": [
                ["750900e4999ebe0d58f19b634768ba25e525aaf12403bfe8fe130501", "424f4f4b"]
            ]
        }
    else:
        koios_payload = {
            "_asset_list": asset_list
        }

    # CoinGecko API call for ADA price
    coingecko_url = "https://api.coingecko.com/api/v3/simple/price"
    coingecko_params = {
        "ids": "cardano",
        "vs_currencies": "usd",
        "include_24hr_vol": "true",
        "include_market_cap": "true"
    }

    try:
        # Get asset info from Koios
        koios_response = requests.post(koios_url, json=koios_payload, headers=koios_headers)
        koios_response.raise_for_status()
        asset_info = koios_response.json()

        # Get price info from CoinGecko
        price_response = requests.get(coingecko_url, params=coingecko_params)
        price_response.raise_for_status()
        price_data = price_response.json()

        return {
            "asset_info": asset_info,
            "price_data": price_data.get("cardano", {})
        }
    except Exception as e:
        return f"Error: {str(e)}"


@bot.message_handler(commands=['adaprice'])
def get_price(message):
    try:
        # Split the message into parts
        parts = message.text.split()

        # Show help if no parameters
        if len(parts) == 1:
            help_text = """
❌ Invalid format. Use: 
/adaprice <policy_id> <asset_name> [policy_id2 asset_name2...]

Example:
/adaprice 750900e4999ebe0d58f19b634768ba25e525aaf12403bfe8fe130501 424f4f4b
/adaprice policy_id1 asset_name1 policy_id2 asset_name2

Note: You can query multiple assets at once by providing policy_id and asset_name pairs
"""
            bot.reply_to(message, help_text)
            return

        # Parse asset list from message
        asset_list = []
        # Skip the command part and process pairs of policy_id and asset_name
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                asset_list.append([parts[i], parts[i + 1]])

        if not asset_list:
            bot.reply_to(message, "❌ No valid asset pairs provided")
            return

        bot.reply_to(message, f"Fetching ADA price and asset information for {len(asset_list)} assets... 💰")
        result = get_ada_price(asset_list)

        if isinstance(result, str):
            bot.reply_to(message, f"Error: {result}")
            return

        response_text = "💎 Cardano (ADA) Information:\n\n"

        # Add price information
        if "price_data" in result:
            price_data = result["price_data"]
            response_text += f"💰 Price: ${price_data.get('usd', 'N/A')}\n"
            response_text += f"📊 24h Volume: ${price_data.get('usd_24h_vol', 'N/A'):,.2f}\n"
            response_text += f"💹 Market Cap: ${price_data.get('usd_market_cap', 'N/A'):,.2f}\n\n"

        # Add asset information
        if "asset_info" in result and result["asset_info"]:
            response_text += "🏦 Asset Information:\n"
            for asset in result["asset_info"]:
                response_text += f"\nPolicy ID: {asset.get('policy_id', 'N/A')}\n"
                response_text += f"Asset Name: {asset.get('asset_name_ascii', 'N/A')}\n"
                response_text += f"Fingerprint: {asset.get('fingerprint', 'N/A')}\n"
                response_text += f"Total Supply: {asset.get('total_supply', 'N/A')}\n"

                # Add metadata if available
                if 'metadata' in asset:
                    response_text += "Metadata:\n"
                    metadata = asset['metadata']
                    if 'name' in metadata:
                        response_text += f"- Name: {metadata['name']}\n"
                    if 'description' in metadata:
                        response_text += f"- Description: {metadata['description']}\n"

                response_text += "-------------------\n"

        # Send response in chunks if it's too long
        if len(response_text) > 4096:
            for i in range(0, len(response_text), 4096):
                bot.reply_to(message, response_text[i:i + 4096])
        else:
            bot.reply_to(message, response_text)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


def get_epoch_info():
    """Get current epoch information"""
    try:
        epoch_info = koios_api.get_epoch_info()
        return epoch_info[0] if epoch_info else None
    except Exception as e:
        return f"Error: {str(e)}"


def get_address_info(address):
    """Get address information"""
    try:
        address_info = koios_api.get_address_info(address)
        return address_info[0] if address_info else None
    except Exception as e:
        return f"Error: {str(e)}"


# Command Handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
Welcome to DexHunter & Cardano Bot! 🚀

DexHunter Commands:
/trending - Get trending pairs (default 5m)
/trending_1h - Get trending pairs (1h)
/trending_24h - Get trending pairs (24h)
/estimate <amount> <token_in> <token_out> - Get swap estimate

Cardano Commands:
/tip - Get latest block information
/adaprice - Get current ADA price
/epoch - Get current epoch information
/address <address> - Get address information

Example for estimate:
/estimate 100 TOKEN_IN_ID TOKEN_OUT_ID
"""
    bot.reply_to(message, welcome_text)


@bot.message_handler(commands=['trending', 'trending_1h', 'trending_24h'])
def get_trending_pairs(message):
    period = {
        '/trending': '5m',
        '/trending_1h': '1h',
        '/trending_24h': '24h'
    }.get(message.text.split()[0], '5m')

    bot.reply_to(message, "Fetching trending pairs... 🔍")

    result = get_trending(period)
    if isinstance(result, str):
        bot.reply_to(message, f"Error fetching trending pairs: {result}")
        return

    response_text = f"🔥 Trending Pairs ({period}):\n\n"
    pairs = result[:10] if len(result) > 10 else result

    for pair in pairs:
        token_id = pair['token_id']
        short_token = token_id[:10] + "..." + token_id[-4:] if len(token_id) > 14 else token_id

        current_volume = pair['current_period_volume']
        volume_change = pair['volume_change_percentage']
        price_change = pair['price_change_percentage']
        current_price = pair['current_period_closing_price']

        volume_formatted = f"{current_volume:,.2f}"
        price_formatted = f"{current_price:.8f}" if current_price < 0.01 else f"{current_price:.4f}"

        response_text += f"📊 Token: {short_token}\n"
        response_text += f"💰 Current Price: {price_formatted}\n"
        response_text += f"📈 Volume: ${volume_formatted}\n"
        response_text += f"📊 Volume Change: {volume_change:,.2f}%\n"
        response_text += f"💹 Price Change: {price_change:,.2f}%\n"
        response_text += f"🔄 Trades: {pair['amount_buys']} buys, {pair['amount_sales']} sales\n\n"
        response_text += "----\n\n"

    if not pairs:
        response_text += "No trending pairs found for this period."

    if len(response_text) > 4096:
        for i in range(0, len(response_text), 4096):
            bot.reply_to(message, response_text[i:i + 4096])
    else:
        bot.reply_to(message, response_text)


@bot.message_handler(commands=['estimate'])
def get_estimate(message):
    try:
        parts = message.text.split()
        if len(parts) != 4:
            bot.reply_to(message, "❌ Invalid format. Use: /estimate <amount> <token_in> <token_out>")
            return

        _, amount, token_in, token_out = parts

        bot.reply_to(message, "Calculating swap estimate... 🔄")

        result = get_swap_estimate(amount, token_in, token_out)
        if isinstance(result, str):
            bot.reply_to(message, f"Error getting estimate: {result}")
            return

        response_text = "💱 Swap Estimate:\n\n"
        response_text += f"Input: {amount} {result.get('token_in_symbol', 'N/A')}\n"
        response_text += f"Output: {result.get('amount_out', 'N/A')} {result.get('token_out_symbol', 'N/A')}\n"
        response_text += f"Price Impact: {result.get('price_impact', 'N/A')}%\n"
        response_text += f"Route: {result.get('route_summary', 'N/A')}"

        bot.reply_to(message, response_text)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


@bot.message_handler(commands=['tip'])
def get_chain_tip(message):
    bot.reply_to(message, "Fetching latest block information... 🔍")
    result = get_cardano_tip()

    if isinstance(result, str):
        bot.reply_to(message, f"Error: {result}")
        return

    response_text = "🎯 Latest Block Information:\n\n"
    response_text += f"Block: {result['block_no']}\n"
    response_text += f"Hash: {result['hash']}\n"
    response_text += f"Slot: {result['abs_slot']}\n"
    response_text += f"Epoch: {result['epoch_no']}"

    bot.reply_to(message, response_text)


@bot.message_handler(commands=['adaprice'])
def get_price(message):
    bot.reply_to(message, "Fetching ADA price... 💰")
    result = get_ada_price()

    if isinstance(result, str):
        bot.reply_to(message, f"Error: {result}")
        return

    response_text = "💎 ADA Price Information:\n\n"
    response_text += f"Price (USD): ${result['price_usd']:.4f}\n"
    response_text += f"24h Volume: ${result['volume_24h']:,.2f}\n"
    response_text += f"Market Cap: ${result['market_cap']:,.2f}"

    bot.reply_to(message, response_text)


@bot.message_handler(commands=['epoch'])
def get_epoch(message):
    bot.reply_to(message, "Fetching epoch information... ⏳")
    result = get_epoch_info()

    if isinstance(result, str):
        bot.reply_to(message, f"Error: {result}")
        return

    response_text = "📊 Epoch Information:\n\n"
    response_text += f"Epoch: {result['epoch_no']}\n"
    response_text += f"Start Time: {result['start_time']}\n"
    response_text += f"End Time: {result['end_time']}\n"
    response_text += f"Progress: {result['progress']}%\n"
    response_text += f"Active Stake: {result['active_stake'] / 1000000:.2f} ADA"

    bot.reply_to(message, response_text)


@bot.message_handler(commands=['address'])
def get_address(message):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.reply_to(message, "❌ Invalid format. Use: /address <cardano_address>")
            return

        _, address = parts

        bot.reply_to(message, "Fetching address information... 🔍")
        result = get_address_info(address)

        if isinstance(result, str):
            bot.reply_to(message, f"Error: {result}")
            return

        response_text = "📍 Address Information:\n\n"
        response_text += f"Balance: {result['balance'] / 1000000:.6f} ADA\n"
        response_text += f"Stake Address: {result['stake_address']}\n"
        response_text += f"Script Address: {'Yes' if result['script_address'] else 'No'}\n"

        if result['tokens']:
            response_text += "\n🎭 Tokens:\n"
            for token in result['tokens'][:5]:
                response_text += f"- {token['asset_name']}: {token['quantity']}\n"

        bot.reply_to(message, response_text)

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")


# Error handler
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "❌ Unknown command. Use /start to see available commands.")


# Start the bot
def main():
    print("Bot started...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()
