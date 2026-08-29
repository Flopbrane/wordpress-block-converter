"""WP-TXT記法をWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import csv
import io
from html import escape

from blocks.code import create_code_block
from blocks.image import create_image_block
from blocks.list_block import create_list_block
from blocks.paragraph import create_paragraph_block
from blocks.quote import create_quote_block
from blocks.separator import create_separator_block
from blocks.spacer import create_spacer_block
from blocks.table import create_table_block_from_rows
from dictionaries.wp_txt_dict import (
    WP_TXT_CODE_END,
    WP_TXT_CODE_START,
    WP_TXT_HEADING_PATTERN,
    WP_TXT_IMAGE_PATTERN,
    WP_TXT_LINK_PATTERN,
    WP_TXT_ORDERED_LIST_PATTERN,
    WP_TXT_QUOTE_PATTERN,
    WP_TXT_SEPARATOR_MARKER,
    WP_TXT_SPACER_PATTERN,
    WP_TXT_SUBHEADING_PATTERN,
    WP_TXT_TABLE_END,
    WP_TXT_TABLE_START,
    WP_TXT_UNORDERED_LIST_PATTERN,
)


def convert_wp_txt_to_gutenberg(load_file: str) -> str:
    """WP-TXT記法をWordPress GutenbergブロックHTMLへ変換します。"""
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_ordered: bool = False
    quote_lines: list[str] = []
    code_lines: list[str] = []
    table_lines: list[str] = []
    in_code_block = False
    in_table_block = False

    for line in load_file.splitlines():
        stripped_line = line.strip()

        if in_code_block:
            if stripped_line == WP_TXT_CODE_END:
                blocks.append(create_code_block("\n".join(code_lines)))
                code_lines = []
                in_code_block = False
            else:
                code_lines.append(line)
            continue

        if in_table_block:
            if stripped_line == WP_TXT_TABLE_END:
                _flush_table(blocks, table_lines)
                table_lines = []
                in_table_block = False
            else:
                table_lines.append(line)
            continue

        if not stripped_line:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            continue

        if stripped_line == WP_TXT_CODE_START:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            in_code_block = True
            continue

        if stripped_line == WP_TXT_TABLE_START:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            in_table_block = True
            continue

        heading_match = WP_TXT_HEADING_PATTERN.match(stripped_line)
        if heading_match:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            blocks.append(_create_safe_heading_block(heading_match.group(1), 2))
            continue

        subheading_match = WP_TXT_SUBHEADING_PATTERN.match(stripped_line)
        if subheading_match:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            blocks.append(_create_safe_heading_block(subheading_match.group(1), 3))
            continue

        if stripped_line == WP_TXT_SEPARATOR_MARKER:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            blocks.append(create_separator_block())
            continue

        spacer_match = WP_TXT_SPACER_PATTERN.match(stripped_line)
        if spacer_match:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            blocks.append(create_spacer_block(int(spacer_match.group(1))))
            continue

        image_match = WP_TXT_IMAGE_PATTERN.match(stripped_line)
        if image_match:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            blocks.append(create_image_block(image_match.group(1), image_match.group(2)))
            continue

        unordered_list_match = WP_TXT_UNORDERED_LIST_PATTERN.match(stripped_line)
        if unordered_list_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            if list_items and list_ordered:
                _flush_list(blocks, list_items, list_ordered)
                list_items = []
            list_ordered = False
            list_items.append(unordered_list_match.group(1))
            continue

        ordered_list_match = WP_TXT_ORDERED_LIST_PATTERN.match(stripped_line)
        if ordered_list_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            if list_items and not list_ordered:
                _flush_list(blocks, list_items, list_ordered)
                list_items = []
            list_ordered = True
            list_items.append(ordered_list_match.group(1))
            continue

        quote_match = WP_TXT_QUOTE_PATTERN.match(stripped_line)
        if quote_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            quote_lines.append(quote_match.group(1))
            continue

        _flush_list(blocks, list_items, list_ordered)
        list_items = []
        _flush_quote(blocks, quote_lines)
        quote_lines = []
        paragraph_lines.append(_convert_wp_txt_links(stripped_line))

    if in_code_block and code_lines:
        blocks.append(create_code_block("\n".join(code_lines)))
    if in_table_block and table_lines:
        _flush_table(blocks, table_lines)

    _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
    return "\n\n".join(block for block in blocks if block)


def _flush_text_blocks(
    blocks: list[str],
    paragraph_lines: list[str],
    list_items: list[str],
    list_ordered: bool,
    quote_lines: list[str],
) -> None:
    _flush_paragraph(blocks, paragraph_lines)
    _flush_list(blocks, list_items, list_ordered)
    _flush_quote(blocks, quote_lines)


def _flush_paragraph(blocks: list[str], paragraph_lines: list[str]) -> None:
    if paragraph_lines:
        blocks.append(create_paragraph_block("\n".join(paragraph_lines), line_break_html="<br><br>"))


def _flush_list(blocks: list[str], list_items: list[str], list_ordered: bool) -> None:
    if list_items:
        blocks.append(create_list_block(list_items, ordered=list_ordered))


def _flush_quote(blocks: list[str], quote_lines: list[str]) -> None:
    if quote_lines:
        blocks.append(create_quote_block("\n".join(quote_lines)))


def _flush_table(blocks: list[str], table_lines: list[str]) -> None:
    rows = [_split_table_line(line) for line in table_lines if line.strip()]
    rows = [row for row in rows if row]
    if not rows:
        return

    headers = rows[0]
    body_rows = rows[1:]
    blocks.append(create_table_block_from_rows(headers, body_rows))


def _split_table_line(line: str) -> list[str]:
    clean_line = line.strip().strip("|")
    if not clean_line:
        return []

    delimiter = _detect_table_delimiter(clean_line)
    reader = csv.reader(io.StringIO(clean_line), delimiter=delimiter)
    return [cell.strip() for cell in next(reader, [])]


def _detect_table_delimiter(line: str) -> str:
    delimiter_counts = {
        "|": line.count("|"),
        "\t": line.count("\t"),
        ",": line.count(","),
    }
    return max(delimiter_counts, key=delimiter_counts.get)


def _convert_wp_txt_links(text: str) -> str:
    return WP_TXT_LINK_PATTERN.sub(r"[\1](\2)", text)


def _create_safe_heading_block(text: str, level: int) -> str:
    safe_text = escape(text.strip())
    return (
        f'<!-- wp:heading {{"level":{level}}} -->\n'
        f'<h{level} class="wp-block-heading">{safe_text}</h{level}>\n'
        "<!-- /wp:heading -->"
    )
