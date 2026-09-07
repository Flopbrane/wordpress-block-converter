"""コードをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from html import escape


def create_code_block(text: str) -> str:
    """コードをWordPress Gutenbergのcodeブロックに変換します。"""
    safe_text = escape(text.rstrip())
    return (
        "<!-- wp:code -->\n"
        f'<pre class="wp-block-code"><code>{safe_text}</code></pre>\n'
        "<!-- /wp:code -->"
    )


def create_emphasis_code_block(text: str) -> str:
    """強調コードを横幅が広がりすぎないHTMLブロックに変換します。"""
    safe_text = escape(text.strip())
    style = (
        "display:inline-block; border:1px solid #999; padding:16px; "
        "border-radius:8px; background-color:#f9f9f9;"
    )
    return (
        "<!-- wp:html -->\n"
        f'<pre class="wp-block-code" style="{style}"><code>{safe_text}</code></pre>\n'
        "<!-- /wp:html -->"
    )
