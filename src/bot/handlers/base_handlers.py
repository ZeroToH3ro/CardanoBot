from telebot import TeleBot
from src.bot.services.dex_service import DexHunterService
from src.bot.services.cardano_service import CardanoService
from src.bot.utils.formatters import FormatUtils

def register_base_handlers(bot: TeleBot):
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

    @bot.message_handler(commands=['tip'])
    def get_chain_tip(message):
        bot.reply_to(message, "Fetching latest block information... 🔍")

        cardano_service = CardanoService()
        result = cardano_service.get_cardano_tip()

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
        try:
            parts = message.text.split()

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

            asset_list = []
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    asset_list.append([parts[i], parts[i + 1]])

            if not asset_list:
                bot.reply_to(message, "❌ No valid asset pairs provided")
                return

            bot.reply_to(message, f"Fetching ADA price and asset information for {len(asset_list)} assets... 💰")

            cardano_service = CardanoService()
            result = cardano_service.get_ada_price(asset_list)

            if isinstance(result, str):
                bot.reply_to(message, f"Error: {result}")
                return

            response_text = "💎 Cardano (ADA) Information:\n\n"

            if "price_data" in result:
                price_data = result["price_data"]
                response_text += f"💰 Price: ${price_data.get('usd', 'N/A')}\n"
                response_text += f"📊 24h Volume: ${price_data.get('usd_24h_vol', 'N/A'):,.2f}\n"
                response_text += f"💹 Market Cap: ${price_data.get('usd_market_cap', 'N/A'):,.2f}\n\n"

            if "asset_info" in result and result["asset_info"]:
                response_text += "🏦 Asset Information:\n"
                for asset in result["asset_info"]:
                    response_text += f"\nPolicy ID: {asset.get('policy_id', 'N/A')}\n"
                    response_text += f"Asset Name: {asset.get('asset_name_ascii', 'N/A')}\n"
                    response_text += f"Fingerprint: {asset.get('fingerprint', 'N/A')}\n"
                    response_text += f"Total Supply: {asset.get('total_supply', 'N/A')}\n"

                    if 'metadata' in asset:
                        response_text += "Metadata:\n"
                        metadata = asset['metadata']
                        if 'name' in metadata:
                            response_text += f"- Name: {metadata['name']}\n"
                        if 'description' in metadata:
                            response_text += f"- Description: {metadata['description']}\n"

                    response_text += "----\n"

            if len(response_text) > 4096:
                for i in range(0, len(response_text), 4096):
                    bot.reply_to(message, response_text[i:i + 4096])
            else:
                bot.reply_to(message, response_text)

        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    @bot.message_handler(commands=['address'])
    def get_address(message):
        try:
            parts = message.text.split()
            if len(parts) != 2:
                bot.reply_to(message, "❌ Invalid format. Use: /address <cardano_address>")
                return

            _, address = parts

            bot.reply_to(message, "Fetching address information... 🔍")

            cardano_service = CardanoService()
            result = cardano_service.get_address_info(address)

            if isinstance(result, str):
                bot.reply_to(message, f"Error: {result}")
                return

            response_text = "📍 Address Information:\n\n"
            response_text += f"Balance: {result['balance'] / 10000:.6f} ADA\n"
            response_text += f"Stake Address: {result['stake_address']}\n"
            response_text += f"Script Address: {'Yes' if result['script_address'] else 'No'}\n"

            if result['tokens']:
                response_text += "\n🎭 Tokens:\n"
                for token in result['tokens'][:5]:
                    response_text += f"- {token['asset_name']}: {token['quantity']}\n"

            bot.reply_to(message, response_text)

        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    @bot.message_handler(commands=['epoch'])
    def get_epoch(message):
        bot.reply_to(message, "Fetching epoch information... ⏳")
        cardano_service = CardanoService()
        result = cardano_service.get_epoch_info()

        if isinstance(result, str):
            bot.reply_to(message, f"Error: {result}")
            return

        response_text = "📊 Epoch Information\n\n"
        response_text += f"🔢 Epoch Number: {result['epoch_no']}\n\n"

        # Time Information
        response_text += "⏰ Time Details\n"
        response_text += f"▪️ Start: {FormatUtils.format_timestamp(result['start_time'])}\n"
        response_text += f"▪️ End: {FormatUtils.format_timestamp(result['end_time'])}\n"
        response_text += f"▪️ First Block: {FormatUtils.format_timestamp(result['first_block_time'])}\n"
        response_text += f"▪️ Last Block: {FormatUtils.format_timestamp(result['last_block_time'])}\n\n"

        # Stake and Rewards
        response_text += "💰 Stake & Rewards\n"
        response_text += f"▪️ Active Stake: {FormatUtils.format_ada(result['active_stake'])} ADA\n"
        response_text += f"▪️ Total Rewards: {FormatUtils.format_ada(result['total_rewards'])} ADA\n"
        response_text += f"▪️ Avg Block Reward: {FormatUtils.format_ada(result['avg_blk_reward'])} ADA\n\n"

        # Block and Transaction Information
        response_text += "📦 Blocks & Transactions\n"
        response_text += f"▪️ Block Count: {result['blk_count']:,}\n"
        response_text += f"▪️ Transaction Count: {result['tx_count']:,}\n"
        response_text += f"▪️ Total Fees: {FormatUtils.format_ada(result['fees'])} ADA\n"
        response_text += f"▪️ Total Output: {FormatUtils.format_ada(result['out_sum'])} ADA\n"

        bot.reply_to(message, response_text)

    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        bot.reply_to(message, "❌ Unknown command. Use /start to see available commands.")
