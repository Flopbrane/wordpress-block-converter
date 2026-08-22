from html import escape


def create_quote_block(text: str) -> str:
    """引用文をWordPress Gutenbergのquoteブロックに変換します。"""
    safe_text = escape(text.strip())
    return (
        "<!-- wp:quote -->\n"
        '<blockquote class="wp-block-quote">\n'
        f"<p>{safe_text}</p>\n"
        "</blockquote>\n"
        "<!-- /wp:quote -->"
    )
