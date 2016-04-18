import logging

import requests

try:
    from urllib import parse
except ImportError:
    import urlparse as parse

from telegram_handler.formatters import MarkdownFormatter

logger = logging.getLogger(__name__)

__all__ = ['TelegramHandler']


class TelegramHandler(logging.Handler):
    base_url = 'https://api.telegram.org/bot{token}/'

    def __init__(self, token, chat_id, disable_notification=False, disable_web_page_preview=False,
                 level=logging.NOTSET):
        self.token = token
        self.chat_id = chat_id
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.url = self.formatUrl(self.token, 'sendMessage')

        super(TelegramHandler, self).__init__(level=level)

        self.formatter = MarkdownFormatter()

    @classmethod
    def formatUrl(cls, token, method):
        return parse.urljoin(cls.base_url.format(token=token), method)

    def sendMessage(self, text, **kwargs):
        data = {'text': text}
        data.update(kwargs)
        return requests.post(self.url, data=data)

    def emit(self, record):
        text = self.format(record)
        data = {
            'chat_id': self.chat_id,
            'disable_web_page_preview': self.disable_web_page_preview,
            'disable_notification': self.disable_notification,
        }
        if getattr(self.formatter, 'parse_mode', None):
            data['parse_mode'] = self.formatter.parse_mode
        response = self.sendMessage(text, **data)
        json = response.json()
        if not json['ok']:
            logger.debug(response.text)
