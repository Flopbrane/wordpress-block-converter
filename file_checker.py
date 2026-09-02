"""ファイル形式の確認とconverter選択を担当するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import csv
import json
import re
from collections.abc import Callable
from io import StringIO
from pathlib import Path

from converters.html_converter import convert_html_to_gutenberg
from converters.json_converter import convert_json_to_gutenberg
from converters.markdown_converter import convert_markdown_to_gutenberg
from converters.separated_values_converter import convert_separated_values_to_gutenberg
from converters.text_converter import convert_text_to_gutenberg
from converters.wp_txt_converter import convert_wp_txt_to_gutenberg
from dictionaries.html_dict import HTML_EXTENSIONS
from dictionaries.json_dict import JSON_EXTENSIONS
from dictionaries.markdown_dict import MARKDOWN_EXTENSIONS
from dictionaries.separated_values_dict import SEPARATED_VALUES_EXTENSIONS, SNIFF_DELIMITERS
from dictionaries.text_dict import TEXT_EXTENSIONS
from dictionaries.wp_txt_dict import (
    WP_TXT_CODE_START,
    WP_TXT_EXTENSIONS,
    WP_TXT_HEADING_PATTERN,
    WP_TXT_SUBHEADING_PATTERN,
    WP_TXT_TABLE_START,
)

SUPPORTED_FILE_TYPES: list[tuple[str, str]] = [
    ("対応ファイル", "*.txt *.wp_txt *.wptxt *.md *.markdown *.html *.htm *.wp_html *.csv *.ssv *.tsv *.psv *.pipesv *.json"),
    ("テキスト", "*.txt"),
    ("WP-TXT", "*.wp_txt *.wptxt"),
    ("Markdown", "*.md *.markdown"),
    ("HTML", "*.html *.htm *.wp_html"),
    ("区切り値ファイル", "*.csv *.ssv *.tsv *.psv *.pipesv"),
    ("JSON", "*.json"),
    ("すべてのファイル", "*.*"),
]

WORDPRESS_BLOCK_START_PATTERN: re.Pattern[str] = re.compile(r"^\s*<!--\s*wp:", re.IGNORECASE)
WORDPRESS_BLOCK_COMMENT_PATTERN: re.Pattern[str] = re.compile(r"<!--\s*/?wp:", re.IGNORECASE)
HTML_DOCTYPE_PATTERN: re.Pattern[str] = re.compile(r"^\s*<!DOCTYPE\s+html\b", re.IGNORECASE)
HTML_TAG_PATTERN: re.Pattern[str] = re.compile(r"<[a-zA-Z][a-zA-Z0-9:-]*(?:\s[^>]*)?>")
MARKDOWN_HEADING_PATTERN: re.Pattern[str] = re.compile(r"^\s{0,3}#{1,6}\s+\S")
CSV_MIN_COLUMNS = 2
CSV_MIN_ROWS = 2


def select_converter(load_file_path: str | Path, load_file: str | None = None) -> Callable[[str], str]:
    """load_file_pathと内容から、適切なconverterを返します。"""
    file_extension: str = Path(load_file_path).suffix.lower()
    if load_file is not None:
        content_converter: Callable[[str], str] | None = _select_converter_by_content(load_file, file_extension)
        if content_converter is not None:
            return content_converter

    if file_extension in WP_TXT_EXTENSIONS:
        return convert_wp_txt_to_gutenberg
    if file_extension in TEXT_EXTENSIONS:
        return convert_text_to_gutenberg
    if file_extension in MARKDOWN_EXTENSIONS:
        return convert_markdown_to_gutenberg
    if file_extension in HTML_EXTENSIONS:
        return convert_html_to_gutenberg
    if file_extension in JSON_EXTENSIONS:
        return convert_json_to_gutenberg
    if file_extension in SEPARATED_VALUES_EXTENSIONS:
        return lambda load_file_text: convert_separated_values_to_gutenberg(
            load_file_text,
            file_extension=file_extension,
        )

    supported_extensions: list[str] = sorted(
        TEXT_EXTENSIONS |
        WP_TXT_EXTENSIONS |
        MARKDOWN_EXTENSIONS |
        HTML_EXTENSIONS |
        JSON_EXTENSIONS |
        SEPARATED_VALUES_EXTENSIONS
    )
    raise ValueError(
        "対応していないファイル形式です。"
        f"対応拡張子: {', '.join(supported_extensions)}"
    )


def keep_existing_wordpress_html(load_file: str) -> str:
    """既存のWordPressブロックHTMLは二重変換せず、そのまま返します。"""
    return load_file


def _select_converter_by_content(
    load_file: str,
    file_extension: str,
) -> Callable[[str], str] | None:
    if _looks_like_existing_wordpress_html(load_file, file_extension):
        return keep_existing_wordpress_html
    if _looks_like_markdown(load_file):
        return convert_markdown_to_gutenberg
    if _looks_like_json(load_file):
        return convert_json_to_gutenberg
    if _looks_like_html(load_file):
        return convert_html_to_gutenberg
    if _looks_like_wp_txt(load_file):
        return convert_wp_txt_to_gutenberg
    if _looks_like_separated_values(load_file):
        return lambda load_file_text: convert_separated_values_to_gutenberg(
            load_file_text,
            file_extension=".csv",
        )

    return None


def _looks_like_existing_wordpress_html(load_file: str, file_extension: str) -> bool:
    first_line: str = _first_non_empty_line(load_file)
    if first_line and WORDPRESS_BLOCK_START_PATTERN.search(first_line):
        return True

    return file_extension == ".wp_html" and bool(WORDPRESS_BLOCK_COMMENT_PATTERN.search(load_file))


def _looks_like_markdown(load_file: str) -> bool:
    first_line = _first_non_empty_line(load_file)
    return bool(first_line and MARKDOWN_HEADING_PATTERN.match(first_line))


def _looks_like_html(load_file: str) -> bool:
    if WORDPRESS_BLOCK_COMMENT_PATTERN.search(load_file):
        return False

    first_line = _first_non_empty_line(load_file)
    if first_line and HTML_DOCTYPE_PATTERN.match(first_line):
        return True

    return bool(HTML_TAG_PATTERN.search(_sample_text(load_file)))


def _looks_like_json(load_file: str) -> bool:
    stripped_file = load_file.strip()
    if not stripped_file or stripped_file[0] not in "{[":
        return False

    try:
        json.loads(stripped_file)
    except json.JSONDecodeError:
        return False

    return True


def _looks_like_wp_txt(load_file: str) -> bool:
    for line in _non_empty_lines(load_file, limit=10):
        stripped_line = line.strip()
        if stripped_line in {WP_TXT_CODE_START, WP_TXT_TABLE_START}:
            return True
        if WP_TXT_HEADING_PATTERN.match(stripped_line) or WP_TXT_SUBHEADING_PATTERN.match(stripped_line):
            return True

    return False


def _looks_like_separated_values(load_file: str) -> bool:
    sample_lines = _non_empty_lines(load_file, limit=10)
    if len(sample_lines) < CSV_MIN_ROWS:
        return False

    sample = "\n".join(sample_lines)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=SNIFF_DELIMITERS)
    except csv.Error:
        return False

    reader = csv.reader(StringIO(sample), delimiter=dialect.delimiter)
    rows = [[cell.strip() for cell in row] for row in reader if any(cell.strip() for cell in row)]
    if len(rows) < CSV_MIN_ROWS:
        return False

    first_width = len(rows[0])
    if first_width < CSV_MIN_COLUMNS:
        return False

    return all(len(row) == first_width for row in rows[1:])


def _first_non_empty_line(load_file: str) -> str:
    lines = _non_empty_lines(load_file, limit=1)
    return lines[0] if lines else ""


def _non_empty_lines(load_file: str, limit: int) -> list[str]:
    lines: list[str] = []
    for line in load_file.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if not line.strip():
            continue

        lines.append(line)
        if len(lines) >= limit:
            break

    return lines


def _sample_text(load_file: str) -> str:
    return "\n".join(_non_empty_lines(load_file, limit=10))
