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

WP_TXT_HEADING_PATTERN: re.Pattern[str] = re.compile(
    r"^(?:【(.+?)】|\[Heading:(.+?)])$",
    re.IGNORECASE,
)
WP_TXT_SUBHEADING_PATTERN: re.Pattern[str] = re.compile(
    r"^(?:《(.+?)》|\[Subheading:(.+?)])$",
    re.IGNORECASE,
)
WP_TXT_UNORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^(?:・(.+)|[-*]\s+(.+))$")
WP_TXT_ORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(r"^\d+[.)]\s+(.+)$")
WP_TXT_QUOTE_PATTERN: re.Pattern[str] = re.compile(r"^>\s?(.+)$")
WP_TXT_SPACER_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:余白|Spacer):(\d+)]$",
    re.IGNORECASE,
)
WP_TXT_LINK_PATTERN: re.Pattern[str] = re.compile(
    r"\[(?:リンク|Link):([^|\]]+)\|(https?://[^\]\s]+)]",
    re.IGNORECASE,
)
WP_TXT_IMAGE_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:画像|Image):([^|\]]+)\|([^\]]*)]$",
    re.IGNORECASE,
)
WP_TXT_AUDIO_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:音声|Audio):(https?://[^\]\s]+)]$",
    re.IGNORECASE,
)
WP_TXT_VIDEO_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:動画|Video):(https?://[^\]\s]+)]$",
    re.IGNORECASE,
)
WP_TXT_FILE_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:ファイル|File):(https?://[^\]\s]+)]$",
    re.IGNORECASE,
)
WP_TXT_IMAGE_ROW_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:画像横並び|ImageRow):([^\]\n]+)]$",
    re.IGNORECASE,
)

WP_TXT_HTML_EXEC_START = "[HTML]"
WP_TXT_HTML_EXEC_END = "[/HTML]"
WP_TXT_BOLD_START = "[太字]"
WP_TXT_BOLD_END = "[/太字]"
WP_TXT_BOLD_START_EN = "[Bold]"
WP_TXT_BOLD_END_EN = "[/Bold]"
WP_TXT_NOTICE_START = "[注意]"
WP_TXT_NOTICE_END = "[/注意]"
WP_TXT_NOTICE_START_EN = "[Notice]"
WP_TXT_NOTICE_END_EN = "[/Notice]"
WP_TXT_SUPPLEMENT_START = "[補足]"
WP_TXT_SUPPLEMENT_END = "[/補足]"
WP_TXT_SUPPLEMENT_START_EN = "[Supplement]"
WP_TXT_SUPPLEMENT_END_EN = "[/Supplement]"
WP_TXT_STEPS_START = "[手順]"
WP_TXT_STEPS_END = "[/手順]"
WP_TXT_STEPS_START_EN = "[Steps]"
WP_TXT_STEPS_END_EN = "[/Steps]"
WP_TXT_IMAGE_ROW_END = "[/画像横並び]"
WP_TXT_IMAGE_ROW_END_EN = "[/ImageRow]"
WP_TXT_CODE_START = "[コード]"
WP_TXT_CODE_END = "[/コード]"
WP_TXT_CODE_START_EN = "[Code]"
WP_TXT_CODE_END_EN = "[/Code]"
WP_TXT_CODE_OUTPUT_MODE = "wp_code"
WP_TXT_CODE_OUTPUT_MODES: set[str] = {"wp_code", "styled_html"}
WP_TXT_EMPHASIS_CODE_START = "[強調コード]"
WP_TXT_EMPHASIS_CODE_END = "[/強調コード]"
WP_TXT_EMPHASIS_CODE_START_EN = "[EmphasisCode]"
WP_TXT_EMPHASIS_CODE_END_EN = "[/EmphasisCode]"
WP_TXT_LIST_START = "[リスト]"
WP_TXT_LIST_END = "[/リスト]"
WP_TXT_LIST_START_EN = "[List]"
WP_TXT_LIST_END_EN = "[/List]"
WP_TXT_ORDERED_LIST_START = "[番号リスト]"
WP_TXT_ORDERED_LIST_END = "[/番号リスト]"
WP_TXT_ORDERED_LIST_START_EN = "[OrderedList]"
WP_TXT_ORDERED_LIST_END_EN = "[/OrderedList]"
WP_TXT_PARAGRAPH_START = "<!-- wp:paragraph -->"
WP_TXT_PARAGRAPH_END = "<!-- /wp:paragraph -->"
WP_TXT_HTML_START = "<!-- wp:html -->"
WP_TXT_HTML_END = "<!-- /wp:html -->"
WP_TXT_BOX_START = "[囲い込み]"
WP_TXT_BOX_END = "[/囲い込み]"
WP_TXT_BOX_START_EN = "[Box]"
WP_TXT_BOX_END_EN = "[/Box]"
WP_TXT_TABLE_START = "[表]"
WP_TXT_TABLE_END = "[/表]"
WP_TXT_TABLE_START_EN = "[Table]"
WP_TXT_TABLE_END_EN = "[/Table]"
WP_TXT_SEPARATOR_MARKER = "---"
