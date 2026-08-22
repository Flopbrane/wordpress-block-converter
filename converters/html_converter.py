from html import unescape

from dictionaries.html_dict import (
    HTML_BLOCK_RULES,
    HTML_BR_PATTERN,
    HTML_EMBED_RULE,
    HTML_LIST_ITEM_PATTERN,
    HTML_TAG_PATTERN,
    VIDEO_EMBED_PROVIDERS,
)


def convert_html_to_gutenberg(load_file: str) -> str:
    """HTMLをWordPress Gutenberg向けHTMLに変換します。"""
    blocks = []
    block_matches = []

    for block_type, rule in HTML_BLOCK_RULES.items():
        for block_match in rule["pattern"].finditer(load_file):
            block_matches.append((block_match.start(), block_match.end(), block_type, block_match))

    used_end = 0
    sorted_matches = sorted(block_matches, key=lambda item: (item[0], -(item[1] - item[0])))

    for start, end, block_type, block_match in sorted_matches:
        if start < used_end:
            continue

        used_end = end
        rule = HTML_BLOCK_RULES[block_type]

        if block_type == "paragraph":
            paragraph_text = _clean_html_text(block_match.group(1))
            if paragraph_text:
                provider_name_slug = _find_embed_provider(paragraph_text)
                if provider_name_slug and HTML_EMBED_RULE["pattern"].match(paragraph_text):
                    blocks.append(HTML_EMBED_RULE["converter"](paragraph_text, provider_name_slug))
                else:
                    blocks.append(rule["converter"](paragraph_text))
        elif block_type == "heading":
            heading_level = int(block_match.group(1))
            heading_text = _clean_html_text(block_match.group(2))
            if heading_text:
                blocks.append(rule["converter"](heading_text, heading_level))
        elif block_type in {"unordered_list", "ordered_list"}:
            list_items = _extract_list_items(block_match.group(1))
            if list_items:
                blocks.append(
                    rule["converter"](
                        list_items,
                        ordered=rule["ordered"],
                        use_html_block=rule["use_html_block"],
                    )
                )
        elif block_type == "quote":
            quote_text = _clean_html_text(block_match.group(1))
            if quote_text:
                blocks.append(rule["converter"](quote_text))
        elif block_type == "code":
            code_text = block_match.group(1) if block_match.group(1) is not None else block_match.group(2)
            code_text = _clean_code_text(code_text)
            if code_text:
                blocks.append(rule["converter"](code_text))
        elif block_type == "table":
            blocks.append(rule["converter"](block_match.group(0)))
        elif block_type == "spacer":
            blocks.append(rule["converter"](rule["height"]))

    return "\n\n".join(blocks)


def _clean_html_text(text: str) -> str:
    text = HTML_BR_PATTERN.sub("\n", text)
    text = HTML_TAG_PATTERN.sub("", text)
    return unescape(text).strip()


def _extract_list_items(text: str) -> list[str]:
    list_items = []

    for list_item_match in HTML_LIST_ITEM_PATTERN.finditer(text):
        item_text = _clean_html_text(list_item_match.group(1))
        if item_text:
            list_items.append(item_text)

    return list_items


def _clean_code_text(text: str) -> str:
    text = HTML_TAG_PATTERN.sub("", text)
    return unescape(text).strip()


def _find_embed_provider(url: str) -> str | None:
    lower_url = url.lower()

    for compare_text, provider_name_slug in VIDEO_EMBED_PROVIDERS.items():
        if compare_text in lower_url:
            return provider_name_slug

    return None
