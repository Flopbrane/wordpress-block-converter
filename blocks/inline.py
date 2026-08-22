import re
from html import escape


MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
URL_PATTERN = re.compile(r"(?<![\"'=])\bhttps?://[^\s<]+")


def format_inline_text(text: str, line_break_html: str = "<br>") -> str:
    """本文中の文字を安全に整形し、リンクをHTMLに変換します。"""
    parts = []
    current_position = 0

    for link_match in MARKDOWN_LINK_PATTERN.finditer(text):
        parts.append(_escape_and_link_urls(text[current_position:link_match.start()]))
        parts.append(_create_link_html(link_match.group(1), link_match.group(2)))
        current_position = link_match.end()

    parts.append(_escape_and_link_urls(text[current_position:]))
    safe_text = "".join(parts)
    return line_break_html.join(safe_text.splitlines())


def _escape_and_link_urls(text: str) -> str:
    safe_text = escape(text)
    return URL_PATTERN.sub(lambda match: _create_link_html(match.group(0), match.group(0)), safe_text)


def _create_link_html(label: str, url: str) -> str:
    safe_label = escape(label.strip())
    safe_url = escape(url.strip(), quote=True)
    return f'<a href="{safe_url}">{safe_label}</a>'
