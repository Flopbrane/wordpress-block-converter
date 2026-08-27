"""区切り値ファイル変換用の辞書ファイルです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

SEPARATED_VALUES_EXTENSIONS: set[str] = {
    ".csv",
    ".ssv",
    ".tsv",
    ".psv",
    ".pipesv",
}

SEPARATED_VALUES_FORMAT_NAME = "separated_values"

COMMA_DELIMITER = ","
SEMICOLON_DELIMITER = ";"
TAB_DELIMITER = "\t"
PIPE_DELIMITER = "|"
SPACE_DELIMITER = " "

SNIFF_DELIMITERS = (
    COMMA_DELIMITER
    + SEMICOLON_DELIMITER
    + TAB_DELIMITER
    + PIPE_DELIMITER
)

DEFAULT_DELIMITER_BY_EXTENSION: dict[str, str] = {
    ".csv": COMMA_DELIMITER,
    ".ssv": SPACE_DELIMITER,
    ".tsv": TAB_DELIMITER,
    ".psv": PIPE_DELIMITER,
    ".pipesv": PIPE_DELIMITER,
}
