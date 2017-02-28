import logging
import os
import sys
import unittest
from collections import namedtuple
from logging.config import dictConfig

import mock
from six import StringIO

from telegram_handler import handlers, main, utils, formatters


class TestTelegramHandler(unittest.TestCase):
    token = 'TestToken'
    chat_id = '1234567'

    def setUp(self):
        self.handler = handlers.TelegramHandler(self.token, self.chat_id)

    def log_record(self, msg, **kwargs):
        kwargs['msg'] = msg
        return logging.makeLogRecord(kwargs)

    def emit(self, *args, **kwargs):
        return self.handler.emit(self.log_record(*args, **kwargs))

    # def format(self, *args, **kwargs):
    #     return self.handler.format(self.log_record(*args, **kwargs))

    @mock.patch('requests.post')
    def test_send_message(self, magic_mock):
        text = 'Test Text'
        additional_kwargs = {
            'foo': 'bar'
        }
        data = {
            'text': text
        }
        data.update(additional_kwargs)
        self.handler.send_message(text, **additional_kwargs)

        url = self.handler.format_url(self.handler.token, 'sendMessage')
        magic_mock.assert_called_once_with(url, data=data, timeout=self.handler.timeout)

    @mock.patch('requests.post')
    def test_emit(self, magic_mock):
        response = namedtuple('Response', ['json', 'text'])
        magic_mock.return_value = response(json=lambda *args, **kwargs: {'ok': True}, text='Some text')

        record = self.log_record('Test Text')
        self.handler.emit(record)

        url, data = magic_mock.call_args
        url = url[0]
        data = data['data']

        self.assertEqual(url, self.handler.url)

        expected_data = {
            'text': self.handler.format(record),
            'parse_mode': self.handler.formatter.parse_mode,
            'chat_id': self.chat_id,
            'disable_web_page_preview': self.handler.disable_web_page_preview,
            'disable_notification': self.handler.disable_notification,
        }
        self.assertEqual(data, expected_data)

    @mock.patch('sys.path', new=sys.path + [os.path.dirname(os.path.dirname(__file__))])
    @mock.patch('telegram_handler.TelegramHandler.emit')
    def test_hanler_configuring(self, magic_mock):
        logger_name = self.__class__.__name__
        config = {
            'version': 1,
            'formatters': {
                'telegram': {
                    'class': 'telegram_handler.MarkdownFormatter',
                    'format': '%(levelname)s %(message)s'
                }
            },
            'handlers': {
                'telegram': {
                    'class': 'telegram_handler.TelegramHandler',
                    'formatter': 'telegram',
                    'token': self.token,
                    'chat_id': self.chat_id
                }
            },
            'loggers': {
                logger_name: {
                    'handlers': ['telegram'],
                    'level': 'DEBUG'
                }
            }
        }
        dictConfig(config)
        logger = logging.getLogger(logger_name)
        logger.info('Hello')

        magic_mock.assert_called_once()

    @mock.patch('requests.post')
    @mock.patch('telegram_handler.handlers.logger.exception')
    def test_requests_error_hanling(self, logger_mock, requests_mock):
        requests_mock.side_effect = ValueError('Test error')

        self.emit('Test message')

        requests_mock.assert_called_once()
        logger_mock.assert_called_once()

    @mock.patch('requests.post')
    @mock.patch('telegram_handler.handlers.logger.warning')
    def test_api_response_not_ok(self, logger_mock, magic_mock):
        response = namedtuple('Response', ['json', 'text'])
        magic_mock.return_value = response(json=lambda *args, **kwargs: {'ok': False}, text='Some text')

        self.emit('Some message')

        magic_mock.assert_called_once()
        logger_mock.assert_called_once()


