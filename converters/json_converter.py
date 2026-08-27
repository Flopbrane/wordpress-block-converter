"""JSONをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import json
from typing import Any

from blocks.heading import create_heading_block
from blocks.list_block import create_list_block
from blocks.paragraph import create_paragraph_block
from blocks.table import create_table_block_from_rows
from dictionaries.json_dict import (
    FAQ_KEYS,
    LIST_KEYS,
    SECTION_KEYS,
    TABLE_KEYS,
    TEXT_KEYS,
    TITLE_KEYS,
)


def convert_json_to_gutenberg(load_file: str) -> str:
    """JSON構造データをWordPress Gutenberg向けHTMLへ変換します。"""
    try:
        json_data = json.loads(load_file)
    except json.JSONDecodeError as error:
        raise ValueError(f"JSONの読み込みに失敗しました: {error}") from error

    blocks: list[str] = []
    _append_json_blocks(blocks, json_data, heading_level=1)
    return "\n\n".join(blocks)


def _append_json_blocks(blocks: list[str], value: Any, heading_level: int = 2) -> None:
    if isinstance(value, dict):
        _append_dict_blocks(blocks, value, heading_level)
        return

    if isinstance(value, list):
        _append_list_value_blocks(blocks, value, heading_level)
        return

    if value is not None:
        blocks.append(create_paragraph_block(str(value)))


def _append_dict_blocks(blocks: list[str], data: dict[str, Any], heading_level: int) -> None:
    title = _get_first_text_value(data, TITLE_KEYS)
    if title:
        blocks.append(create_heading_block(title, heading_level))

    text = _get_first_text_value(data, TEXT_KEYS)
    if text:
        blocks.append(create_paragraph_block(text))

    _append_items_block(blocks, data)
    _append_table_block(blocks, data)
    _append_faq_blocks(blocks, data, heading_level + 1)

    for key in SECTION_KEYS:
        sections = data.get(key)
        if isinstance(sections, list):
            for section in sections:
                _append_json_blocks(blocks, section, heading_level + 1)


def _append_items_block(blocks: list[str], data: dict[str, Any]) -> None:
    for key in LIST_KEYS:
        items = data.get(key)
        if not isinstance(items, list):
            continue

        clean_items = [str(item) for item in items if _is_simple_value(item)]
        if clean_items:
            ordered = bool(data.get("ordered", False))
            blocks.append(create_list_block(clean_items, ordered=ordered))
        return


def _append_table_block(blocks: list[str], data: dict[str, Any]) -> None:
    for key in TABLE_KEYS:
        table_data = data.get(key)
        table_block = _create_table_from_json_value(table_data)
        if table_block:
            blocks.append(table_block)
            return


def _append_faq_blocks(blocks: list[str], data: dict[str, Any], heading_level: int) -> None:
    for key in FAQ_KEYS:
        faq_items = data.get(key)
        if not isinstance(faq_items, list):
            continue

        for faq_item in faq_items:
            if not isinstance(faq_item, dict):
                continue

            question = _get_first_text_value(faq_item, ("question", "q", "title", "heading"))
            answer = _get_first_text_value(faq_item, ("answer", "a", "text", "body"))
            if question:
                blocks.append(create_heading_block(question, min(heading_level, 5)))
            if answer:
                blocks.append(create_paragraph_block(answer))
        return


def _append_list_value_blocks(blocks: list[str], values: list[Any], heading_level: int) -> None:
    if not values:
        return

    if all(isinstance(item, dict) for item in values):
        table_block = _create_table_from_dict_rows(values)
        if table_block:
            blocks.append(table_block)
            return

    if all(_is_simple_value(item) for item in values):
        blocks.append(create_list_block([str(item) for item in values]))
        return

    for item in values:
        _append_json_blocks(blocks, item, heading_level)


def _create_table_from_json_value(value: Any) -> str:
    if isinstance(value, dict):
        headers = value.get("headers")
        rows = value.get("rows")
        if isinstance(headers, list) and isinstance(rows, list):
            return create_table_block_from_rows(
                [str(header) for header in headers],
                [[str(cell) for cell in row] for row in rows if isinstance(row, list)],
            )

    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return _create_table_from_dict_rows(value)

    return ""


def _create_table_from_dict_rows(rows: list[Any]) -> str:
    dict_rows = [row for row in rows if isinstance(row, dict)]
    if not dict_rows:
        return ""

    headers: list[str] = []
    for row in dict_rows:
        for key in row.keys():
            if key not in headers:
                headers.append(str(key))

    body_rows = [
        [str(row.get(header, "")) for header in headers]
        for row in dict_rows
    ]
    return create_table_block_from_rows(headers, body_rows)


def _get_first_text_value(data: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = data.get(key)
        if _is_simple_value(value):
            return str(value).strip()

    return ""


def _is_simple_value(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool))
