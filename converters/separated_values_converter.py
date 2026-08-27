"""CSV/SSV/TSV/PSVをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import csv
import shlex
from io import StringIO

from blocks.table import create_table_block_from_rows
from dictionaries.separated_values_dict import (
    DEFAULT_DELIMITER_BY_EXTENSION,
    SEPARATED_VALUES_EXTENSIONS,
    SNIFF_DELIMITERS,
    SPACE_DELIMITER,
)


def convert_separated_values_to_gutenberg(
    load_file: str,
    file_extension: str = ".csv",
) -> str:
    """区切り値ファイルをWordPress Gutenbergのtableブロックへ変換します。"""
    if file_extension not in SEPARATED_VALUES_EXTENSIONS:
        raise ValueError(f"対応していない区切り値ファイル形式です: {file_extension}")

    rows: list[list[str]] = _parse_separated_values(load_file, file_extension)
    if not rows:
        return ""

    rows = _normalize_row_width(rows)
    headers: list[str] = rows[0]
    body_rows: list[list[str]] = rows[1:]
    return create_table_block_from_rows(headers, body_rows)


def _parse_separated_values(load_file: str, file_extension: str) -> list[list[str]]:
    normalized_load_file: str = load_file.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized_load_file:
        return []

    delimiter: str = _detect_delimiter(normalized_load_file, file_extension)
    if delimiter == SPACE_DELIMITER:
        return _parse_space_separated_values(normalized_load_file)

    reader = csv.reader(StringIO(normalized_load_file), delimiter=delimiter)
    return [
        [cell.strip() for cell in row]
        for row in reader
        if any(cell.strip() for cell in row)
    ]


def _detect_delimiter(load_file: str, file_extension: str) -> str:
    sample = "\n".join(load_file.splitlines()[:10])

    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=SNIFF_DELIMITERS)
        return dialect.delimiter
    except csv.Error:
        pass

    return DEFAULT_DELIMITER_BY_EXTENSION.get(file_extension, ",")


def _parse_space_separated_values(load_file: str) -> list[list[str]]:
    rows: list[list[str]] = []

    for line in load_file.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue

        rows.append([cell.strip() for cell in shlex.split(stripped_line)])

    return rows


def _normalize_row_width(rows: list[list[str]]) -> list[list[str]]:
    max_width = max(len(row) for row in rows)
    return [row + [""] * (max_width - len(row)) for row in rows]
