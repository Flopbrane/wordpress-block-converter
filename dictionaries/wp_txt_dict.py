"""WP-TXT記法の変換ルールをまとめるモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re

PREWP_TXT_EXTENSIONS: set[str] = {".prewp_txt"}
WP_TXT_EXTENSIONS: set[str] = {".wp_txt", ".wptxt"} | PREWP_TXT_EXTENSIONS

WP_TXT_HEADING_PATTERN: re.Pattern[str] = re.compile(r"^【(.+?)】$")
WP_TXT_SUBHEADING_PATTERN: re.Pattern[str] = re.compile(r"^《(.+?)》$")
WP_TXT_UNORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^・(.+)$")
WP_TXT_ORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\d+[.)]\s+(.+)$")
WP_TXT_QUOTE_PATTERN: re.Pattern[str] = re.compile(r"^>\s?(.+)$")
WP_TXT_SPACER_PATTERN: re.Pattern[str] = re.compile(r"^\[余白:(\d+)]$")
WP_TXT_LINK_PATTERN: re.Pattern[str] = re.compile(r"\[リンク:([^|\]]+)\|(https?://[^\]\s]+)]")
WP_TXT_IMAGE_PATTERN: re.Pattern[str] = re.compile(r"^\[画像:([^|\]]+)\|([^\]]*)]$")

WP_TXT_CODE_START = "[コード]"
WP_TXT_CODE_END = "[/コード]"
WP_TXT_CODE_OUTPUT_MODE = "wp_code"
WP_TXT_CODE_OUTPUT_MODES: set[str] = {"wp_code", "styled_html"}
WP_TXT_EMPHASIS_CODE_START = "[強調コード]"
WP_TXT_EMPHASIS_CODE_END = "[/強調コード]"
WP_TXT_TABLE_START = "[表]"
WP_TXT_TABLE_END = "[/表]"
WP_TXT_SEPARATOR_MARKER = "---"
