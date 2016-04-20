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

    def test_handler_url(self):
        self.assertEqual(self.handler.url, self.handler.formatUrl(self.token, 'sendMessage'))

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
        self.handler.sendMessage(text, **additional_kwargs)

        magic_mock.assert_called_once_with(self.handler.url, data=data)

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


class TestCLI(unittest.TestCase):
    token = 'TestToken'
    chat_id = '123456'

    @mock.patch('argparse.ArgumentParser._print_message')
    @mock.patch('sys.argv', new=[__file__])
    def test_cli_token_abcent(self, magic_mock):
        with self.assertRaises(SystemExit):
            main()

    @mock.patch('requests.Response.json', new=lambda *args, **kwargs: {'ok': False})
    @mock.patch('sys.argv', new=[__file__, token])
    def test_response_not_ok(self):
        with self.assertRaises(ValueError) as error:
            main()
        self.assertIn('getUdates response is not ok', str(error.exception))

    @mock.patch('requests.Response.json', new=lambda *args, **kwargs: {'ok': True, 'result': []})
    @mock.patch('sys.argv', new=[__file__, token])
    def test_response_invalid_shema(self):
        with self.assertRaises(Exception) as error:
            main()
        self.assertIn('Got such a json', str(error.exception))

    @mock.patch('requests.Response.json',
                new=lambda *args, **kwargs: {'ok': True, 'result': [{'message': {'chat': {'id': TestCLI.chat_id}}}]})
    @mock.patch('sys.argv', new=[__file__, token])
    def test_response_shema_ok(self):
        io = StringIO()
        with mock.patch('sys.stdout', new=io):
            main()
        self.assertIn(self.chat_id, io.getvalue())


class TestUtils(unittest.TestCase):
    def test_surround(self):
        ch = 'hello'
        text = 'world'

        result = utils.surround(text, ch)

        self.assertTrue(result.startswith(ch))
        self.assertTrue(result.endswith(ch))

    def test_tag_escape(self):
        tag = 'p'
        escaped_text = '<b>'
        text = 'Hello, {} world!'.format(escaped_text)

        result = utils.tag(text, tag, escape=True)

        self.assertNotIn(result, escaped_text)


class TestFormatters(unittest.TestCase):
    def setUp(self):
        self.styled_formatter = formatters.StyledFormatter()
        self.html_formatter = formatters.HtmlFormatter()
        self.markdown_formatter = formatters.MarkdownFormatter()

    def test_styled_formatter_unconfigured(self):
        with self.assertRaises(NotImplementedError) as error:
            self.styled_formatter.escape('Some Text')

        self.assertIn('not set', str(error.exception))

        with self.assertRaises(NotImplementedError) as error:
            self.styled_formatter.style_text('Some Text', list(self.styled_formatter.styles.keys())[0])

        self.assertIn('not set', str(error.exception))

        with self.assertRaises(NotImplementedError) as error:
            self.styled_formatter.bold('text')

        self.assertIn('not set', str(error.exception))

    def test_invalid_style_key(self):
        formatter = type('TestFormatter', (formatters.StyledFormatter,),
                         {'_style_func': lambda *args, **kwargs: (args, kwargs)})()

        with self.assertRaises(NotImplementedError) as error:
            formatter.style_text('Some text', 'invalid key')

        self.assertIn('not implemented', str(error.exception))

    @mock.patch('telegram_handler.formatters.HtmlFormatter._escape_func')
    def test_escape(self, magic_mock):
        text = 'Some text'
        self.html_formatter.escape(text)
        magic_mock.assert_called_once_with(text)

    @mock.patch('telegram_handler.formatters.HtmlFormatter._style_func')
    @mock.patch('telegram_handler.formatters.HtmlFormatter.escape')
    def test_style_text(self, escape_mock, style_mock):
        text = 'Some text'
        style_key = list(self.html_formatter.styles.keys())[0]

        self.html_formatter.style_text(text, style_key)

        escape_mock.assert_called_once_with(text)
        style_mock.assert_called_once()

        self.html_formatter.style_text(text, style_key, escape=False)

        escape_mock.assert_called_once()
