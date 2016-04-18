from .formatters import *
from .handlers import *


def main():
    import argparse, requests

    parser = argparse.ArgumentParser('Telegram Loggin Handler', description='Helps to retrieve chat_id')
    parser.add_argument('token')

    args = parser.parse_args()
    token = args.token

    url = TelegramHandler.formatUrl(token, 'getUpdates')

    json = requests.get(url).json()

    if not json['ok']:
        raise ValueError('Something went wrong! getUdates response is not ok! {}'.format(json))

    try:
        chat_id = json['result'][0]['message']['chat']['id']
    except:
        raise ValueError('Something went wrong! Got such a json: {}'.format(json))

    print(chat_id)


if __name__ == '__main__':
    main()
