from blocks.inline import format_inline_text


def create_quote_block(text: str) -> str:
    """引用文をWordPress Gutenbergのquoteブロックに変換します。"""
    safe_text = format_inline_text(text.strip())
    return (
        "<!-- wp:quote -->\n"
        '<blockquote class="wp-block-quote">\n'
        f"<p>{safe_text}</p>\n"
        "</blockquote>\n"
        "<!-- /wp:quote -->"
    )
