import logging

from telegram_handler.utils import surround, tag, escape_html, escape_markdown

__all__ = ['TelegramFormatter', 'StyledFormatter', 'MarkdownFormatter', 'HtmlFormatter']


class TelegramFormatter(logging.Formatter):
    """Base formatter class suitable for use with `TelegramHandler`"""

    fmt = "%(asctime)s %(name)s %(levelname)s %(message)s"
    parse_mode = None

    def __init__(self, fmt=None, *args, **kwargs):
        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)


class StyledFormatter(TelegramFormatter):
    styles = {
        'bold': None,
        'italic': None,
        'inline': None,
        'inline_preformatted': None,
        'url': None
    }

    _escape_func = None
    _style_func = None

    escape_message = True
    escape_exception = False

    def __init__(self, *args, **kwargs):
        if 'escape_message' in kwargs:
            self.escape_exception = kwargs.pop('escape_message')
        if 'escape_exception' in kwargs:
            self.escape_exception = kwargs.pop('escape_exception')
        super(StyledFormatter, self).__init__(*args, **kwargs)

    def style_text(self, text, style_key, escape=True):
        if self._style_func is None:
            raise NotImplementedError('_style_func is not set')
        if not self.styles.get(style_key, None):
            raise NotImplementedError('Style {} not implemented'.format(style_key))
        if escape:
            text = self.escape(text)
        return self.__class__._style_func(text, self.styles[style_key])

    @classmethod
    def escape(cls, text):
        if not cls._escape_func:
            raise NotImplementedError('_escape_func not set')
        return cls._escape_func(text)

    def bold(cls, text, **kwargs):
        return cls.style_text(text, 'bold', **kwargs)

    def italic(cls, text, **kwargs):
        return cls.style_text(text, 'italic', **kwargs)

    def inline(cls, text, **kwargs):
        return cls.style_text(text, 'inline', **kwargs)

    def inline_preformatted(cls, text, **kwargs):
        return cls.style_text(text, 'inline_preformatted', **kwargs)

    def url(self, text, url, escape=True):
        if escape:
            text = self.escape(text)
        return self.styles['url'].format(text=text, url=url)

    def formatMessage(self, record):
        s = super(StyledFormatter, self).formatMessage(record)
        if self.escape_message:
            s = self.escape(s)
        return s

    def formatException(self, *args, **kwargs):
        string = super(StyledFormatter, self).formatException(*args, **kwargs)
        return self.inline_preformatted(string, escape=self.escape_exception)


class MarkdownFormatter(StyledFormatter):
    """Markdown formatter for telegram."""

    parse_mode = 'Markdown'

    styles = {
        'bold': '*',
        'italic': '_',
        'inline': '`',
        'inline_preformatted': '```',
        'url': '[{text}]({url})'
    }

    _escape_func = escape_markdown
    _style_func = surround

    escape_message = False


class HtmlFormatter(StyledFormatter):
    """HTML formatter for telegram."""

    parse_mode = 'HTML'

    styles = {
        'bold': 'b',
        'italic': 'i',
        'inline': 'code',
        'inline_preformatted': 'pre',
        'url': '<a href="{url}">{text}</a>'
    }

    _escape_func = escape_html
    _style_func = tag
