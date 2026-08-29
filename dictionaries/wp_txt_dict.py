"""WP-TXT記法の変換ルールをまとめるモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re

WP_TXT_EXTENSIONS: set[str] = {".wp_txt", ".wptxt"}

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
WP_TXT_TABLE_START = "[表]"
WP_TXT_TABLE_END = "[/表]"
WP_TXT_SEPARATOR_MARKER = "---"
