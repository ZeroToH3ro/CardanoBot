import telebot
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('API_KEY_TELEGRAM')
bot = telebot.TeleBot(BOT_TOKEN)

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

# Command handler for /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
Welcome to DexHunter Bot! 🚀

Available commands:
/trending - Get trending pairs (default 5m)
/trending_1h - Get trending pairs (1h)
/trending_24h - Get trending pairs (24h)
/estimate <amount> <token_in> <token_out> - Get swap estimate

Example for estimate:
/estimate 100 TOKEN_IN_ID TOKEN_OUT_ID
"""
    bot.reply_to(message, welcome_text)

# Command handler for /trending with different time periods
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

    # Format the trending pairs response
    response_text = f"🔥 Trending Pairs ({period}):\n\n"

    # Take only first 10 pairs if there are more
    pairs = result[:10] if len(result) > 10 else result

    for pair in pairs:
        token_id = pair['token_id']
        # Truncate token_id for display
        short_token = token_id[:10] + "..." + token_id[-4:] if len(token_id) > 14 else token_id

        current_volume = pair['current_period_volume']
        volume_change = pair['volume_change_percentage']
        price_change = pair['price_change_percentage']
        current_price = pair['current_period_closing_price']

        # Format numbers for better readability
        volume_formatted = f"{current_volume:,.2f}"
        price_formatted = f"{current_price:.8f}" if current_price < 0.01 else f"{current_price:.4f}"

        response_text += f"📊 Token: {short_token}\n"
        response_text += f"💰 Current Price: {price_formatted}\n"
        response_text += f"📈 Volume: ${volume_formatted}\n"
        response_text += f"📊 Volume Change: {volume_change:,.2f}%\n"
        response_text += f"💹 Price Change: {price_change:,.2f}%\n"
        response_text += f"🔄 Trades: {pair['amount_buys']} buys, {pair['amount_sales']} sales\n\n"
        response_text += "------------------------\n\n"

    if not pairs:
        response_text += "No trending pairs found for this period."

    # Send response in chunks if it's too long
    if len(response_text) > 4096:
        for i in range(0, len(response_text), 4096):
            bot.reply_to(message, response_text[i:i+4096])
    else:
        bot.reply_to(message, response_text)

# Command handler for /estimate
@bot.message_handler(commands=['estimate'])
def get_estimate(message):
    try:
        # Split the message into parts
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

        # Format the estimate response
        response_text = "💱 Swap Estimate:\n\n"
        response_text += f"Input: {amount} {result.get('token_in_symbol', 'N/A')}\n"
        response_text += f"Output: {result.get('amount_out', 'N/A')} {result.get('token_out_symbol', 'N/A')}\n"
        response_text += f"Price Impact: {result.get('price_impact', 'N/A')}%\n"
        response_text += f"Route: {result.get('route_summary', 'N/A')}"

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