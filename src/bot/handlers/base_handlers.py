import koios_api
from telebot import TeleBot, types
from src.bot.services.dex_service import DexHunterService
from src.bot.services.cardano_service import CardanoService
from src.bot.services.worker_service import WorkerService
from src.bot.utils.formatters import FormatUtils
from src.bot.utils.mapping_token_name import FormatTokenName


def register_base_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
          # Create inline keyboard markup
        markup = types.InlineKeyboardMarkup(row_width=2)

          # DexHunter buttons
        dex_button = types.InlineKeyboardButton("🔄 DexHunter", callback_data="dex_menu")
        cardano_button = types.InlineKeyboardButton("💎 Cardano", callback_data="cardano_menu")

          # Add buttons to markup
        markup.add(dex_button, cardano_button)

        welcome_text = """
    Welcome to DexHunter & Cardano Bot! 🚀

    Please select a category below to see available commands:
    """
        bot.reply_to(message, welcome_text, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        if call.data == "dex_menu":
            markup = types.InlineKeyboardMarkup(row_width=2)
            trending_button = types.InlineKeyboardButton("📈 Trending", callback_data="trending_options")
            estimate_button = types.InlineKeyboardButton("💱 Estimate", callback_data="estimate_info")
            fear_greed_button = types.InlineKeyboardButton("😨 Fear & Greed", callback_data="fear_greed")
            back_button = types.InlineKeyboardButton("🔙 Back to Main", callback_data="main_menu")

            markup.add(trending_button, estimate_button, fear_greed_button, back_button)

            bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = "🔄 DexHunter Commands:\n\n"
            "• /trending - Get trending pairs (5m)\n"
            "• /trending_1h - Get trending pairs (1h)\n"
            "• /trending_24h - Get trending pairs (24h)\n"
            "• /estimate <amount> <token_in> <token_out> - Get swap estimate\n"
            "• /feargreed - Get Fear & Greed Index",
            reply_markup = markup
            )
        elif call.data == "cardano_menu":
            markup = types.InlineKeyboardMarkup(row_width=2)
            tip_button = types.InlineKeyboardButton("🎯 Tip", callback_data="tip_info")
            price_button = types.InlineKeyboardButton("💰 ADA Price", callback_data="price_info")
            epoch_button = types.InlineKeyboardButton("⏳ Epoch", callback_data="epoch_info")
            address_button = types.InlineKeyboardButton("📍 Address", callback_data="address_info")
            back_button = types.InlineKeyboardButton("🔙 Back to Main", callback_data="main_menu")

            markup.add(tip_button, price_button, epoch_button, address_button, back_button)

            bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = "💎 Cardano Commands:\n\n"
            "• /tip - Get latest block information\n"
            "• /adaprice - Get current ADA price\n"
            "• /epoch - Get current epoch information\n"
            "• /address <address> - Get address information",
            reply_markup = markup
            )
        elif call.data == "main_menu":
            markup = types.InlineKeyboardMarkup(row_width=2)
            dex_button = types.InlineKeyboardButton("🔄 DexHunter", callback_data="dex_menu")
            cardano_button = types.InlineKeyboardButton("💎 Cardano", callback_data="cardano_menu")
            markup.add(dex_button, cardano_button)

            bot.edit_message_text(
            chat_id = call.message.chat.id,
            message_id = call.message.message_id,
            text = "Welcome to DexHunter & Cardano Bot! 🚀\n\nPlease select a category below to see available commands:",
            reply_markup = markup
            )
          # Handle specific command information
        elif call.data in ["trending_options", "estimate_info", "fear_greed", "tip_info",
        "price_info", "epoch_info", "address_info"]:
            command_info = {
            "trending_options": "Use /trending, /trending_1h, or /trending_24h to get trending pairs",
            "estimate_info": "Use /estimate <amount> <token_in> <token_out> to get swap estimate",
            "fear_greed": "Use /feargreed to get the current Fear & Greed Index",
            "tip_info": "Use /tip to get the latest block information",
            "price_info": "Use /adaprice to get current ADA price",
            "epoch_info": "Use /epoch to get current epoch information",
            "address_info": "Use /address <address> to get address information"
            }

        markup = types.InlineKeyboardMarkup()
        back_button = types.InlineKeyboardButton("🔙 Back",
        callback_data = "dex_menu" if call.data in ["trending_options", "estimate_info", "fear_greed"]
         else "cardano_menu"
        )
        markup.add(back_button)

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = command_info[call.data],
        reply_markup = markup
        )

    # Dex Service

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
        tokens_mapping = FormatTokenName.load_token_name()

        if isinstance(result, str):
            bot.reply_to(message, f"❌ Error fetching trending pairs: {result}")
            return

        response_text = f"🔥 <b>TRENDING PAIRS ({period.upper()})</b> 🔥\n\n"
        pairs = result[:10] if len(result) > 10 else result

        for idx, pair in enumerate(pairs, 1):
            token_id = pair['token_id']
            token_name = tokens_mapping.get(token_id, "Unknown Token")
            current_volume = pair['current_period_volume']
            volume_change = pair['volume_change_percentage']
            price_change = pair['price_change_percentage']
            current_price = pair['current_period_closing_price']

            volume_formatted = f"{current_volume:,.2f}"
            price_formatted = f"{current_price:.8f}" if current_price < 0.01 else f"{current_price:.4f}"

            # Add emoji based on price change
            price_emoji = "🟢" if price_change > 0 else "🔴" if price_change < 0 else "⚪️"
            volume_emoji = "📈" if volume_change > 0 else "📉" if volume_change < 0 else "➖"

            response_text += f"#{idx} <b>{token_name}</b> - {token_id}\n"
            response_text += f"├ 💰 Price: ${price_formatted}\n"
            response_text += f"├ {price_emoji} Price Change: {price_change:+,.2f}%\n"
            response_text += f"├ 💎 Volume: ${volume_formatted}\n"
            response_text += f"├ {volume_emoji} Vol Change: {volume_change:+,.2f}%\n"
            response_text += f"└ 🔄 Trades: {pair['amount_buys']}↗️ | {pair['amount_sales']}↘️\n\n"

        if not pairs:
            response_text += "❌ No trending pairs found for this period.\n"

        # Add footer with channel promotion
        response_text += "━━━━━━━━━━━━━━━━━━━━━\n"
        response_text += "🔥 <b>Want Fear and Greed updates?</b>\n"
        response_text += "📢 Join @cardano_hunter now!\n"
        response_text += "━━━━━━━━━━━━━━━━━━━━━"

        if len(response_text) > 4096:
            chunks = [response_text[i:i + 4096] for i in range(0, len(response_text), 4096)]
            for i, chunk in enumerate(chunks):
                # Add footer only to the last chunk
                if i == len(chunks) - 1 and not chunk.endswith("Join @cardano_hunter now!"):
                    chunk += "\n\n📢 Join @cardano_hunter now!"
                bot.reply_to(message, chunk, parse_mode='HTML')
        else:
            bot.reply_to(message, response_text, parse_mode='HTML')

    @bot.message_handler(commands=['estimate'])
    def get_estimate(message):
        global amount, token_in, token_out
        try:
            dex_service = DexHunterService()
            parts = message.text.split()
            if len(parts) == 3:
                __, amount, token = parts
                try:
                    result_in = dex_service.get_swap_estimate(amount, token_in=token, token_out="", slippage=5)
                    if not result_in or isinstance(result_in, str):
                        result_out = dex_service.get_swap_estimate(amount, token_in="", token_out=token, slippage=5)
                        if isinstance(result_out, str) or not result_out:
                            bot.reply_to(message, f"Error calculating swap estimate: {result_in}")
                            return
                        token_in = ""
                        token_out = token
                    else:
                        token_in = token
                        token_out = ""
                except Exception as e:
                    bot.reply_to(message, f"Error fetching estimated swap estimate: {e}")
                    return

            bot.reply_to(message, "Calculating swap estimate... 🔄")
            result = dex_service.get_swap_estimate(amount, token_in, token_out)
            if isinstance(result, str):
                bot.reply_to(message, f"Error getting estimate: {result}")
                return

            # Format response based on the new JSON structure
            response_text = "💱 Swap Estimate:\n\n"

              # Input amount
            response_text += f"Input Amount: {amount}\n"

              # Output amount
            total_output = result.get('total_output', 'N/A')
            response_text += f"Output Amount: {total_output}\n"

              # Price details
            net_price = result.get('net_price', 'N/A')
            net_price_reverse = result.get('net_price_reverse', 'N/A')
            response_text += f"Price: 1 Token = {net_price} / {net_price_reverse}\n"

              # Fee details
            total_fee = result.get('total_fee', 0)
            batcher_fee = result.get('batcher_fee', 0)
            partner_fee = result.get('partner_fee', 0)
            response_text += f"Fees:\n"
            response_text += f"- Total Fee: {total_fee}\n"
            response_text += f"- Batcher Fee: {batcher_fee}\n"
            response_text += f"- Partner Fee: {partner_fee}\n"

              # Split details (if available)
            splits = result.get('splits', [])
            if splits:
                split = splits[0]  # Get first split
            response_text += f"\nRoute Details:\n"
            response_text += f"- DEX: {split.get('dex', 'N/A')}\n"
            response_text += f"- Price Impact: {split.get('price_impact', 'N/A') * 100:.4f}%\n"
            response_text += f"- Pool Fee: {split.get('pool_fee', 'N/A') * 100:.2f}%\n"

              # Output with/without slippage
            output_with_slippage = split.get('expected_output', 'N/A')
            output_without_slippage = split.get('expected_output_without_slippage', 'N/A')
            response_text += f"\nOutput Details:\n"
            response_text += f"- With Slippage: {output_with_slippage}\n"
            response_text += f"- Without Slippage: {output_without_slippage}\n"

            bot.reply_to(message, response_text)
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")

    @bot.message_handler(commands=['feargreed'])
    def handle_fear_greed(message):
        """Handle manual fear and greed index requests"""

        bot.reply_to(message, "Fetching Fear & Greed Index... 🔍")

        dex_service = DexHunterService()
        result = dex_service.get_fear_greed()

        if isinstance(result, str) and result.startswith("Error"):
            bot.reply_to(message, f"Error fetching Fear & Greed Index: {result}")
            return

        worker = WorkerService(bot)
        formatted_message = worker._format_fear_greed_message(result)
        bot.reply_to(message, formatted_message, parse_mode='HTML')


    # Cardano Handler

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

            response_text = "📍 *Address Information*\n\n"
            response_text += f"💰 *Balance:* `{FormatUtils.format_ada(result['balance'])} ADA`\n"
            stake_address = result['stake_address'] if result['stake_address'] else 'Not delegated'
            response_text += f"🎯 *Stake Address:* `{stake_address}`\n"
            response_text += f"📜 *Script Address:* `{'Yes' if result['script_address'] else 'No'}`\n"

            # UTXO Information
            if 'utxo_set' in result and result['utxo_set']:
                response_text += "\n💎 *UTXO Information:*\n"
                for utxo in result['utxo_set'][:3]:  # Show first 3 UTXOs
                    response_text += f"\n▪️ *UTXO:*\n"
                    response_text += f"  TX Hash: `{utxo['tx_hash']}`\n"
                    response_text += f"  Value: `{FormatUtils.format_ada(utxo['value'])} ADA`\n"

                    if 'asset_list' in utxo and utxo['asset_list']:
                        response_text += "  *Assets:*\n"
                        for asset in utxo['asset_list']:
                            try:
                                # Try to decode asset name from hex
                                asset_name = bytes.fromhex(asset['asset_name']).decode('utf-8')
                            except:
                                asset_name = asset['asset_name']

                            response_text += f"    • {asset_name}: `{asset['quantity']}`\n"
                            response_text += f"      Policy: `{asset['policy_id']}`\n"

                if len(result['utxo_set']) > 3:
                    response_text += f"\n_...and {len(result['utxo_set']) - 3} more UTXOs_"

            bot.reply_to(message, response_text, parse_mode='Markdown')

        except Exception as e:
            print(f"Error details: {str(e)}")  # For debugging
            bot.reply_to(message, f"❌ Error: {str(e)}")

    @bot.message_handler(commands=['epoch'])
    def get_epoch(message):
        # Check if echo_no is provided
        command_parts = message.text.split()
        if len(command_parts) > 1:
            epoch_no = int(command_parts[1])
        else:
            tip_info = CardanoService.get_cardano_tip()
            if not tip_info or not isinstance(tip_info, dict):
                bot.reply_to(message, "Error: Could not fetch current epoch")
                return

            epoch_no = tip_info['epoch_no']

        bot.reply_to(message, "Fetching epoch information... ⏳")
        cardano_service = CardanoService()
        result = cardano_service.get_epoch_info(epoch_no)

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
