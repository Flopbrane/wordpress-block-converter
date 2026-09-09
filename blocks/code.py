"""コードをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from html import escape


def escape_html_text(text: str) -> str:
    """本文やHTML内の通常テキストをエスケープします。"""
    return escape(text, quote=True)


def escape_code_text(text: str) -> str:
    """コード表示用に、引用符は残してHTML特殊文字をエスケープします。"""
    return escape(text, quote=False)


def create_code_block(text: str) -> str:
    """コードをWordPress Gutenbergのcodeブロックに変換します。"""
    safe_text = escape_code_text(text.rstrip())
    return (
        "<!-- wp:code -->\n"
        f'<pre class="wp-block-code"><code>{safe_text}</code></pre>\n'
        "<!-- /wp:code -->"
    )


def create_emphasis_code_block(text: str) -> str:
    """強調コードをWordPress Gutenbergのcodeブロックに変換します。"""
    safe_text = escape_code_text(text.strip())
    style = (
        "display:inline-block; border:1px solid #999; padding:16px; "
        "border-radius:8px; background-color:#f9f9f9;"
    )
    return (
        "<!-- wp:code -->\n"
        f'<pre class="wp-block-code" style="{style}"><code>{safe_text}</code></pre>\n'
        "<!-- /wp:code -->"
    )
