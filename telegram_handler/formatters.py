import logging

from telegram_handler.utils import escape_html

__all__ = ['TelegramFormatter', 'MarkdownFormatter', 'HtmlFormatter']


class TelegramFormatter(logging.Formatter):
    """Base formatter class suitable for use with `TelegramHandler`"""

    fmt = ("%(asctime)s %(levelname)s\n[%(host)s:%(name)s:%(funcName)s]\n%("
           "message)s")
    parse_mode = None

    def __init__(self, fmt=None, *args, **kwargs):
        super(TelegramFormatter, self).__init__(fmt or self.fmt, *args, **kwargs)


class MarkdownFormatter(TelegramFormatter):
    """Markdown formatter for telegram."""
    fmt = ('`%(asctime)s` *%(levelname)s*\n[%(host)s:%(name)s:%('
           'funcName)s]\n%(message)s')
    parse_mode = 'Markdown'

    def formatException(self, *args, **kwargs):
        string = super(MarkdownFormatter, self).formatException(*args, **kwargs)
        return '```\n%s\n```' % string


class EMOJI:
    WHITE_CIRCLE = '\U000026AA'
    BLUE_CIRCLE = '\U0001F535'
    YELLOW_CIRCLE = '\U0001f7e1'
    RED_CIRCLE = '\U0001F534'
    BLACK_CIRCLE = '\u26AB'


class HtmlFormatter(TelegramFormatter):
    """HTML formatter for telegram."""
    fmt = ('<code>%(asctime)s</code> <b>%(levelname)s</b>\nFrom %(host)s:%('
           'name)s:%(funcName)s\n%(message)s')
    parse_mode = 'HTML'

    def __init__(self, *args, **kwargs):
        self.use_emoji = kwargs.pop('use_emoji', False)
        super(HtmlFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        """
        :param logging.LogRecord record:
        """
        super(HtmlFormatter, self).format(record)

        if record.funcName:
            record.funcName = escape_html(str(record.funcName))
        if record.name:
            record.name = escape_html(str(record.name))
        if record.msg:
            record.msg = escape_html(record.getMessage())
        if record.message:
            record.message = escape_html(record.message)
        if self.use_emoji:
            if record.levelno == logging.DEBUG:
                record.levelname += ' ' + EMOJI.WHITE_CIRCLE
            elif record.levelno == logging.INFO:
                record.levelname += ' ' + EMOJI.BLUE_CIRCLE
            elif record.levelno == logging.WARNING:
                record.levelname += ' ' + EMOJI.YELLOW_CIRCLE
            elif record.levelno == logging.ERROR:
                record.levelname += ' ' + EMOJI.RED_CIRCLE
            else:
                record.levelname += ' ' + EMOJI.BLACK_CIRCLE

        if hasattr(self, '_style'):
            return self._style.format(record)
        else:
            # py2.7 branch
            return self._fmt % record.__dict__

    def formatException(self, *args, **kwargs):
        string = super(HtmlFormatter, self).formatException(*args, **kwargs)
        return '<pre>%s</pre>' % escape_html(string)

    def formatStack(self, *args, **kwargs):
        string = super(HtmlFormatter, self).formatStack(*args, **kwargs)
        return '<pre>%s</pre>' % escape_html(string)
