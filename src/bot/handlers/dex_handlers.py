from telebot import TeleBot
from src.bot.services.dex_service import DexHunterService

def register_dex_handlers(bot: TeleBot):

    @bot.message_handler(commands=['trending', 'trending_1h', 'trending_24h'])
    def get_trending_pairs(message):
        period = {
            '/trending': '5m',
            '/trending_1h': '1h',
            '/trending_24h': '24h'
        }.get(message.text.split()[0], '5m')

        bot.reply_to(message, "Fetching trending pairs... 🔍")

        dex_service = DexHunterService()
        result = dex_service.get_trending(period)

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

            dex_service = DexHunterService()
            result = dex_service.get_swap_estimate(amount, token_in, token_out)

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

    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        bot.reply_to(message, "❌ Unknown command. Use /start to see available commands.")