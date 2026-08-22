"""ショートコードをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from html import escape


def create_shortcode_block(shortcode_text: str) -> str:
    """ショートコードをWordPress Gutenbergのshortcodeブロックに変換します。"""
    safe_shortcode: str = escape(shortcode_text.strip())
    return f"<!-- wp:shortcode -->\n{safe_shortcode}\n<!-- /wp:shortcode -->"
