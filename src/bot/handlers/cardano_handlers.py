from telebot import TeleBot
from src.bot.services.cardano_service import CardanoService

def register_cardano_handlers(bot: TeleBot):

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

    @bot.message_handler(func=lambda message: True)
    def echo_all(message):
        bot.reply_to(message, "❌ Unknown command. Use /start to see available commands.")