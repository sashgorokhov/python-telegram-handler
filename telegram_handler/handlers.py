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

    def __init__(self, token, chat_id, disable_notification=False, disable_web_page_preview=False, timeout=2,
                 level=logging.NOTSET):
        self.token = token
        self.chat_id = chat_id
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification
        self.timeout = timeout
        self.url = self.formatUrl(self.token, 'sendMessage')

        super(TelegramHandler, self).__init__(level=level)

        self.formatter = MarkdownFormatter()

    @classmethod
    def formatUrl(cls, token, method):
        return parse.urljoin(cls.base_url.format(token=token), method)

    def make_request(self, url, data):
        """
        :rtype: requests.Response|None
        """
        logger.debug(str(data))
        try:
            response = requests.post(self.url, data=data)
        except:
            logger.exception('Error while making POST %s', url)
            return None

        logger.debug(response.text)
        return response

    def sendMessage(self, text, **kwargs):
        """
        :param str text:
        :param dict kwargs:
        :rtype: requests.Response|None
        """

        data = {'text': text}
        data.update(kwargs)
        return self.make_request(self.url, data)

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
        if not response: return
        json = response.json()
        if not json['ok']:
            logger.warning('Telegram responded with ok=false status! {}'.format(response.text))
