"""見出しをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from blocks.inline import format_inline_text


def create_heading_block(text: str, level: int = 2) -> str:
    """見出しをWordPress Gutenbergのheadingブロックに変換します。"""
    safe_level = min(max(level, 1), 6)
    safe_text = format_inline_text(text.strip())

    return (
        f'<!-- wp:heading {{"level":{safe_level}}} -->\n'
        f'<h{safe_level} class="wp-block-heading">{safe_text}</h{safe_level}>\n'
        "<!-- /wp:heading -->"
    )
