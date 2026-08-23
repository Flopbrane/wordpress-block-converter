"""Markdown変換用の辞書ファイルです"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from collections.abc import Callable

from blocks.code import create_code_block
from blocks.embed import create_embed_block
from blocks.heading import create_heading_block
from blocks.image import create_image_block
from blocks.list_block import create_list_block
from blocks.quote import create_quote_block
from blocks.separator import create_separator_block
from blocks.shortcode import create_shortcode_block
from blocks.spacer import create_spacer_block
from blocks.table import create_table_block_from_rows

MARKDOWN_EXTENSIONS: set[str] = {".md", ".markdown"}

MARKDOWN_FORMAT_NAME = "markdown"

MARKDOWN_HEADING_MARK = "#"

MARKDOWN_UNORDERED_LIST_MARKS: set[str] = {"-", "*", "+"}

MARKDOWN_CODE_FENCE = "```"

MARKDOWN_HEADING_PATTERN: re.Pattern[str] = re.compile(r"^(#{1,6})\s+(.+)$")
MARKDOWN_UNORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\s*[-*+]\s+(.+)$")
MARKDOWN_ORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\s*\d+[.)]\s+(.+)$")
MARKDOWN_QUOTE_PATTERN: re.Pattern[str] = re.compile(r"^\s*>\s?(.+)$")
MARKDOWN_SPACER_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\[spacer(?::(\d+))?\]\s*$", re.IGNORECASE
    )
MARKDOWN_SEPARATOR_PATTERN: re.Pattern[str] = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
MARKDOWN_SHORTCODE_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*\[[A-Za-z0-9_-]+(?:\s+[^\]]*)?\]\s*$"
    )
MARKDOWN_IMAGE_PATTERN: re.Pattern[str] = re.compile(r"^!\[([^\]]*)\]\((https?://[^\s)]+)\)$")
MARKDOWN_TABLE_ROW_PATTERN: re.Pattern[str] = re.compile(r"^\s*\|(.+)\|\s*$")
MARKDOWN_TABLE_SEPARATOR_PATTERN: re.Pattern[str] = re.compile(r"^\s*\|?[\s:-]+\|[\s|:-]+\|?\s*$")
MARKDOWN_EMBED_URL_PATTERN: re.Pattern[str] = re.compile(r"^https?://[^\s<]+$", re.IGNORECASE)

MARKDOWN_HEADING_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "heading",
    "pattern": MARKDOWN_HEADING_PATTERN,
    "converter": create_heading_block,
    "subheading_spacer_height": 12,
}

MARKDOWN_LIST_RULES: dict[str, dict[str, str | re.Pattern[str] | Callable[..., object] | bool]] = {
    "unordered": {
        "name": "unordered_list",
        "pattern": MARKDOWN_UNORDERED_LIST_PATTERN,
        "converter": create_list_block,
        "ordered": False,
        "use_html_block": True,
    },
    "ordered": {
        "name": "ordered_list",
        "pattern": MARKDOWN_ORDERED_LIST_PATTERN,
        "converter": create_list_block,
        "ordered": True,
        "use_html_block": True,
    },
}

MARKDOWN_CODE_RULE: dict[str, str | Callable[..., object]] = {
    "name": "code",
    "fence": MARKDOWN_CODE_FENCE,
    "converter": create_code_block,
}

MARKDOWN_QUOTE_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "quote",
    "pattern": MARKDOWN_QUOTE_PATTERN,
    "converter": create_quote_block,
}

MARKDOWN_SPACER_RULE: dict[str, str | re.Pattern[str] | Callable[..., object] | int] = {
    "name": "spacer",
    "pattern": MARKDOWN_SPACER_PATTERN,
    "converter": create_spacer_block,
    "default_height": 40,
}

MARKDOWN_SEPARATOR_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "separator",
    "pattern": MARKDOWN_SEPARATOR_PATTERN,
    "converter": create_separator_block,
}

MARKDOWN_SHORTCODE_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "shortcode",
    "pattern": MARKDOWN_SHORTCODE_PATTERN,
    "converter": create_shortcode_block,
}

MARKDOWN_IMAGE_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "image",
    "pattern": MARKDOWN_IMAGE_PATTERN,
    "converter": create_image_block,
}

MARKDOWN_TABLE_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "table",
    "row_pattern": MARKDOWN_TABLE_ROW_PATTERN,
    "separator_pattern": MARKDOWN_TABLE_SEPARATOR_PATTERN,
    "converter": create_table_block_from_rows,
}

MARKDOWN_EMBED_RULE: dict[str, str | re.Pattern[str] | Callable[..., object]] = {
    "name": "embed",
    "pattern": MARKDOWN_EMBED_URL_PATTERN,
    "converter": create_embed_block,
}
