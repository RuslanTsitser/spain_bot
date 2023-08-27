from telebot import TeleBot
from const.key import TELEGRAM_BOT_TOKEN


def send_message_telegram(message: str, telegram_id: str) -> None:
    bot = TeleBot(TELEGRAM_BOT_TOKEN)
    bot.send_message(telegram_id, message)
    print("send message telegram")
