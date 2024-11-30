from telebot import TeleBot
from config.settings import BOT_TOKEN
from .handlers import base_handlers, dex_handlers, cardano_handlers

def create_bot():
    bot = TeleBot(BOT_TOKEN)

    # Register handlers
    base_handlers.register_base_handlers(bot)
    # dex_handlers.register_dex_handlers(bot)
    # cardano_handlers.register_cardano_handlers(bot)

    return bot