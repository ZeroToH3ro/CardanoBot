# services/worker_service.py
import threading
import time
import logging
from datetime import datetime

from config.settings import CHANNEL_ID
from src.bot.services.dex_service import DexHunterService

class WorkerService:
    def __init__(self, bot):
        self.bot = bot
        self.dex_service = DexHunterService()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_running = False
        self.last_value = None
        self.channel_id = CHANNEL_ID

    def start(self):
        """Start the worker service"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._run_fear_greed_worker)
            thread.daemon = True
            thread.start()
            self.logger.info("Fear and Greed worker service started")

    def stop(self):
        """Stop the worker service"""
        self.is_running = False
        self.logger.info("Fear and Greed worker service stopped")

    def _run_fear_greed_worker(self):
        while self.is_running:
            try:
                self._process_fear_greed_data()
                time.sleep(60)  # Wait for 1 minute
            except Exception as e:
                self.logger.error(f"Error in fear and greed worker: {str(e)}")
                time.sleep(10)  # Wait 10 seconds before retrying if there's an error

    def _process_fear_greed_data(self):
        """Process fear and greed data and send updates if necessary"""
        data = self.dex_service.get_fear_greed()

        if isinstance(data, str) and data.startswith("Error"):
            self.logger.error(f"Failed to fetch fear and greed data: {data}")
            return

        try:
            # Since data is a list, let's process the most recent data (first item)
            latest_data = data[0] if data else None
            if not latest_data:
                self.logger.error("No fear and greed data available")
                return

            message = self._format_fear_greed_message(latest_data)
            print(message)
            # Calculate current value based on buy/sell volumes
            buy_volume = latest_data.get('global_buy_volume', 0)
            sell_volume = latest_data.get('global_sell_volume', 0)
            total_volume = buy_volume + sell_volume

            if total_volume > 0:
                # Calculate ratio between 0 and 100
                current_value = int((buy_volume / total_volume) * 100)
            else:
                current_value = 50  # Default neutral value

            if current_value != self.last_value:
                self.bot.send_message(self.channel_id, message, parse_mode='HTML')
                self.last_value = current_value
                self.logger.info(f"Fear and Greed update sent: {current_value}")

        except Exception as e:
            self.logger.error(f"Error processing fear and greed data: {str(e)}")

    def _format_fear_greed_message(self, data):
        """Format fear and greed message"""
        # Calculate buy/sell ratio
        buy_volume = data.get('global_buy_volume', 0)
        sell_volume = data.get('global_sell_volume', 0)
        total_volume = buy_volume + sell_volume

        if total_volume > 0:
            buy_ratio = (buy_volume / total_volume) * 100
            value = int(buy_ratio)
        else:
            value = 50  # Default neutral value

        # Determine classification based on buy ratio
        if value >= 75:
            classification = 'Extreme Greed'
        elif value >= 60:
            classification = 'Greed'
        elif value >= 40:
            classification = 'Neutral'
        elif value >= 25:
            classification = 'Fear'
        else:
            classification = 'Extreme Fear'

        # Format volumes in billions or millions
        def format_volume(vol):
            if vol >= 1_000_000_000:
                return f"{vol / 1_000_000_000:.2f}B"
            return f"{vol / 1_000_000:.2f}M"

        buy_vol_formatted = format_volume(buy_volume)
        sell_vol_formatted = format_volume(sell_volume)
        total_vol_formatted = format_volume(total_volume)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Define emoji based on classification
        emoji_map = {
            'Extreme Fear': '😱',
            'Fear': '😨',
            'Neutral': '😐',
            'Greed': '🤑',
            'Extreme Greed': '🤯'
        }
        emoji = emoji_map.get(classification, '❓')

        # Create progress bar
        progress_length = 20
        filled_length = int(value * progress_length / 100)
        progress_bar = '█' * filled_length + '▒' * (progress_length - filled_length)

        message = (
            f"<b>Market Sentiment Index</b> {emoji}\n\n"
            f"Value: {value}\n"
            f"Classification: {classification}\n"
            f"[{progress_bar}] {value}%\n\n"
            f"📊 Trading Volume:\n"
            f"Buy Volume: {buy_vol_formatted}\n"
            f"Sell Volume: {sell_vol_formatted}\n"
            f"Total Volume: {total_vol_formatted}\n\n"
            f"📈 Trades Count:\n"
            f"Buys: {data.get('global_buy_count', 0):,}\n"
            f"Sells: {data.get('global_sell_count', 0):,}\n"
            f"Total: {data.get('count', 0):,}\n\n"
            f"🕒 {timestamp}"
        )
        return message