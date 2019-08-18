import json
import logging

import mock
import pytest
import requests

import telegram_handler.handlers


# From http://stackoverflow.com/questions/899067/how-should-i-verify-a-log-message-when-testing-python-code-under-nose
class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.

    Messages are available from an instance's ``messages`` dict, in order, indexed by
    a lowercase log level string (e.g., 'debug', 'info', etc.).
    """

    def __init__(self, *args, **kwargs):
        self.messages = {'debug': [], 'info': [], 'warning': [], 'error': [],
                         'critical': []}
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        "Store a message from ``record`` in the instance's ``messages`` dict."
        self.acquire()
        try:
            name = record.levelname.lower()
            self.messages.setdefault(name, [])
            self.messages[name].append(record.getMessage())
        finally:
            self.release()

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                message_list.clear()
        finally:
            self.release()


@pytest.fixture
def handler():
    handler = telegram_handler.handlers.TelegramHandler('foo', 'bar', level=logging.DEBUG)
    telegram_handler.handlers.logger.handlers = []
    telegram_handler.handlers.logger.addHandler(MockLoggingHandler())
    telegram_handler.handlers.logger.level = logging.DEBUG
    return handler


def test_emit(handler):
    record = logging.makeLogRecord({'msg': 'hello'})

    with mock.patch('requests.post') as patch:
        handler.emit(record)

    assert patch.called
    assert patch.call_count == 1
    assert patch.call_args[1]['json']['chat_id'] == 'bar'
    assert 'hello' in patch.call_args[1]['json']['text']
    assert patch.call_args[1]['json']['parse_mode'] == 'HTML'

def test_emit_big_message(handler):
    message = '*' * telegram_handler.handlers.MAX_MESSAGE_LEN

    record = logging.makeLogRecord({'msg': message})

    with mock.patch('requests.post') as patch:
        handler.emit(record)

    assert patch.called
    assert patch.call_count == 1


def test_emit_http_exception(handler):
    record = logging.makeLogRecord({'msg': 'hello'})

    with mock.patch('requests.post') as patch:
        response = requests.Response()
        response.status_code = 500
        response._content = 'Server error'.encode()
        patch.return_value = response
        handler.emit(record)

    assert telegram_handler.handlers.logger.handlers[0].messages['error']
    assert telegram_handler.handlers.logger.handlers[0].messages['debug']


def test_emit_telegram_error(handler):
    record = logging.makeLogRecord({'msg': 'hello'})

    with mock.patch('requests.post') as patch:
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({'ok': False}).encode()
        patch.return_value = response
        handler.emit(record)

    assert telegram_handler.handlers.logger.handlers[0].messages['warning']


def test_get_chat_id_success(handler):
    with mock.patch('requests.post') as patch:
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({'ok': True, 'result': [{'message': {'chat': {'id': 'foo'}}}]}).encode()
        patch.return_value = response

        assert handler.get_chat_id() == 'foo'


def test_get_chat_id_telegram_error(handler):
    with mock.patch('requests.post') as patch:
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({'ok': False}).encode()
        patch.return_value = response

        assert handler.get_chat_id() is None

    assert telegram_handler.handlers.logger.handlers[0].messages['error']


def test_get_chat_id_no_response(handler):
    with mock.patch.object(handler, 'request') as patch:
        patch.return_value = None
        value = handler.get_chat_id()

    assert value is None
    patch.assert_called_once()


def test_get_chat_id_response_invalid_format(handler):
    with mock.patch('requests.post') as patch:
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({'ok': True, 'result': []}).encode()
        patch.return_value = response

        assert handler.get_chat_id() is None

    assert telegram_handler.handlers.logger.handlers[0].messages['error']
    assert telegram_handler.handlers.logger.handlers[0].messages['debug']


def test_handler_init_without_chat():
    with mock.patch('requests.post') as patch:
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({'ok': False}).encode()
        patch.return_value = response

        handler = telegram_handler.handlers.TelegramHandler('foo', level=logging.INFO)

        assert patch.called
        assert telegram_handler.handlers.logger.handlers[0].messages['error']

        assert handler.level == logging.NOTSET

def test_handler_respects_proxy():
    proxies = {
        'http': 'http_proxy_sample',
        'https': 'https_proxy_sample',
    }

    handler = telegram_handler.handlers.TelegramHandler('foo', 'bar', level=logging.INFO, proxies=proxies)
    
    record = logging.makeLogRecord({'msg': 'hello'})

    with mock.patch('requests.post') as patch:
        handler.emit(record)

    assert patch.call_args[1]['proxies'] == proxies

def test_custom_formatter(handler):
    handler.setFormatter(logging.Formatter())

    record = logging.makeLogRecord({'msg': 'hello'})

    with mock.patch('requests.post') as patch:
        handler.emit(record)

    assert 'parse_mode' not in patch.call_args[1]['json']
