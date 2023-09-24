from telebot import TeleBot
from telebot.types import Update, MessageEntity
from const.key import APPOINTMENT_FAMILY_URL, APPOINTMENT_URL, TELEGRAM_BOT_TOKEN
from app_firestore import set_is_sent
from get_main_data import get_main_data


def send_message_telegram(message: str, telegram_id: str) -> None:
    bot = TeleBot(TELEGRAM_BOT_TOKEN)
    bot.send_message(telegram_id, message)
    print("send message telegram")


def handle_request(json_string) -> None:
    update = Update.de_json(json_string)
    if (update is not None):
        entities = update.message.entities
        if isinstance(entities, list):
            if (any(entity.type == "bot_command" for entity in entities)):
                # handle only first command and value after
                command = entities[0]
                if (command.offset == 0):
                    telegram_id = str(update.message.chat.id)
                    full_message = update.message.text
                    handle_command(telegram_id, command, full_message)
                    return

        user_id = update.message.chat.id
        message = update.message.text
        bot = TeleBot(TELEGRAM_BOT_TOKEN)
        bot.send_message(user_id, message)


def handle_command(telegram_id: str, entity: MessageEntity, full_message: str) -> None:
    bot = TeleBot(TELEGRAM_BOT_TOKEN)
    command = full_message[entity.offset:entity.length]
    message_after_command = full_message[entity.length:]

    website_url = APPOINTMENT_FAMILY_URL if command == "/family" else APPOINTMENT_URL if command == "/single" else None

    if (website_url is None):
        bot.send_message(telegram_id, "Unknown command")
        return

    parts = message_after_command.split(" ")
    php_session_id = parts[1] if len(
        parts) > 1 else parts[0] if len(parts) > 0 else None

    if (php_session_id is None):
        bot.send_message(telegram_id, "No php_session_id")
        return

    main_data = get_main_data(
        request_php_token=php_session_id,
        url=website_url,
        telegram_id=telegram_id,
    )

    if (main_data is None):
        bot.send_message(telegram_id, "No data")
    elif (main_data.firestore_data.is_expired and main_data.firestore_data.is_sent == False):
        set_is_sent(telegram_id, True)
        bot.send_message(
            telegram_id,
            'Token expired' + '\n' +
            'php_session_id: ' + main_data.new_php_session_id)
    elif (main_data.available_dates != []):
        bot.send_message(
            telegram_id,
            'php_session_id: ' +
            main_data.new_php_session_id + '\n' + 'available_dates: ' +
            str(main_data.available_dates) + '\n' +
            'url: ' + main_data.firestore_data.url
        )
    else:
        bot.send_message(telegram_id, "No available dates")


formatted_json_text = {
    "update_id": 236975568,
    "message": {
        "message_id": 160,
        "from": {
            "id": 747213289,
            "is_bot": False,
            "first_name": "Ruslan",
            "last_name": "Tsitser",
            "username": "RuslanTsitser",
            "language_code": "en"
        },
        "chat": {
            "id": 747213289,
            "first_name": "Ruslan",
            "last_name": "Tsitser",
            "username": "RuslanTsitser",
            "type": "private"
        },
        "date": 1695559797,
        "text": "hello"
    }
}


# formatted json
formatted_json_command = {
    "update_id": 236975570,
    "message": {
        "message_id": 164,
        "from": {
            "id": 747213289,
            "is_bot": False,
            "first_name": "Ruslan",
            "last_name": "Tsitser",
            "username": "RuslanTsitser",
            "language_code": "en"
        },
        "chat": {
            "id": 747213289,
            "first_name": "Ruslan",
            "last_name": "Tsitser",
            "username": "RuslanTsitser",
            "type": "private"
        },
        "date": 1695560005,
        "text": "/command",
        "entities": [
                {
                    "offset": 0,
                    "length": 8,
                    "type": "bot_command"
                }
        ]
    }
}
