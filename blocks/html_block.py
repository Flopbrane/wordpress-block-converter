def create_html_block(html_text: str) -> str:
    """HTMLをWordPress Gutenbergのcustom HTMLブロックに変換します。"""
    clean_html = html_text.strip()
    return f"<!-- wp:html -->\n{clean_html}\n<!-- /wp:html -->"
