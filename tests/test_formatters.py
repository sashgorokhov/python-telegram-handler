import logging
import sys

from telegram_handler import formatters


def test_markdown_formatter_exception():
    formatter = formatters.MarkdownFormatter()

    try:
        raise ValueError('test')
    except ValueError as e:
        string = formatter.formatException(sys.exc_info())
        assert string.startswith('```')
        assert string.endswith('```')


def test_html_formatter_exception():
    formatter = formatters.HtmlFormatter()

    try:
        raise ValueError('test')
    except ValueError as e:
        string = formatter.formatException(sys.exc_info())
        assert string.startswith('<pre>')
        assert string.endswith('</pre>')


def test_html_formatter_format():
    formatter = formatters.HtmlFormatter()

    logrecord = logging.makeLogRecord(dict(name='<foo>', func='<module>', msg='Whatsup?', funcName='test'))
    s = formatter.format(logrecord)

    assert '<foo>' not in s
    assert '<module>' not in s
