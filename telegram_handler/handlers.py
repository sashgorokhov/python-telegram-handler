import logging
from io import BytesIO

import requests

from telegram_handler.TelegramBotQueue import MQBot
from telegram_handler.formatters import HtmlFormatter

logger = logging.getLogger(__name__)
logger.setLevel(logging.NOTSET)
logger.propagate = False

__all__ = ['TelegramHandler']


MAX_MESSAGE_LEN = 4096


class TelegramHandler(logging.Handler):
    API_ENDPOINT = 'https://api.telegram.org'
    last_response = None

    def __init__(self, token, chat_id=None, level=logging.WARNING, timeout=2, disable_notification=False,
                 disable_notification_logging_level=logging.ERROR,
                 disable_web_page_preview=False, proxies=None, **kwargs):
        self.token = token
        self.disable_web_page_preview = disable_web_page_preview
        # self.disable_notification = kwargs.get('custom_disable_notification', disable_notification)
        self.disable_notification = disable_notification
        if 'custom_enable_notification' in kwargs:
            self.disable_notification = not kwargs.get('custom_enable_notification')
        self.disable_notification_logging_level = disable_notification_logging_level
        self.timeout = timeout
        self.proxies = proxies
        self.chat_id = chat_id or self.get_chat_id()
        level = kwargs.get('custom_logging_level', level)
        if not self.chat_id:
            level = logging.NOTSET
            logger.error('Did not get chat id. Setting handler logging level to NOTSET.')
        logger.info('Chat id: %s', self.chat_id)

        super(TelegramHandler, self).__init__(level=level)

        self.setFormatter(HtmlFormatter(use_emoji=kwargs.get('use_emoji', True)))
        self.bot = MQBot(token=self.token)

    @classmethod
    def format_url(cls, token, method):
        return '%s/bot%s/%s' % (cls.API_ENDPOINT, token, method)

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
        kwargs.setdefault('proxies', self.proxies)
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

    """
    def send_message(self, text, **kwargs):
        data = {'text': text}
        data.update(kwargs)
        return self.request('sendMessage', json=data)

    def send_document(self, text, document, **kwargs):
        data = {'caption': text}
        data.update(kwargs)
        return self.request('sendDocument', data=data, files={'document': ('traceback.txt', document, 'text/plain')})
    """

    def emit(self, record):
        text = self.format(record)
        disable_notification = (record.levelno is None or record.levelno < self.disable_notification_logging_level) or \
                               self.disable_notification
        data = {
            'chat_id': self.chat_id,
            'disable_web_page_preview': self.disable_web_page_preview,
            'disable_notification': disable_notification,
        }

        if getattr(self.formatter, 'parse_mode', None):
            data['parse_mode'] = self.formatter.parse_mode

        kwargs = dict()
        if self.timeout is not None:
            kwargs.setdefault('timeout', self.timeout)
        if self.proxies is not None:
            kwargs.setdefault('proxies', self.proxies)



        try:
            if len(text) < MAX_MESSAGE_LEN:
                response = self.bot.send_message(text=text, api_kwargs=kwargs, **data)
            else:
                del data['disable_web_page_preview']
                response = self.bot.send_document(caption=text[:1000], api_kwargs=kwargs, document=BytesIO(text.encode()),
                                                  filename="traceback.txt",
                                                  **data)
            if not response:
                logger.warning(
                    'Telegram responded with ok=false status! {}'.format(
                        response))
        except Exception as e:
            logger.exception("Error while sending message to telegram, "
                             f"{str(e)}")
            logger.debug(str(kwargs))
