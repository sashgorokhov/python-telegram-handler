import logging
from io import BytesIO

import requests

from telegram_handler.formatters import HtmlFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
logger.propagate = False

__all__ = ['TelegramHandler']


MAX_MESSAGE_LEN = 4096


class TelegramHandler(logging.Handler):
    last_response = None

    def __init__(self, token, chat_id=None, level=logging.NOTSET, timeout=2, disable_notification=False,
                 disable_web_page_preview=False):
        self.token = token
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.timeout = timeout
        self.chat_id = chat_id or self.get_chat_id()
        if not self.chat_id:
            level = logging.NOTSET
            logger.error('Did not get chat id. Setting handler logging level to NOTSET.')
        logger.info('Chat id: %s', self.chat_id)

        super(TelegramHandler, self).__init__(level=level)

        self.setFormatter(HtmlFormatter())

    @classmethod
    def format_url(cls, token, method):
        return 'http://botapi.antrekod.ru/bot%s/%s' % (token, method)

    def get_chat_id(self):
        response = self.request('getUpdates')
        if not response or not response.get('ok', False):
            logger.error('Telegram response is not ok: %s', str(response))
            return
        try:
            return response['result'][-1]['message']['chat']['id']
        except:
            logger.exception('Something went terribly wrong while obtaining chat id')
            logger.debug(response)

    def request(self, method, **kwargs):
        url = self.format_url(self.token, method)

        kwargs.setdefault('timeout', self.timeout)

        response = None
        try:
            response = requests.post(url, **kwargs)
            self.last_response = response
            response.raise_for_status()
            return response.json()
        except:
            logger.exception('Error while making POST to %s', url)
            logger.debug(str(kwargs))
            if response is not None:
                logger.debug(response.content)

        return response

    def send_message(self, text, **kwargs):
        data = {'text': text}
        data.update(kwargs)
        return self.request('sendMessage', json=data)

    def send_document(self, text, document, **kwargs):
        data = {'caption': text}
        data.update(kwargs)
        return self.request('sendDocument', data=data, files={'document': ('traceback.txt', document, 'text/plain')})

    def emit(self, record):
        text = self.format(record)

        data = {
            'chat_id': self.chat_id,
            'disable_web_page_preview': self.disable_web_page_preview,
            'disable_notification': self.disable_notification,
        }

        if getattr(self.formatter, 'parse_mode', None):
            data['parse_mode'] = self.formatter.parse_mode

        if len(text) < MAX_MESSAGE_LEN:
            response = self.send_message(text, **data)
        else:
            response = self.send_document(text[:1000], document=BytesIO(text.encode()), **data)

        if response and not response.get('ok', False):
            logger.warning('Telegram responded with ok=false status! {}'.format(response))
