from html import escape


def create_paragraph_block(text: str, line_break_html: str = "<br>") -> str:
    """段落をWordPress Gutenbergのparagraphブロックに変換します。"""
    safe_text = line_break_html.join(escape(line) for line in text.strip().splitlines())
    return f"<!-- wp:paragraph -->\n<p>{safe_text}</p>\n<!-- /wp:paragraph -->"
