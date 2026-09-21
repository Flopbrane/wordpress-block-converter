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
from blocks.list_block import create_list_block, normalize_adjacent_list_blocks
from blocks.media import create_audio_block, create_file_block, create_video_block
from blocks.paragraph import create_paragraph_block
from blocks.quote import create_quote_block
from blocks.separator import create_separator_block
from blocks.spacer import create_spacer_block
from blocks.table import create_table_block_from_rows
from dictionaries.wp_txt_dict import (
    WP_TXT_AUDIO_PATTERN,
    WP_TXT_BOX_END,
    WP_TXT_BOX_END_EN,
    WP_TXT_BOX_START,
    WP_TXT_BOX_START_EN,
    WP_TXT_CODE_END,
    WP_TXT_CODE_END_EN,
    WP_TXT_CODE_OUTPUT_MODE,
    WP_TXT_CODE_OUTPUT_MODES,
    WP_TXT_CODE_START,
    WP_TXT_CODE_START_EN,
    WP_TXT_EMPHASIS_CODE_END,
    WP_TXT_EMPHASIS_CODE_END_EN,
    WP_TXT_EMPHASIS_CODE_START,
    WP_TXT_EMPHASIS_CODE_START_EN,
    WP_TXT_FILE_PATTERN,
    WP_TXT_HEADING_PATTERN,
    WP_TXT_HTML_END,
    WP_TXT_HTML_EXEC_END,
    WP_TXT_HTML_EXEC_START,
    WP_TXT_HTML_START,
    WP_TXT_IMAGE_PATTERN,
    WP_TXT_IMAGE_ROW_END,
    WP_TXT_IMAGE_ROW_END_EN,
    WP_TXT_IMAGE_ROW_PATTERN,
    WP_TXT_LINK_PATTERN,
    WP_TXT_LIST_END,
    WP_TXT_LIST_END_EN,
    WP_TXT_LIST_START,
    WP_TXT_LIST_START_EN,
    WP_TXT_NOTICE_END,
    WP_TXT_NOTICE_END_EN,
    WP_TXT_NOTICE_START,
    WP_TXT_NOTICE_START_EN,
    WP_TXT_ORDERED_LIST_END,
    WP_TXT_ORDERED_LIST_END_EN,
    WP_TXT_ORDERED_LIST_PATTERN,
    WP_TXT_ORDERED_LIST_START,
    WP_TXT_ORDERED_LIST_START_EN,
    WP_TXT_PARAGRAPH_END,
    WP_TXT_PARAGRAPH_START,
    WP_TXT_QUOTE_PATTERN,
    WP_TXT_SEPARATOR_MARKER,
    WP_TXT_SPACER_PATTERN,
    WP_TXT_STEPS_END,
    WP_TXT_STEPS_END_EN,
    WP_TXT_STEPS_START,
    WP_TXT_STEPS_START_EN,
    WP_TXT_SUBHEADING_PATTERN,
    WP_TXT_SUPPLEMENT_END,
    WP_TXT_SUPPLEMENT_END_EN,
    WP_TXT_SUPPLEMENT_START,
    WP_TXT_SUPPLEMENT_START_EN,
    WP_TXT_TABLE_END,
    WP_TXT_TABLE_END_EN,
    WP_TXT_TABLE_START,
    WP_TXT_TABLE_START_EN,
    WP_TXT_UNORDERED_LIST_PATTERN,
    WP_TXT_VIDEO_PATTERN,
)

PrewpBlockType = Literal[
    "text",
    "code",
    "emphasis_code",
    "list",
    "ordered_list",
    "paragraph",
    "html",
    "html_exec",
    "box",
    "notice",
    "notice_en",
    "supplement",
    "supplement_en",
    "steps",
    "image_row",
    "table",
]

TAG_PAIRS: dict[str, tuple[str, PrewpBlockType]] = {
    WP_TXT_CODE_START: (WP_TXT_CODE_END, "code"),
    WP_TXT_CODE_START_EN: (WP_TXT_CODE_END_EN, "code"),
    WP_TXT_EMPHASIS_CODE_START: (WP_TXT_EMPHASIS_CODE_END, "emphasis_code"),
    WP_TXT_EMPHASIS_CODE_START_EN: (WP_TXT_EMPHASIS_CODE_END_EN, "emphasis_code"),
    WP_TXT_LIST_START: (WP_TXT_LIST_END, "list"),
    WP_TXT_LIST_START_EN: (WP_TXT_LIST_END_EN, "list"),
    WP_TXT_ORDERED_LIST_START: (WP_TXT_ORDERED_LIST_END, "ordered_list"),
    WP_TXT_ORDERED_LIST_START_EN: (WP_TXT_ORDERED_LIST_END_EN, "ordered_list"),
    WP_TXT_PARAGRAPH_START: (WP_TXT_PARAGRAPH_END, "paragraph"),
    WP_TXT_HTML_START: (WP_TXT_HTML_END, "html"),
    WP_TXT_HTML_EXEC_START: (WP_TXT_HTML_EXEC_END, "html_exec"),
    WP_TXT_BOX_START: (WP_TXT_BOX_END, "box"),
    WP_TXT_BOX_START_EN: (WP_TXT_BOX_END_EN, "box"),
    WP_TXT_NOTICE_START: (WP_TXT_NOTICE_END, "notice"),
    WP_TXT_NOTICE_START_EN: (WP_TXT_NOTICE_END_EN, "notice_en"),
    WP_TXT_SUPPLEMENT_START: (WP_TXT_SUPPLEMENT_END, "supplement"),
    WP_TXT_SUPPLEMENT_START_EN: (WP_TXT_SUPPLEMENT_END_EN, "supplement_en"),
    WP_TXT_STEPS_START: (WP_TXT_STEPS_END, "steps"),
    WP_TXT_STEPS_START_EN: (WP_TXT_STEPS_END_EN, "steps"),
    WP_TXT_TABLE_START: (WP_TXT_TABLE_END, "table"),
    WP_TXT_TABLE_START_EN: (WP_TXT_TABLE_END_EN, "table"),
}
TAG_PAIRS_BY_LOWER: dict[str, tuple[str, PrewpBlockType]] = {
    start_tag.lower(): (end_tag, block_type)
    for start_tag, (end_tag, block_type) in TAG_PAIRS.items()
}
PREWP_TAG_PATTERN: re.Pattern[str] = re.compile(
    r"\[(?:画像横並び|ImageRow):[^\]\n]+]|"
    + "|".join(re.escape(tag) for tag in sorted(TAG_PAIRS, key=len, reverse=True)),
)


@dataclass(frozen=True)
class PrewpBlock:
    """PRE-WPを解析した中間ブロックです。"""

    block_type: PrewpBlockType
    text: str
    option: str = ""


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
        end_tag, block_type, option = _get_tag_definition(start_tag)
        body_start = tag_match.end()
        body_end = normalized_text.find(end_tag, body_start)

        if body_end == -1:
            _append_text_block(blocks, normalized_text[tag_match.start():])
            break

        block_text = _trim_marker_edges(normalized_text[body_start:body_end])
        blocks.append(PrewpBlock(block_type, block_text, option))
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
        elif prewp_block.block_type in {"html", "html_exec"}:
            blocks.append(_create_explicit_html_block(prewp_block.text))
        elif prewp_block.block_type == "box":
            blocks.append(_create_box_block(prewp_block.text))
        elif prewp_block.block_type == "notice":
            blocks.append(_create_note_box_block(prewp_block.text, "注意", "#fff4e5", "#c2410c"))
        elif prewp_block.block_type == "notice_en":
            blocks.append(_create_note_box_block(prewp_block.text, "Notice", "#fff4e5", "#c2410c"))
        elif prewp_block.block_type == "supplement":
            blocks.append(_create_note_box_block(prewp_block.text, "補足", "#eef6ff", "#0369a1"))
        elif prewp_block.block_type == "supplement_en":
            blocks.append(
                _create_note_box_block(prewp_block.text, "Supplement", "#eef6ff", "#0369a1")
            )
        elif prewp_block.block_type == "steps":
            blocks.append(_create_explicit_list_block(prewp_block.text, ordered=True))
        elif prewp_block.block_type == "image_row":
            blocks.append(_create_image_row_block(prewp_block.text, prewp_block.option))
        elif prewp_block.block_type == "table":
            _flush_table(blocks, prewp_block.text.splitlines())

    return normalize_adjacent_list_blocks("\n\n".join(block for block in blocks if block))


def _append_text_block(blocks: list[PrewpBlock], text: str) -> None:
    if text.strip():
        blocks.append(PrewpBlock("text", text))


def _get_tag_definition(start_tag: str) -> tuple[str, PrewpBlockType, str]:
    image_row_match = WP_TXT_IMAGE_ROW_PATTERN.match(start_tag)
    if image_row_match:
        if start_tag.lower().startswith("[imagerow:"):
            return WP_TXT_IMAGE_ROW_END_EN, "image_row", image_row_match.group(1).strip()
        return WP_TXT_IMAGE_ROW_END, "image_row", image_row_match.group(1).strip()

    end_tag, block_type = TAG_PAIRS_BY_LOWER[start_tag.lower()]
    return end_tag, block_type, ""


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
            list_items.append(_first_match_group(unordered_list_match))
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
        blocks.append(_create_safe_heading_block(_first_match_group(heading_match), 2))
        return True

    subheading_match = WP_TXT_SUBHEADING_PATTERN.match(stripped_line)
    if subheading_match:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(_create_safe_heading_block(_first_match_group(subheading_match), 3))
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

    media_block = _create_media_block(stripped_line)
    if media_block is not None:
        _flush_text_blocks(blocks, paragraph_lines, list_items, list_ordered, quote_lines)
        blocks.append(media_block)
        return True

    return False


def _create_media_block(stripped_line: str) -> str | None:
    image_match = WP_TXT_IMAGE_PATTERN.match(stripped_line)
    if image_match:
        return create_image_block(image_match.group(1), image_match.group(2))

    audio_match = WP_TXT_AUDIO_PATTERN.match(stripped_line)
    if audio_match:
        return create_audio_block(audio_match.group(1))

    video_match = WP_TXT_VIDEO_PATTERN.match(stripped_line)
    if video_match:
        return create_video_block(video_match.group(1))

    file_match = WP_TXT_FILE_PATTERN.match(stripped_line)
    if file_match:
        return create_file_block(file_match.group(1))

    return None


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


def _create_box_block(text: str) -> str:
    safe_text = "<br><br>".join(
        format_inline_text(paragraph.strip(), line_break_html="<br>")
        for paragraph in _split_explicit_paragraphs(text)
        if paragraph.strip()
    )
    style = (
        "border:1px solid #999;padding:16px;border-radius:8px;"
        "background-color:#f9f9f9;"
    )
    return f'<!-- wp:html -->\n<div style="{style}">{safe_text}</div>\n<!-- /wp:html -->'


def _create_note_box_block(
    text: str,
    label: str,
    background_color: str,
    border_color: str,
) -> str:
    safe_text = _format_box_text(text)
    safe_label = escape(label)
    style = (
        f"border-left:4px solid {border_color};padding:16px;"
        f"background-color:{background_color};"
    )
    html = f'<div style="{style}"><strong>{safe_label}</strong><br>{safe_text}</div>'
    return f"<!-- wp:html -->\n{html}\n<!-- /wp:html -->"


def _format_box_text(text: str) -> str:
    return "<br><br>".join(
        format_inline_text(paragraph.strip(), line_break_html="<br>")
        for paragraph in _split_explicit_paragraphs(text)
        if paragraph.strip()
    )


def _create_image_row_block(text: str, gap: str) -> str:
    images = [_parse_image_row_line(line) for line in text.splitlines() if line.strip()]
    image_tags = "\n".join(
        f'<img src="{safe_src}" alt="{safe_alt}" style="max-width:100%;height:auto;">'
        for safe_src, safe_alt in images
    )
    safe_gap = escape(gap or "24px", quote=True)
    html = (
        f'<div style="display:flex;gap:{safe_gap};align-items:flex-start;flex-wrap:wrap;">\n'
        f"{image_tags}\n"
        "</div>"
    )
    return f"<!-- wp:html -->\n{html}\n<!-- /wp:html -->"


def _parse_image_row_line(line: str) -> tuple[str, str]:
    stripped_line = line.strip()
    image_match = WP_TXT_IMAGE_PATTERN.match(stripped_line)
    if image_match:
        first_value = image_match.group(1)
        second_value = image_match.group(2)
        if second_value.startswith(("http://", "https://")):
            return escape(second_value, quote=True), escape(first_value, quote=True)
        return escape(first_value, quote=True), escape(second_value, quote=True)
    return escape(stripped_line, quote=True), ""


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


def _first_match_group(match: re.Match[str]) -> str:
    return next(group for group in match.groups() if group is not None)


def _create_safe_heading_block(text: str, level: int) -> str:
    safe_text = escape(text.strip())
    return (
        f'<!-- wp:heading {{"level":{level}}} -->\n'
        f'<h{level} class="wp-block-heading">{safe_text}</h{level}>\n'
        "<!-- /wp:heading -->"
    )
