from src.bot.bot import create_bot
from src.bot.services.worker_service import WorkerService


def main():
    bot = create_bot()

    # WorkerServcie
    worker = WorkerService(bot)
    worker.start()

    print("Bot started...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()