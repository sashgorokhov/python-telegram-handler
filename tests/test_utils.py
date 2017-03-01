from telegram_handler import utils


def test_escape_html():
    html = '<b>Hello, world!</b> Foo&bar'

    escaped = utils.escape_html(html)

    assert '<' not in escaped
    assert '>' not in escaped
    assert 'Foo&bar' not in escaped