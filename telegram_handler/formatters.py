import logging

from telegram_handler.utils import surround

__all__ = ['TelegramFormatter', 'StyledFormatter', 'MarkdownFormatter']


class TelegramFormatter(logging.Formatter):
    """Base formatter class suitable for use with `TelegramHandler`"""

    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
    parse_mode = None

    def __init__(self, fmt=None, *args, **kwargs):
        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)


class StyledFormatter(TelegramFormatter):
    """Formatter with helper methods for styling output."""

    _bold = None
    _italic = None
    _inline = None
    _inline_preformatted = None
    _url = None

    @classmethod
    def bold(cls, text):
        return surround(text, cls._bold)

    @classmethod
    def italic(cls, text):
        return surround(text, cls._italic)

    @classmethod
    def inline(cls, text):
        return surround(text, cls._inline)

    @classmethod
    def inline_preformatted(cls, text):
        return surround(text, cls._inline_preformatted)

    @classmethod
    def url(self, text, url):
        return self._url % (text, url)

    def formatException(self, *args, **kwargs):
        string = super(StyledFormatter, self).formatException(*args, **kwargs)
        return self.inline_preformatted(string)


class MarkdownFormatter(StyledFormatter):
    """Markdown formatter for telegram."""

    parse_mode = 'Markdown'

    _bold = '*'
    _italic = '_'
    _inline = '`'
    _inline_preformatted = '```'
    _url = '[%s](%s)'
