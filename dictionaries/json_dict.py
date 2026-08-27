"""JSON変換用の辞書ファイルです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

JSON_EXTENSIONS: set[str] = {".json"}

JSON_FORMAT_NAME = "json"

SECTION_KEYS: tuple[str, ...] = ("sections", "blocks", "content")
TEXT_KEYS: tuple[str, ...] = ("text", "body", "description")
TITLE_KEYS: tuple[str, ...] = ("title", "heading")
LIST_KEYS: tuple[str, ...] = ("items", "list")
FAQ_KEYS: tuple[str, ...] = ("faq", "faqs")
TABLE_KEYS: tuple[str, ...] = ("table", "rows")
