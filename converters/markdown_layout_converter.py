"""Markdown独自レイアウト記法をWordPress Gutenberg向けHTMLに変換します。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from blocks.heading import create_heading_block
from blocks.layout import (
    create_card_columns_block,
    create_cta_block,
    create_image_columns_block,
    create_media_text_block,
)
from blocks.paragraph import create_paragraph_block


def convert_markdown_layout_to_gutenberg(layout_name: str, layout_lines: list[str]) -> str:
    """:::name形式の独自レイアウト記法をGutenbergブロックへ変換します。"""
    layout_data = _parse_layout_lines(layout_lines)
    clean_layout_name = layout_name.strip().lower()

    if clean_layout_name in {"image_text_left", "image_text_right"}:
        media_position = "right" if clean_layout_name.endswith("_right") else "left"
        return create_media_text_block(
            image=layout_data.get("image", ""),
            alt=layout_data.get("alt", ""),
            title=layout_data.get("title", ""),
            text=layout_data.get("text", ""),
            media_position=media_position,
            media_width=_to_int(layout_data.get("width", "40"), 40),
        )

    if clean_layout_name in {"image_row", "image_row_2", "image_row_3"}:
        return create_image_columns_block(
            _collect_numbered_items(layout_data, "image", "alt"),
            gap=layout_data.get("gap", "24px"),
        )

    if clean_layout_name == "cta":
        return create_cta_block(
            title=layout_data.get("title", ""),
            text=layout_data.get("text", ""),
            button=layout_data.get("button", ""),
            url=layout_data.get("url", ""),
        )

    if clean_layout_name == "faq":
        return _create_faq_blocks(layout_data)

    if clean_layout_name in {"cards", "card_row"}:
        return create_card_columns_block(
            _collect_numbered_items(layout_data, "title", "text"),
            gap=layout_data.get("gap", "24px"),
        )

    return ""


def _parse_layout_lines(layout_lines: list[str]) -> dict[str, str]:
    layout_data: dict[str, str] = {}
    current_key = ""

    for line in layout_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip().lower()
            layout_data[current_key] = value.strip()
            continue

        if current_key and line.strip():
            layout_data[current_key] = f"{layout_data[current_key]}\n{line.strip()}"

    return layout_data


def _collect_numbered_items(
    layout_data: dict[str, str],
    first_key_name: str,
    second_key_name: str,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    indexes = sorted(
        {
            key.removeprefix(first_key_name)
            for key in layout_data
            if key.startswith(first_key_name) and key.removeprefix(first_key_name).isdigit()
        },
        key=int,
    )

    for index in indexes:
        items.append({
            first_key_name: layout_data.get(f"{first_key_name}{index}", ""),
            second_key_name: layout_data.get(f"{second_key_name}{index}", ""),
        })

    return items


def _create_faq_blocks(layout_data: dict[str, str]) -> str:
    blocks = []
    if layout_data.get("title", "").strip():
        blocks.append(create_heading_block(layout_data["title"], 2))

    indexes = sorted(
        {
            key[1:]
            for key in layout_data
            if key.startswith("q") and key[1:].isdigit()
        },
        key=int,
    )

    for index in indexes:
        question = layout_data.get(f"q{index}", "")
        answer = layout_data.get(f"a{index}", "")
        if question.strip():
            blocks.append(create_heading_block(question, 3))
        if answer.strip():
            blocks.append(create_paragraph_block(answer))

    return "\n\n".join(blocks)


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default
