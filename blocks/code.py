from html import escape


def create_code_block(text: str) -> str:
    """コードをWordPress Gutenbergのcodeブロックに変換します。"""
    safe_text = escape(text.rstrip())
    return f"<!-- wp:code -->\n<pre><code>{safe_text}</code></pre>\n<!-- /wp:code -->"
