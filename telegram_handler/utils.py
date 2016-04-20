def surround(text, ch):
    """
    Surround `text` with `ch`

    :param str text:
    :param str ch:
    :rtype: str
    """
    return ch + str(text) + ch


def tag(text, tag, escape=True):
    """
    Inclose text in a tag

    :param str text:
    :param str tag:
    :rtype: str
    """
    if escape:
        text = escape_html(text)
    return '<{1}>{0}</{1}>'.format(text, tag)


def escape_html(text):
    """
    Escapes all html characters in text

    :param str text:
    :rtype: str
    """
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def escape_markdown(text):
    """
    Escapes all markdown characters in text

    :param str text:
    :rtype: str
    """
    return surround(text, '``')
