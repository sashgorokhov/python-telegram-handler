import logging

from telegram_handler.utils import escape_html

__all__ = ['TelegramFormatter', 'MarkdownFormatter', 'HtmlFormatter']


class TelegramFormatter(logging.Formatter):
    """Base formatter class suitable for use with `TelegramHandler`"""

    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
    parse_mode = None

    def __init__(self, fmt=None, *args, **kwargs):
        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)


class MarkdownFormatter(TelegramFormatter):
    """Markdown formatter for telegram."""
    parse_mode = 'Markdown'

    def formatException(self, *args, **kwargs):
        string = super(MarkdownFormatter, self).formatException(*args, **kwargs)
        return '```%s```' % string


class HtmlFormatter(TelegramFormatter):
    """HTML formatter for telegram."""
    parse_mode = 'HTML'

    def formatException(self, *args, **kwargs):
        string = super(HtmlFormatter, self).formatException(*args, **kwargs)
        return '<pre>%s</pre>' % escape_html(string)
