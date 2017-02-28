from telegram_handler import formatters


def test_markdown_formatter_exception():
    formatter = formatters.MarkdownFormatter()

    try:
        raise ValueError('test')
    except ValueError as e:
        string = formatter.formatException((type(e), e, e.__traceback__))
        assert string.startswith('```')
        assert string.endswith('```')


def test_html_formatter_exception():
    formatter = formatters.HtmlFormatter()

    try:
        raise ValueError('test')
    except ValueError as e:
        string = formatter.formatException((type(e), e, e.__traceback__))
        assert string.startswith('<pre>')
        assert string.endswith('</pre>')
