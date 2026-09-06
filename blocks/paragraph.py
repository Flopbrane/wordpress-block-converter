"""段落をWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from blocks.inline import format_inline_text


def create_paragraph_block(
    text: str,
    line_break_html: str = "<br>",
    convert_inline_code: bool = False,
) -> str:
    """段落をWordPress Gutenbergのparagraphブロックに変換します。"""
    safe_text = format_inline_text(
        text.strip(),
        line_break_html=line_break_html,
        convert_inline_code=convert_inline_code,
    )
    return f"<!-- wp:paragraph -->\n<p>{safe_text}</p>\n<!-- /wp:paragraph -->"
