from telebot import TeleBot
from telebot.types import Update
from const.key import TELEGRAM_BOT_TOKEN


def send_message_telegram(message: str, telegram_id: str) -> None:
    bot = TeleBot(TELEGRAM_BOT_TOKEN)
    bot.send_message(telegram_id, message)
    print("send message telegram")


def handle_request(json_string) -> None:
    update = Update.de_json(json_string)
    if (update is not None):
        user_id = update.message.chat.id
        message = update.message.text
        bot = TeleBot(TELEGRAM_BOT_TOKEN)
        bot.send_message(user_id, message)
