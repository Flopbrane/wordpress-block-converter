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
from html.parser import HTMLParser
from re import Pattern
from typing import Any, cast

from blocks.html_block import create_html_block
from blocks.list_block import normalize_adjacent_list_blocks
from dictionaries.html_dict import (
    DIRECT_URL_RULES,
    EMBED_PROVIDER_RULES,
    HTML_ATTRIBUTE_PATTERN,
    HTML_BLOCK_RULES,
    HTML_BR_PATTERN,
    HTML_DIV_HTML_BLOCK_STYLE_KEYWORDS,
    HTML_EMBED_RULE,
    HTML_EMPHASIS_PATTERN,
    HTML_EXISTING_CUSTOM_HTML_BLOCK_PATTERN,
    HTML_LINK_PATTERN,
    HTML_LIST_ITEM_PATTERN,
    HTML_SHORTCODE_RULE,
    HTML_STRONG_PATTERN,
    HTML_TAG_PATTERN,
    HTML_WORDPRESS_BLOCK_COMMENT_PATTERN,
)


def convert_html_to_gutenberg(load_file: str) -> str:
    """HTMLをWordPress Gutenberg向けHTMLに変換します。"""
    blocks: list[str] = []
    block_matches: list[tuple[int, int, str, re.Match[str] | str]] = []

    for protected_start, protected_end, protected_html in _find_protected_html_blocks(load_file):
        block_matches.append((protected_start, protected_end, "protected_html", protected_html))

    for block_type, rule in HTML_BLOCK_RULES.items():
        pattern = cast(Pattern[str], rule["pattern"])
        for block_match in pattern.finditer(load_file):
            block_matches.append((block_match.start(), block_match.end(), block_type, block_match))

    used_end = 0
    sorted_matches: list[tuple[int, int, str, re.Match[str] | str]] = sorted(
        block_matches, key=lambda item: (item[0], -(item[1] - item[0]))
        )

    for start, end, block_type, block_match in sorted_matches:
        if start < used_end:
            continue

        used_end: int = end
        if block_type == "protected_html":
            protected_html = _remove_wordpress_block_comments(cast(str, block_match))
            if HTML_EXISTING_CUSTOM_HTML_BLOCK_PATTERN.fullmatch(protected_html.strip()):
                blocks.append(protected_html.strip())
            else:
                blocks.append(create_html_block(protected_html))
            continue

        block_match = cast(re.Match[str], block_match)
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

    return normalize_adjacent_list_blocks("\n\n".join(blocks))


def _clean_html_text(text: str) -> str:
    text = HTML_LINK_PATTERN.sub(_convert_html_link_to_markdown_link, text)
    text = HTML_STRONG_PATTERN.sub(_convert_html_strong_to_markdown_strong, text)
    text = HTML_EMPHASIS_PATTERN.sub(_convert_html_emphasis_to_markdown_emphasis, text)
    text = HTML_BR_PATTERN.sub("\n", text)
    text = HTML_TAG_PATTERN.sub("", text)
    return unescape(text).strip()


def _remove_wordpress_block_comments(html_text: str) -> str:
    return HTML_WORDPRESS_BLOCK_COMMENT_PATTERN.sub("", html_text)


def _find_protected_html_blocks(load_file: str) -> list[tuple[int, int, str]]:
    protected_blocks: list[tuple[int, int, str]] = []

    for custom_html_match in HTML_EXISTING_CUSTOM_HTML_BLOCK_PATTERN.finditer(load_file):
        protected_blocks.append(
            (custom_html_match.start(), custom_html_match.end(), custom_html_match.group(0))
        )

    div_parser = _StyledDivHtmlBlockParser(load_file)
    div_parser.feed(load_file)
    protected_blocks.extend(div_parser.protected_blocks)
    protected_blocks.sort(key=lambda item: (item[0], -(item[1] - item[0])))

    filtered_blocks: list[tuple[int, int, str]] = []
    used_end = 0
    for start, end, html_text in protected_blocks:
        if start < used_end:
            continue
        filtered_blocks.append((start, end, html_text))
        used_end = end

    return filtered_blocks


class _StyledDivHtmlBlockParser(HTMLParser):
    """装飾付きdivを親子ごとCustom HTMLとして保護するための簡易パーサーです。"""

    def __init__(self, html_text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.html_text = html_text
        self.protected_blocks: list[tuple[int, int, str]] = []
        self._line_offsets = _build_line_offsets(html_text)
        self._div_stack: list[tuple[int, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "div":
            return

        start = self._current_absolute_position()
        is_protected = _has_html_block_style(attrs)
        self._div_stack.append((start, is_protected))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "div" or not _has_html_block_style(attrs):
            return

        start = self._current_absolute_position()
        starttag_text = self.get_starttag_text()
        if starttag_text is None:
            return

        end = start + len(starttag_text)
        self.protected_blocks.append((start, end, self.html_text[start:end]))

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "div" or not self._div_stack:
            return

        start, is_protected = self._div_stack.pop()
        if not is_protected:
            return

        end_start = self._current_absolute_position()
        end_match = re.match(r"</div\s*>", self.html_text[end_start:], re.IGNORECASE)
        if not end_match:
            return

        end = end_start + len(end_match.group(0))
        self.protected_blocks.append((start, end, self.html_text[start:end]))

    def _current_absolute_position(self) -> int:
        line_number, column_number = self.getpos()
        return self._line_offsets[line_number - 1] + column_number


def _build_line_offsets(text: str) -> list[int]:
    offsets = [0]
    for line_match in re.finditer(r"\n", text):
        offsets.append(line_match.end())
    return offsets


def _has_html_block_style(attrs: list[tuple[str, str | None]]) -> bool:
    style_text = ""
    for name, value in attrs:
        if name.lower() == "style" and value:
            style_text = value.lower()
            break

    if not style_text:
        return False

    return any(keyword in style_text for keyword in HTML_DIV_HTML_BLOCK_STYLE_KEYWORDS)


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
