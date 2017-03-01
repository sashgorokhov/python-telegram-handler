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


def test_html_formatter_emoji():
    formatter = formatters.HtmlFormatter(use_emoji=True)

    emoji_level_map = {
        formatters.EMOJI.WHITE_CIRCLE: [logging.DEBUG],
        formatters.EMOJI.BLUE_CIRCLE: [logging.INFO],
        formatters.EMOJI.RED_CIRCLE: [logging.WARNING, logging.ERROR]
    }

    for emoji, levels in emoji_level_map.items():
        for level in levels:
            logrecord = logging.makeLogRecord({'levelno': level, 'levelname': logging.getLevelName(level)})
            s = formatter.format(logrecord)
            assert s.find(emoji) > 0, 'Emoji not found in %s' % level
