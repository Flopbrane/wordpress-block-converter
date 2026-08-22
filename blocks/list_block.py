from blocks.inline import format_inline_text


def create_list_block(items: list[str], ordered: bool = False, use_html_block: bool = False) -> str:
    """箇条書きをWordPress Gutenbergのlistブロックに変換します。"""
    tag_name = "ol" if ordered else "ul"
    safe_items = [format_inline_text(item.strip()) for item in items if item.strip()]
    list_items = "\n".join(f"<li>{item}</li>" for item in safe_items)
    list_html = f"<{tag_name}>\n{list_items}\n</{tag_name}>"

    if use_html_block:
        return f"<!-- wp:html -->\n{list_html}\n<!-- /wp:html -->"

    return (
        f"<!-- wp:list -->\n"
        f"{list_html}\n"
        "<!-- /wp:list -->"
    )
