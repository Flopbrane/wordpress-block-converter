"""WP-TXT/PRE-WP記法をWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from html import escape
from typing import Literal

from blocks.code import create_code_block, create_emphasis_code_block
from blocks.image import create_image_block
from blocks.inline import format_inline_text
from blocks.list_block import create_list_block
from blocks.paragraph import create_paragraph_block
from blocks.quote import create_quote_block
from blocks.separator import create_separator_block
from blocks.spacer import create_spacer_block
from blocks.table import create_table_block_from_rows
from dictionaries.wp_txt_dict import (
    WP_TXT_CODE_END,
    WP_TXT_CODE_OUTPUT_MODE,
    WP_TXT_CODE_OUTPUT_MODES,
    WP_TXT_CODE_START,
    WP_TXT_EMPHASIS_CODE_END,
    WP_TXT_EMPHASIS_CODE_START,
    WP_TXT_HEADING_PATTERN,
    WP_TXT_HTML_END,
    WP_TXT_HTML_START,
    WP_TXT_IMAGE_PATTERN,
    WP_TXT_LINK_PATTERN,
    WP_TXT_LIST_END,
    WP_TXT_LIST_START,
    WP_TXT_ORDERED_LIST_END,
    WP_TXT_ORDERED_LIST_PATTERN,
    WP_TXT_ORDERED_LIST_START,
    WP_TXT_PARAGRAPH_END,
    WP_TXT_PARAGRAPH_START,
    WP_TXT_QUOTE_PATTERN,
    WP_TXT_SEPARATOR_MARKER,
    WP_TXT_SPACER_PATTERN,
    WP_TXT_SUBHEADING_PATTERN,
    WP_TXT_TABLE_END,
    WP_TXT_TABLE_START,
    WP_TXT_UNORDERED_LIST_PATTERN,
)

PrewpBlockType = Literal[
    "text",
    "code",
    "emphasis_code",
    "list",
    "ordered_list",
    "paragraph",
    "html",
    "table",
]

TAG_PAIRS: dict[str, tuple[str, PrewpBlockType]] = {
    WP_TXT_CODE_START: (WP_TXT_CODE_END, "code"),
    WP_TXT_EMPHASIS_CODE_START: (WP_TXT_EMPHASIS_CODE_END, "emphasis_code"),
    WP_TXT_LIST_START: (WP_TXT_LIST_END, "list"),
    WP_TXT_ORDERED_LIST_START: (WP_TXT_ORDERED_LIST_END, "ordered_list"),
    WP_TXT_PARAGRAPH_START: (WP_TXT_PARAGRAPH_END, "paragraph"),
    WP_TXT_HTML_START: (WP_TXT_HTML_END, "html"),
    WP_TXT_TABLE_START: (WP_TXT_TABLE_END, "table"),
}
PREWP_TAG_PATTERN: re.Pattern[str] = re.compile(
    "|".join(re.escape(tag) for tag in sorted(TAG_PAIRS, key=len, reverse=True))
)


@dataclass(frozen=True)
class PrewpBlock:
    """PRE-WPを解析した中間ブロックです。"""

    block_type: PrewpBlockType
    text: str


def convert_wp_txt_to_gutenberg(load_file: str) -> str:
    """WP-TXT/PRE-WP記法をWordPress GutenbergブロックHTMLへ変換します。"""
    return render_wordpress(parse_prewp(load_file))


def parse_prewp(text: str) -> list[PrewpBlock]:
    """PRE-WP文字列をタグ付き中間構造へ変換します。"""
    normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks: list[PrewpBlock] = []
    current_position = 0

    while current_position < len(normalized_text):
        tag_match = PREWP_TAG_PATTERN.search(normalized_text, current_position)
        if tag_match is None:
            _append_text_block(blocks, normalized_text[current_position:])
            break

        _append_text_block(blocks, normalized_text[current_position:tag_match.start()])
        start_tag = tag_match.group(0)
        end_tag, block_type = TAG_PAIRS[start_tag]
        body_start = tag_match.end()
        body_end = normalized_text.find(end_tag, body_start)

        if body_end == -1:
            _append_text_block(blocks, normalized_text[tag_match.start():])
            break

        block_text = _trim_marker_edges(normalized_text[body_start:body_end])
        blocks.append(PrewpBlock(block_type, block_text))
        current_position = body_end + len(end_tag)

    return [block for block in blocks if block.text.strip()]


def render_wordpress(document: list[PrewpBlock]) -> str:
    """PRE-WP中間構造をWordPress Gutenberg HTMLへ描画します。"""
    blocks: list[str] = []
    for prewp_block in document:
        if prewp_block.block_type == "text":
            blocks.extend(_render_text_blocks(prewp_block.text))
        elif prewp_block.block_type == "code":
            blocks.append(_create_normal_code_block(prewp_block.text))
        elif prewp_block.block_type == "emphasis_code":
            blocks.append(create_emphasis_code_block(prewp_block.text))
        elif prewp_block.block_type == "list":
            blocks.append(_create_explicit_list_block(prewp_block.text, ordered=False))
        elif prewp_block.block_type == "ordered_list":
            blocks.append(_create_explicit_list_block(prewp_block.text, ordered=True))
        elif prewp_block.block_type == "paragraph":
            blocks.append(_create_explicit_paragraph_block(prewp_block.text))
        elif prewp_block.block_type == "html":
            blocks.append(_create_explicit_html_block(prewp_block.text))
        elif prewp_block.block_type == "table":
            _flush_table(blocks, prewp_block.text.splitlines())

    return "\n\n".join(block for block in blocks if block)


def _append_text_block(blocks: list[PrewpBlock], text: str) -> None:
    if text.strip():
        blocks.append(PrewpBlock("text", text))


def _trim_marker_edges(text: str) -> str:
    """タグ直後・直前の改行だけを落とし、コード本文の空白は残します。"""
    return text.removeprefix("\n").removesuffix("\n")


def _render_text_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_ordered = False
    quote_lines: list[str] = []

    for line in text.splitlines():
        stripped_line = line.strip()

        if not stripped_line:
            _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
            paragraph_lines = []
            list_items = []
            quote_lines = []
            continue

        if _append_standalone_block(
            blocks,
            stripped_line,
            paragraph_lines,
            list_items,
            list_ordered,
            quote_lines,
        ):
            paragraph_lines = []
            list_items = []
            quote_lines = []
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
            paragraph_lines, list_items = _prepare_quote_block(
                blocks,
                paragraph_lines,
                list_items,
                list_ordered,
            )
            quote_lines.append(quote_match.group(1))
            continue

        list_items, quote_lines = _prepare_paragraph_line(
            blocks,
            list_items,
            list_ordered,
            quote_lines,
        )
        paragraph_lines.append(_convert_wp_txt_links(stripped_line))

    _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
    return blocks


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _append_standalone_block(
    blocks: list[str],
    stripped_line: str,
    paragraph_lines: list[str],
    list_items: list[str],
    list_ordered: bool,
    quote_lines: list[str],
) -> bool:
    heading_match = WP_TXT_HEADING_PATTERN.match(stripped_line)
    if heading_match:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(_create_safe_heading_block(heading_match.group(1), 2))
        return True

    subheading_match = WP_TXT_SUBHEADING_PATTERN.match(stripped_line)
    if subheading_match:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(_create_safe_heading_block(subheading_match.group(1), 3))
        return True

    if stripped_line == WP_TXT_SEPARATOR_MARKER:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(create_separator_block())
        return True

    spacer_match = WP_TXT_SPACER_PATTERN.match(stripped_line)
    if spacer_match:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(create_spacer_block(int(spacer_match.group(1))))
        return True

    image_match = WP_TXT_IMAGE_PATTERN.match(stripped_line)
    if image_match:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(create_image_block(image_match.group(1), image_match.group(2)))
        return True

    return False


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


def _prepare_quote_block(
    blocks: list[str],
    paragraph_lines: list[str],
    list_items: list[str],
    list_ordered: bool,
) -> tuple[list[str], list[str]]:
    _flush_paragraph(blocks, paragraph_lines)
    _flush_list(blocks, list_items, list_ordered)
    return [], []


def _prepare_paragraph_line(
    blocks: list[str],
    list_items: list[str],
    list_ordered: bool,
    quote_lines: list[str],
) -> tuple[list[str], list[str]]:
    _flush_list(blocks, list_items, list_ordered)
    _flush_quote(blocks, quote_lines)
    return [], []


def _flush_paragraph(blocks: list[str], paragraph_lines: list[str]) -> None:
    if paragraph_lines:
        blocks.append(create_paragraph_block("\n".join(paragraph_lines), line_break_html="<br>"))


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


def _create_normal_code_block(text: str) -> str:
    if WP_TXT_CODE_OUTPUT_MODE not in WP_TXT_CODE_OUTPUT_MODES:
        return create_code_block(text)
    if WP_TXT_CODE_OUTPUT_MODE == "styled_html":
        return create_emphasis_code_block(text)
    return create_code_block(text)


def _create_explicit_list_block(text: str, ordered: bool) -> str:
    items = [line.strip() for line in text.splitlines() if line.strip()]
    return create_list_block(items, ordered=ordered)


def _create_explicit_paragraph_block(text: str) -> str:
    safe_text = "<br><br>".join(
        format_inline_text(paragraph.strip(), line_break_html="<br>")
        for paragraph in _split_explicit_paragraphs(text)
        if paragraph.strip()
    )
    return f"<!-- wp:paragraph -->\n<p>{safe_text}</p>\n<!-- /wp:paragraph -->"


def _split_explicit_paragraphs(text: str) -> list[str]:
    return re.split(r"\n[ \t]*\n+", text.strip())


def _create_explicit_html_block(text: str) -> str:
    return f"<!-- wp:html -->\n{text.strip()}\n<!-- /wp:html -->"


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
    return max(delimiter_counts, key=lambda delimiter: delimiter_counts[delimiter])


def _convert_wp_txt_links(text: str) -> str:
    return WP_TXT_LINK_PATTERN.sub(r"[\1](\2)", text)


def _create_safe_heading_block(text: str, level: int) -> str:
    safe_text = escape(text.strip())
    return (
        f'<!-- wp:heading {{"level":{level}}} -->\n'
        f'<h{level} class="wp-block-heading">{safe_text}</h{level}>\n'
        "<!-- /wp:heading -->"
    )
