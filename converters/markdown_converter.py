"""markdownをwpに変換します"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, cast

from blocks.paragraph import create_paragraph_block
from dictionaries.html_dict import DIRECT_URL_RULES, EMBED_PROVIDER_RULES
from dictionaries.markdown_dict import (
    MARKDOWN_CODE_RULE,
    MARKDOWN_EMBED_RULE,
    MARKDOWN_HEADING_RULE,
    MARKDOWN_IMAGE_RULE,
    MARKDOWN_LIST_RULES,
    MARKDOWN_QUOTE_RULE,
    MARKDOWN_SEPARATOR_RULE,
    MARKDOWN_SHORTCODE_RULE,
    MARKDOWN_SPACER_RULE,
    MARKDOWN_TABLE_RULE,
)


def convert_markdown_to_gutenberg(load_file: str) -> str:
    """MarkdownをWordPress Gutenberg向けHTMLに変換します。"""
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_ordered: bool = False
    quote_lines: list[str] = []
    table_lines: list[str] = []
    code_lines: list[str] = []
    in_code_block: bool = False
    h2_section_active: bool = False

    for line in load_file.splitlines():
        stripped_line: str = line.strip()

        code_fence: str = str(MARKDOWN_CODE_RULE["fence"])
        if stripped_line.startswith(code_fence):
            if in_code_block:
                code_converter: Callable[[str], str] = cast(
                    Callable[[str], str],
                    MARKDOWN_CODE_RULE["converter"]
                    )
                blocks.append(code_converter("\n".join(code_lines)))
                code_lines = []
                in_code_block = False
            else:
                _flush_paragraph(blocks, paragraph_lines)
                paragraph_lines = []
                _flush_list(blocks, list_items, list_ordered)
                list_items = []
                _flush_quote(blocks, quote_lines)
                quote_lines = []
                _flush_table(blocks, table_lines, paragraph_lines)
                table_lines = []
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped_line and h2_section_active:
            _append_paragraph_blank_line(paragraph_lines)
            continue

        if not stripped_line:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            continue

        table_row_pattern = cast(re.Pattern[str], MARKDOWN_TABLE_RULE["row_pattern"])
        if table_row_pattern.match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            table_lines.append(stripped_line)
            continue

        heading_pattern: re.Pattern[str] = cast(re.Pattern[str], MARKDOWN_HEADING_RULE["pattern"])
        heading_match: re.Match[str] | None = heading_pattern.match(stripped_line)
        if heading_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            level = len(heading_match.group(1))
            heading_converter = cast(Callable[[str, int], str], MARKDOWN_HEADING_RULE["converter"])
            if level == 3:
                spacer_height = cast(int, MARKDOWN_HEADING_RULE["subheading_spacer_height"])
                spacer_converter = cast(Callable[[int], str], MARKDOWN_SPACER_RULE["converter"])
                blocks.append(spacer_converter(spacer_height))
                blocks.append(create_paragraph_block(f"**{heading_match.group(2)}**"))
                continue

            blocks.append(heading_converter(heading_match.group(2), level))
            if level == 1:
                h2_section_active = False
            elif level == 2:
                h2_section_active = True
            continue

        spacer_pattern: re.Pattern[str] = cast(re.Pattern[str], MARKDOWN_SPACER_RULE["pattern"])
        spacer_match: re.Match[str] | None = spacer_pattern.match(stripped_line)
        if spacer_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            default_height: int = cast(int, MARKDOWN_SPACER_RULE["default_height"])
            height = int(spacer_match.group(1) or default_height)
            spacer_converter = cast(Callable[[int], str], MARKDOWN_SPACER_RULE["converter"])
            blocks.append(spacer_converter(height))
            continue

        separator_pattern= cast(re.Pattern[str], MARKDOWN_SEPARATOR_RULE["pattern"])
        if separator_pattern.match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            separator_converter = cast(Callable[[], str], MARKDOWN_SEPARATOR_RULE["converter"])
            blocks.append(separator_converter())
            continue

        shortcode_pattern = cast(re.Pattern[str], MARKDOWN_SHORTCODE_RULE["pattern"])
        if shortcode_pattern.match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            shortcode_converter = cast(Callable[[str], str], MARKDOWN_SHORTCODE_RULE["converter"])
            blocks.append(shortcode_converter(stripped_line))
            continue

        image_pattern = cast(re.Pattern[str], MARKDOWN_IMAGE_RULE["pattern"])
        image_match = image_pattern.match(stripped_line)
        if image_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            image_converter = cast(Callable[[str, str], str], MARKDOWN_IMAGE_RULE["converter"])
            blocks.append(image_converter(image_match.group(2), image_match.group(1)))
            continue

        provider_info: dict[str, str | bool | None] | None = _find_embed_provider(stripped_line)
        embed_pattern = cast(re.Pattern[str], MARKDOWN_EMBED_RULE["pattern"])
        if provider_info and embed_pattern.match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            embed_converter: Callable[..., str] = cast(
                Callable[..., str], MARKDOWN_EMBED_RULE["converter"]
            )
            blocks.append(
                embed_converter(
                    stripped_line,
                    provider_info["providerNameSlug"],
                    embed_type=provider_info["type"],
                    responsive=provider_info["responsive"],
                    aspect=provider_info["aspect"],
                )
            )
            continue

        direct_url_block: str | None = _create_direct_url_block(stripped_line)
        if direct_url_block and embed_pattern.match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            blocks.append(direct_url_block)
            continue

        quote_pattern: re.Pattern[str] = cast("re.Pattern[str]", MARKDOWN_QUOTE_RULE["pattern"])
        quote_match: re.Match[str] | None = quote_pattern.match(line)
        if quote_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            quote_lines.append(quote_match.group(1).strip())
            continue

        unordered_rule = MARKDOWN_LIST_RULES["unordered"]
        ordered_rule = MARKDOWN_LIST_RULES["ordered"]
        unordered_pattern: re.Pattern[str] = cast("re.Pattern[str]", unordered_rule["pattern"])
        ordered_pattern: re.Pattern[str] = cast("re.Pattern[str]", ordered_rule["pattern"])
        unordered_match: re.Match[str] | None = unordered_pattern.match(line)
        ordered_match: re.Match[str] | None = ordered_pattern.match(line)
        if unordered_match or ordered_match:
            current_ordered: bool = ordered_match is not None
            if ordered_match is not None:
                item_text: str | Any = ordered_match.group(1)
            else:
                assert unordered_match is not None
                item_text = unordered_match.group(1)

            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            if list_items and list_ordered != current_ordered:
                _flush_list(blocks, list_items, list_ordered)
                list_items = []

            list_ordered = current_ordered
            list_items.append(item_text)
            continue

        _flush_list(blocks, list_items, list_ordered)
        list_items = []
        _flush_quote(blocks, quote_lines)
        quote_lines = []
        _flush_table(blocks, table_lines, paragraph_lines)
        table_lines = []
        paragraph_lines.append(stripped_line)

    if in_code_block:
        code_converter: Callable[[str], str] = cast(
            Callable[[str], str],
            MARKDOWN_CODE_RULE["converter"],
        )
        blocks.append(code_converter("\n".join(code_lines)))

    _flush_table(blocks, table_lines, paragraph_lines)
    _flush_paragraph(blocks, paragraph_lines)
    _flush_list(blocks, list_items, list_ordered)
    _flush_quote(blocks, quote_lines)

    return "\n\n".join(blocks)


def _flush_paragraph(blocks: list[str], paragraph_lines: list[str]) -> None:
    if paragraph_lines:
        blocks.append(create_paragraph_block(_build_paragraph_text(paragraph_lines)))


def _append_paragraph_blank_line(paragraph_lines: list[str]) -> None:
    if paragraph_lines and paragraph_lines[-1]:
        paragraph_lines.append("")


def _build_paragraph_text(paragraph_lines: list[str]) -> str:
    paragraph_groups: list[list[str]] = [[]]

    for line in paragraph_lines:
        if line:
            paragraph_groups[-1].append(line)
        elif paragraph_groups[-1]:
            paragraph_groups.append([])

    joined_groups = [
        " ".join(paragraph_group)
        for paragraph_group in paragraph_groups
        if paragraph_group
    ]
    return "\n\n".join(joined_groups)


def _flush_list(blocks: list[str], list_items: list[str], ordered: bool) -> None:
    if list_items:
        list_rule: dict[str, str | re.Pattern[str] | Callable[..., object] | bool] = (
            MARKDOWN_LIST_RULES["ordered"]
            if ordered else MARKDOWN_LIST_RULES["unordered"]
        )
        list_converter: Callable[..., str] = cast(Callable[..., str], list_rule["converter"])
        list_ordered: bool = cast(bool, list_rule["ordered"])
        use_html_block: bool = cast(bool, list_rule["use_html_block"])
        blocks.append(
            list_converter(
                list_items,
                ordered=list_ordered,
                use_html_block=use_html_block,
            )
        )


def _flush_quote(blocks: list[str], quote_lines: list[str]) -> None:
    if quote_lines:
        quote_converter = cast(Callable[[str], str], MARKDOWN_QUOTE_RULE["converter"])
        blocks.append(quote_converter(" ".join(quote_lines)))


def _flush_table(blocks: list[str], table_lines: list[str], paragraph_lines: list[str]) -> None:
    if not table_lines:
        return

    separator_pattern = cast(re.Pattern[str], MARKDOWN_TABLE_RULE["separator_pattern"])
    if len(table_lines) < 2 or not separator_pattern.match(table_lines[1]):
        paragraph_lines.extend(table_lines)
        table_lines.clear()
        return

    headers = _split_table_row(table_lines[0])
    rows = [_split_table_row(row) for row in table_lines[2:]]
    table_converter = cast(
        Callable[[list[str], list[list[str]]], str],
        MARKDOWN_TABLE_RULE["converter"]
        )
    blocks.append(table_converter(headers, rows))
    table_lines.clear()


def _split_table_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _find_embed_provider(url: str) -> dict[str, str | bool | None] | None:
    lower_url = url.lower()

    for compare_text, provider_info in EMBED_PROVIDER_RULES.items():
        if compare_text in lower_url:
            return provider_info

    return None


def _create_direct_url_block(url: str) -> str | None:
    lower_url = url.lower().split("?", 1)[0].split("#", 1)[0]

    for rule in DIRECT_URL_RULES.values():
        extensions = cast(list[str], rule["extensions"])
        if any(lower_url.endswith(file_extension) for file_extension in extensions):
            direct_url_converter = cast(Callable[[str], str], rule["converter"])
            return direct_url_converter(url)

    return None
