from html import unescape

from dictionaries.html_dict import (
    EMBED_PROVIDER_RULES,
    HTML_ATTRIBUTE_PATTERN,
    HTML_BLOCK_RULES,
    HTML_BR_PATTERN,
    HTML_EMBED_RULE,
    HTML_LINK_PATTERN,
    HTML_LIST_ITEM_PATTERN,
    HTML_TAG_PATTERN,
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
            paragraph_html = block_match.group(1)
            paragraph_text = _clean_html_text(paragraph_html)
            if not paragraph_text:
                image_block = _create_image_block_from_html(paragraph_html)
                if image_block:
                    blocks.append(image_block)
                    continue

            if paragraph_text:
                provider_info = _find_embed_provider(paragraph_text)
                if provider_info and HTML_EMBED_RULE["pattern"].match(paragraph_text):
                    blocks.append(
                        HTML_EMBED_RULE["converter"](
                            paragraph_text,
                            provider_info["providerNameSlug"],
                            embed_type=provider_info["type"],
                            responsive=provider_info["responsive"],
                            aspect=provider_info["aspect"],
                        )
                    )
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
        elif block_type == "image":
            image_block = _create_image_block_from_html(block_match.group(0))
            if image_block:
                blocks.append(image_block)
        elif block_type == "spacer":
            blocks.append(rule["converter"](rule["height"]))

    return "\n\n".join(blocks)


def _clean_html_text(text: str) -> str:
    text = HTML_LINK_PATTERN.sub(_convert_html_link_to_markdown_link, text)
    text = HTML_BR_PATTERN.sub("\n", text)
    text = HTML_TAG_PATTERN.sub("", text)
    return unescape(text).strip()


def _convert_html_link_to_markdown_link(link_match) -> str:
    url = link_match.group(1).strip()
    label = HTML_TAG_PATTERN.sub("", link_match.group(2)).strip()
    return f"[{label}]({url})"


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


def _extract_html_attributes(tag_text: str) -> dict[str, str]:
    return {
        name.lower(): value
        for name, value in HTML_ATTRIBUTE_PATTERN.findall(tag_text)
    }


def _create_image_block_from_html(html_text: str) -> str | None:
    image_rule = HTML_BLOCK_RULES["image"]
    image_match = image_rule["pattern"].search(html_text)
    if not image_match:
        return None

    image_attributes = _extract_html_attributes(image_match.group(0))
    image_src = image_attributes.get("src", "")
    if not image_src:
        return None

    return image_rule["converter"](image_src, image_attributes.get("alt", ""))


def _find_embed_provider(url: str) -> dict[str, str | bool | None] | None:
    lower_url = url.lower()

    for compare_text, provider_info in EMBED_PROVIDER_RULES.items():
        if compare_text in lower_url:
            return provider_info

    return None
