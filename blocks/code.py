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
