from src.bot.bot import create_bot

def main():
    bot = create_bot()
    print("Bot started...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()