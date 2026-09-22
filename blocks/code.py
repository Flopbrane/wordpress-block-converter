"""コードをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from html import escape
from html.entities import html5

HTML_ENTITY_PATTERN: re.Pattern[str] = re.compile(
    r"&(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);"
)
ESCAPED_HTML_TAG_PATTERN: re.Pattern[str] = re.compile(
    r"&lt;/?[A-Za-z][A-Za-z0-9:-]*(?:\s[^&<>]*)?&gt;"
)


def escape_html_text(text: str) -> str:
    """本文やHTML内の通常テキストをエスケープします。"""
    return escape(text, quote=True)


def escape_code_text(text: str) -> str:
    """コード表示用に、引用符は残してHTML特殊文字をエスケープします。"""
    if not ESCAPED_HTML_TAG_PATTERN.search(text):
        return escape(text, quote=False)

    parts: list[str] = []
    current_position = 0

    for entity_match in HTML_ENTITY_PATTERN.finditer(text):
        entity_text = entity_match.group(0)
        if not _is_html_entity(entity_text):
            continue

        parts.append(escape(text[current_position:entity_match.start()], quote=False))
        parts.append(entity_text)
        current_position = entity_match.end()

    parts.append(escape(text[current_position:], quote=False))
    return "".join(parts)


def _is_html_entity(entity_text: str) -> bool:
    if entity_text.startswith("&#"):
        return _is_numeric_html_entity(entity_text)
    return entity_text[1:] in html5


def _is_numeric_html_entity(entity_text: str) -> bool:
    try:
        if entity_text.lower().startswith("&#x"):
            int(entity_text[3:-1], 16)
        else:
            int(entity_text[2:-1], 10)
    except ValueError:
        return False
    return True


def create_code_block(text: str) -> str:
    """コードをWordPress Gutenbergのcodeブロックに変換します。"""
    safe_text = escape_code_text(text)
    return (
        "<!-- wp:code -->\n"
        f'<pre class="wp-block-code"><code>{safe_text}</code></pre>\n'
        "<!-- /wp:code -->"
    )


def create_emphasis_code_block(text: str) -> str:
    """強調コードをstyle付きpre/codeのHTMLブロックに変換します。"""
    safe_text = escape_code_text(text.strip())
    style = (
        "display:inline-block;border:1px solid #999;padding:16px;"
        "border-radius:8px;background-color:#f9f9f9;"
    )
    return (
        "<!-- wp:html -->\n"
        f'<pre class="wp-block-code" style="{style}"><code>{safe_text}</code></pre>\n'
        "<!-- /wp:html -->"
    )
