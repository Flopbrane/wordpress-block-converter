from html import escape


def create_shortcode_block(shortcode_text: str) -> str:
    """ショートコードをWordPress Gutenbergのshortcodeブロックに変換します。"""
    safe_shortcode = escape(shortcode_text.strip())
    return f"<!-- wp:shortcode -->\n{safe_shortcode}\n<!-- /wp:shortcode -->"
