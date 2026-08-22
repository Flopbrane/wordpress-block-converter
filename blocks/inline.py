"""インラインテキストをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from html import escape
from typing import LiteralString

MARKDOWN_LINK_PATTERN: re.Pattern[str] = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
URL_PATTERN: re.Pattern[str] = re.compile(r"(?<![\"'=])\bhttps?://[^\s<]+")
BOLD_PATTERN: re.Pattern[str] = re.compile(r"\*\*(.+?)\*\*")
ITALIC_PATTERN: re.Pattern[str] = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")


def format_inline_text(text: str, line_break_html: str = "<br>") -> str:
    """本文中の文字を安全に整形し、リンクをHTMLに変換します。"""
    parts = []
    current_position = 0

    for link_match in MARKDOWN_LINK_PATTERN.finditer(text):
        parts.append(_escape_and_link_urls(text[current_position:link_match.start()]))
        parts.append(_create_link_html(link_match.group(1), link_match.group(2)))
        current_position = link_match.end()

    parts.append(_escape_and_link_urls(text[current_position:]))
    safe_text: LiteralString = "".join(parts)
    return line_break_html.join(safe_text.splitlines())


def _escape_and_link_urls(text: str) -> str:
    safe_text: str = escape(text)
    safe_text = _format_emphasis(safe_text)
    return URL_PATTERN.sub(
        lambda match: _create_link_html(match.group(0), match.group(0)), safe_text
        )


def _create_link_html(label: str, url: str) -> str:
    safe_label: str = escape(label.strip())
    safe_url: str = escape(url.strip(), quote=True)
    return f'<a href="{safe_url}">{safe_label}</a>'


def _format_emphasis(text: str) -> str:
    text = BOLD_PATTERN.sub(r"<strong>\1</strong>", text)
    return ITALIC_PATTERN.sub(r"<em>\1</em>", text)
