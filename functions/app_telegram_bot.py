from telebot import TeleBot


def send_message_telegram(message: str) -> None:
    bot = TeleBot("5878623665:AAHSivBGwtr3LA2zehj65WqbKPfs_rT9wnE")
    bot.send_message("747213289", message)
    print("send message telegram")
