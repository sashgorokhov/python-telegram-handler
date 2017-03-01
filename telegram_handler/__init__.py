from telegram_handler.formatters import *
from telegram_handler.handlers import *


def main():  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser('Telegram Logging Handler', description='Helps to retrieve chat_id')
    parser.add_argument('token')

    args = parser.parse_args()
    token = args.token

    handler = TelegramHandler(token, 'foo')
    chat_id = handler.get_chat_id()
    if not chat_id:
        print('Did not get chat id')
        print(handler.last_response.status_code, handler.last_response.text)
        exit(-1)
    print(chat_id)


if __name__ == '__main__':  # pragma: no cover
    main()
