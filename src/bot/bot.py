from telebot import TeleBot
from config.settings import BOT_TOKEN
from .handlers import base_handlers

def create_bot():
    bot = TeleBot(BOT_TOKEN)

    # Register handlers
    base_handlers.register_base_handlers(bot)

    return bot