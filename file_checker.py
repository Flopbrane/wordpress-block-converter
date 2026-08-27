"""ファイル形式の確認とconverter選択を担当するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from converters.html_converter import convert_html_to_gutenberg
from converters.json_converter import convert_json_to_gutenberg
from converters.markdown_converter import convert_markdown_to_gutenberg
from converters.separated_values_converter import convert_separated_values_to_gutenberg
from converters.text_converter import convert_text_to_gutenberg
from dictionaries.html_dict import HTML_EXTENSIONS
from dictionaries.json_dict import JSON_EXTENSIONS
from dictionaries.markdown_dict import MARKDOWN_EXTENSIONS
from dictionaries.separated_values_dict import SEPARATED_VALUES_EXTENSIONS
from dictionaries.text_dict import TEXT_EXTENSIONS

SUPPORTED_FILE_TYPES: list[tuple[str, str]] = [
    ("対応ファイル", "*.txt *.md *.markdown *.html *.htm *.csv *.ssv *.tsv *.psv *.pipesv *.json"),
    ("テキスト", "*.txt"),
    ("Markdown", "*.md *.markdown"),
    ("HTML", "*.html *.htm"),
    ("区切り値ファイル", "*.csv *.ssv *.tsv *.psv *.pipesv"),
    ("JSON", "*.json"),
    ("すべてのファイル", "*.*"),
]


def select_converter(load_file_path: str | Path) -> Callable[[str], str]:
    """load_file_pathの拡張子に合うconverterを返します。"""
    file_extension = Path(load_file_path).suffix.lower()

    if file_extension in TEXT_EXTENSIONS:
        return convert_text_to_gutenberg
    if file_extension in MARKDOWN_EXTENSIONS:
        return convert_markdown_to_gutenberg
    if file_extension in HTML_EXTENSIONS:
        return convert_html_to_gutenberg
    if file_extension in JSON_EXTENSIONS:
        return convert_json_to_gutenberg
    if file_extension in SEPARATED_VALUES_EXTENSIONS:
        return lambda load_file: convert_separated_values_to_gutenberg(
            load_file,
            file_extension=file_extension,
        )

    supported_extensions: list[str] = sorted(
        TEXT_EXTENSIONS |
        MARKDOWN_EXTENSIONS |
        HTML_EXTENSIONS |
        JSON_EXTENSIONS |
        SEPARATED_VALUES_EXTENSIONS
    )
    raise ValueError(
        "対応していないファイル形式です。"
        f"対応拡張子: {', '.join(supported_extensions)}"
    )
