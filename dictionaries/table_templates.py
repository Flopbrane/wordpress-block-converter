"""テーブルブロックの出力テンプレートを読み込むモジュールです。"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

TABLE_TEMPLATE_PATH = Path(__file__).resolve().parent / "table_block_templates.json"

_STANDARD_KEYS = {
    "block_open",
    "block_open_auto_layout",
    "block_close",
    "figure_open",
    "figure_close",
    "table_open",
    "table_open_auto_layout",
    "table_close",
    "section_open",
    "section_close",
    "row",
    "cell",
    "caption",
}
_SECTION_KEYS = {"head", "body", "foot"}


@lru_cache(maxsize=1)
def load_table_templates() -> dict[str, Any]:
    """UTF-8 JSONから検証済みのテーブル出力テンプレートを返します。"""
    load_file = json.loads(TABLE_TEMPLATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(load_file, dict):
        raise TypeError("table template root must be an object")

    standard_table = _required_dict(load_file, "standard_table")
    custom_html = _required_dict(load_file, "custom_html")
    missing_standard = _STANDARD_KEYS.difference(standard_table)
    if missing_standard:
        raise ValueError(
            "missing standard table templates: " + ", ".join(sorted(missing_standard))
        )

    for section_key in ("section_open", "section_close"):
        section_templates = _required_dict(standard_table, section_key)
        missing_sections = _SECTION_KEYS.difference(section_templates)
        if missing_sections:
            raise ValueError(
                f"missing {section_key} templates: "
                + ", ".join(sorted(missing_sections))
            )

    for key in ("block_open", "block_close"):
        if not isinstance(custom_html.get(key), str) or not custom_html[key]:
            raise ValueError(f"custom_html.{key} must be a non-empty string")

    _validate_placeholders(standard_table)
    return load_file


def _required_dict(load_file: dict[str, Any], key: str) -> dict[str, Any]:
    value = load_file.get(key)
    if not isinstance(value, dict):
        raise TypeError(f"{key} must be an object")
    return value


def _validate_placeholders(standard_table: dict[str, Any]) -> None:
    expected = {
        "row": {"{cells}"},
        "cell": {"{tag}", "{attributes}", "{content}"},
        "caption": {"{content}"},
    }
    for key, placeholders in expected.items():
        template = standard_table.get(key)
        if not isinstance(template, str) or not template:
            raise ValueError(f"standard_table.{key} must be a non-empty string")
        if any(placeholder not in template for placeholder in placeholders):
            raise ValueError(f"standard_table.{key} has missing placeholders")
