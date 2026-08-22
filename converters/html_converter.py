"""HTML変換用のコンバータファイルです"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from collections.abc import Callable
from html import unescape
from re import Pattern
from typing import Any, cast

from dictionaries.html_dict import (
    DIRECT_URL_RULES,
    EMBED_PROVIDER_RULES,
    HTML_ATTRIBUTE_PATTERN,
    HTML_BLOCK_RULES,
    HTML_BR_PATTERN,
    HTML_EMBED_RULE,
    HTML_EMPHASIS_PATTERN,
    HTML_LINK_PATTERN,
    HTML_LIST_ITEM_PATTERN,
    HTML_SHORTCODE_RULE,
    HTML_STRONG_PATTERN,
    HTML_TAG_PATTERN,
)


def convert_html_to_gutenberg(load_file: str) -> str:
    """HTMLをWordPress Gutenberg向けHTMLに変換します。"""
    blocks: list[str] = []
    block_matches: list[tuple[int, int, str, re.Match[str]]] = []

    for block_type, rule in HTML_BLOCK_RULES.items():
        pattern = cast(Pattern[str], rule["pattern"])
        for block_match in pattern.finditer(load_file):
            block_matches.append((block_match.start(), block_match.end(), block_type, block_match))

    used_end = 0
    sorted_matches: list[tuple[int, int, str, re.Match[str]]] = sorted(
        block_matches, key=lambda item: (item[0], -(item[1] - item[0]))
        )

    for start, end, block_type, block_match in sorted_matches:
        if start < used_end:
            continue

        used_end: int = end
        rule: dict[str, Any] = HTML_BLOCK_RULES[block_type]

        if block_type == "paragraph":
            paragraph_html: str | Any = block_match.group(1)
            paragraph_text: str = _clean_html_text(paragraph_html)
            if not paragraph_text:
                image_block: str | None = _create_image_block_from_html(paragraph_html)
                if image_block:
                    blocks.append(image_block)
                    continue

            if paragraph_text:
                shortcode_block: str | None = _create_shortcode_block(paragraph_text)
                direct_url_block: str | None = _create_direct_url_block(paragraph_text)
                provider_info: dict[str, Any] | None = _find_embed_provider(paragraph_text)

                if shortcode_block:
                    blocks.append(shortcode_block)
                elif direct_url_block:
                    blocks.append(direct_url_block)
                elif provider_info and cast(Pattern[str], HTML_EMBED_RULE["pattern"]).match(
                    paragraph_text
                ):
                    embed_converter: Callable[..., str] = cast(
                        Callable[..., str], HTML_EMBED_RULE["converter"]
                        )
                    blocks.append(
                        embed_converter(
                            paragraph_text,
                            provider_info["providerNameSlug"],
                            embed_type=provider_info["type"],
                            responsive=provider_info["responsive"],
                            aspect=provider_info["aspect"],
                        )
                    )
                else:
                    paragraph_converter: Callable[[str], str] = cast(
                        Callable[[str], str], rule["converter"]
                        )
                    blocks.append(paragraph_converter(paragraph_text))
        elif block_type == "heading":
            heading_level = int(block_match.group(1))
            heading_text: str = _clean_html_text(block_match.group(2))
            if heading_text:
                heading_converter: Callable[[str, int], str] = cast(
                    Callable[[str, int], str], rule["converter"]
                    )
                blocks.append(heading_converter(heading_text, heading_level))
        elif block_type in {"unordered_list", "ordered_list"}:
            list_items: list[str] = _extract_list_items(block_match.group(1))
            if list_items:
                list_converter: Callable[..., str] = cast(Callable[..., str], rule["converter"])
                blocks.append(
                    list_converter(
                        list_items,
                        ordered=rule["ordered"],
                        use_html_block=rule["use_html_block"],
                    )
                )
        elif block_type == "quote":
            quote_text = _clean_html_text(block_match.group(1))
            if quote_text:
                quote_converter: Callable[[str], str] = cast(
                    Callable[[str], str], rule["converter"]
                    )
                blocks.append(quote_converter(quote_text))
        elif block_type == "code":
            code_text: str | Any = (
                block_match.group(1)
                if block_match.group(1) is not None else block_match.group(2)
            )
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
            blocks.append(rule["converter"]())

    return "\n\n".join(blocks)


def _clean_html_text(text: str) -> str:
    text = HTML_LINK_PATTERN.sub(_convert_html_link_to_markdown_link, text)
    text = HTML_STRONG_PATTERN.sub(_convert_html_strong_to_markdown_strong, text)
    text = HTML_EMPHASIS_PATTERN.sub(_convert_html_emphasis_to_markdown_emphasis, text)
    text = HTML_BR_PATTERN.sub("\n", text)
    text = HTML_TAG_PATTERN.sub("", text)
    return unescape(text).strip()


def _convert_html_link_to_markdown_link(link_match) -> str:
    url: str = link_match.group(1).strip()
    label: str = HTML_TAG_PATTERN.sub("", link_match.group(2)).strip()
    return f"[{label}]({url})"


def _convert_html_strong_to_markdown_strong(strong_match) -> str:
    text: str = HTML_TAG_PATTERN.sub("", strong_match.group(2)).strip()
    return f"**{text}**"


def _convert_html_emphasis_to_markdown_emphasis(emphasis_match) -> str:
    text: str = HTML_TAG_PATTERN.sub("", emphasis_match.group(2)).strip()
    return f"*{text}*"


def _extract_list_items(text: str) -> list[str]:
    list_items: list[str] = []

    for list_item_match in HTML_LIST_ITEM_PATTERN.finditer(text):
        item_text: str = _clean_html_text(list_item_match.group(1))
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
    image_rule: dict[str, Any] = HTML_BLOCK_RULES["image"]
    image_match: re.Match[str] | None = cast(Pattern[str], image_rule["pattern"]).search(html_text)
    if not image_match:
        return None

    image_attributes: dict[str, str] = _extract_html_attributes(image_match.group(0))
    image_src: str = image_attributes.get("src", "")
    if not image_src:
        return None

    image_converter: Callable[[str, str], str] = cast(
        Callable[[str, str], str],
        image_rule["converter"]
        )
    return image_converter(image_src, image_attributes.get("alt", ""))


def _find_embed_provider(url: str) -> dict[str, str | bool | None] | None:
    lower_url: str = url.lower()

    for compare_text, provider_info in EMBED_PROVIDER_RULES.items():
        if compare_text in lower_url:
            return provider_info

    return None


def _create_shortcode_block(text: str) -> str | None:
    if cast(Pattern[str], HTML_SHORTCODE_RULE["pattern"]).match(text):
        shortcode_converter: Callable[[str], str] = cast(
            Callable[[str], str],
            HTML_SHORTCODE_RULE["converter"]
        )
        return shortcode_converter(text)

    return None


def _create_direct_url_block(url: str) -> str | None:
    if not cast(Pattern[str], HTML_EMBED_RULE["pattern"]).match(url):
        return None

    lower_url: str = url.lower().split("?", 1)[0].split("#", 1)[0]

    for rule in DIRECT_URL_RULES.values():
        file_extensions: list[str] = cast(list[str], rule["extensions"])
        if any(lower_url.endswith(file_extension) for file_extension in file_extensions):
            direct_url_converter: Callable[[str], str] = cast(
                Callable[[str], str], rule["converter"]
            )
            return direct_url_converter(url)

    return None
