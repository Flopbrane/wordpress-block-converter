"""prewp_txt向けlint処理です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from dictionaries.wp_txt_dict import (
    WP_TXT_BOLD_END,
    WP_TXT_BOLD_END_EN,
    WP_TXT_BOLD_START,
    WP_TXT_BOLD_START_EN,
    WP_TXT_BOX_END,
    WP_TXT_BOX_END_EN,
    WP_TXT_BOX_START,
    WP_TXT_BOX_START_EN,
    WP_TXT_CODE_END,
    WP_TXT_CODE_END_EN,
    WP_TXT_CODE_START,
    WP_TXT_CODE_START_EN,
    WP_TXT_EMPHASIS_CODE_END,
    WP_TXT_EMPHASIS_CODE_END_EN,
    WP_TXT_EMPHASIS_CODE_START,
    WP_TXT_EMPHASIS_CODE_START_EN,
    WP_TXT_HTML_END,
    WP_TXT_HTML_EXEC_END,
    WP_TXT_HTML_EXEC_START,
    WP_TXT_HTML_START,
    WP_TXT_IMAGE_ROW_END,
    WP_TXT_IMAGE_ROW_END_EN,
    WP_TXT_LIST_END,
    WP_TXT_LIST_END_EN,
    WP_TXT_LIST_START,
    WP_TXT_LIST_START_EN,
    WP_TXT_NOTICE_END,
    WP_TXT_NOTICE_END_EN,
    WP_TXT_NOTICE_START,
    WP_TXT_NOTICE_START_EN,
    WP_TXT_ORDERED_LIST_END,
    WP_TXT_ORDERED_LIST_END_EN,
    WP_TXT_ORDERED_LIST_START,
    WP_TXT_ORDERED_LIST_START_EN,
    WP_TXT_PARAGRAPH_END,
    WP_TXT_PARAGRAPH_START,
    WP_TXT_STEPS_END,
    WP_TXT_STEPS_END_EN,
    WP_TXT_STEPS_START,
    WP_TXT_STEPS_START_EN,
    WP_TXT_SUPPLEMENT_END,
    WP_TXT_SUPPLEMENT_END_EN,
    WP_TXT_SUPPLEMENT_START,
    WP_TXT_SUPPLEMENT_START_EN,
    WP_TXT_TABLE_END,
    WP_TXT_TABLE_END_EN,
    WP_TXT_TABLE_START,
    WP_TXT_TABLE_START_EN,
)

LintLevel = Literal["error", "warning"]

VALID_LINK_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:リンク|Link):([^|\]\n]+)\|(https?://[^\]\s]+)]$",
    re.IGNORECASE,
)
VALID_IMAGE_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:画像|Image):(https?://[^|\]\s]+)\|([^\]\n]+)]$",
    re.IGNORECASE,
)
VALID_AUDIO_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:音声|Audio):https?://[^\]\s]+]$",
    re.IGNORECASE,
)
VALID_VIDEO_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:動画|Video):https?://[^\]\s]+]$",
    re.IGNORECASE,
)
VALID_FILE_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"^\[(?:ファイル|File):https?://[^\]\s]+]$",
    re.IGNORECASE,
)
SPACER_MARKER_PATTERN: re.Pattern[str] = re.compile(
    r"\[(?:余白|Spacer):([^\]\n]+)]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LintIssue:
    """prewp_txtのlint結果です。"""

    level: LintLevel
    line: int
    message: str
    hint: str


def lint_prewp_txt(load_file: str) -> list[LintIssue]:
    """prewp_txtのマーカー崩れを検出します。"""
    issues: list[LintIssue] = []
    _check_marker_pair(load_file, WP_TXT_BOX_START, WP_TXT_BOX_END, "囲い込み", issues)
    _check_marker_pair(load_file, WP_TXT_BOX_START_EN, WP_TXT_BOX_END_EN, "Box", issues)
    _check_marker_pair(load_file, WP_TXT_BOLD_START, WP_TXT_BOLD_END, "太字", issues)
    _check_marker_pair(load_file, WP_TXT_BOLD_START_EN, WP_TXT_BOLD_END_EN, "Bold", issues)
    _check_marker_pair(load_file, WP_TXT_CODE_START, WP_TXT_CODE_END, "コード", issues)
    _check_marker_pair(load_file, WP_TXT_CODE_START_EN, WP_TXT_CODE_END_EN, "Code", issues)
    _check_marker_pair(
        load_file,
        WP_TXT_EMPHASIS_CODE_START,
        WP_TXT_EMPHASIS_CODE_END,
        "強調コード",
        issues,
    )
    _check_marker_pair(
        load_file,
        WP_TXT_EMPHASIS_CODE_START_EN,
        WP_TXT_EMPHASIS_CODE_END_EN,
        "EmphasisCode",
        issues,
    )
    _check_marker_pair(load_file, WP_TXT_LIST_START, WP_TXT_LIST_END, "リスト", issues)
    _check_marker_pair(load_file, WP_TXT_LIST_START_EN, WP_TXT_LIST_END_EN, "List", issues)
    _check_marker_pair(
        load_file,
        WP_TXT_ORDERED_LIST_START,
        WP_TXT_ORDERED_LIST_END,
        "番号リスト",
        issues,
    )
    _check_marker_pair(
        load_file,
        WP_TXT_ORDERED_LIST_START_EN,
        WP_TXT_ORDERED_LIST_END_EN,
        "OrderedList",
        issues,
    )
    _check_marker_pair(
        load_file,
        WP_TXT_PARAGRAPH_START,
        WP_TXT_PARAGRAPH_END,
        "段落",
        issues,
    )
    _check_marker_pair(load_file, WP_TXT_HTML_EXEC_START, WP_TXT_HTML_EXEC_END, "HTML", issues)
    _check_marker_pair(load_file, WP_TXT_HTML_START, WP_TXT_HTML_END, "HTML", issues)
    _check_marker_pair(load_file, WP_TXT_NOTICE_START, WP_TXT_NOTICE_END, "注意", issues)
    _check_marker_pair(load_file, WP_TXT_NOTICE_START_EN, WP_TXT_NOTICE_END_EN, "Notice", issues)
    _check_marker_pair(load_file, WP_TXT_SUPPLEMENT_START, WP_TXT_SUPPLEMENT_END, "補足", issues)
    _check_marker_pair(
        load_file,
        WP_TXT_SUPPLEMENT_START_EN,
        WP_TXT_SUPPLEMENT_END_EN,
        "Supplement",
        issues,
    )
    _check_marker_pair(load_file, WP_TXT_STEPS_START, WP_TXT_STEPS_END, "手順", issues)
    _check_marker_pair(load_file, WP_TXT_STEPS_START_EN, WP_TXT_STEPS_END_EN, "Steps", issues)
    _check_marker_pair(load_file, "[画像横並び:", WP_TXT_IMAGE_ROW_END, "画像横並び", issues)
    _check_marker_pair(load_file, "[ImageRow:", WP_TXT_IMAGE_ROW_END_EN, "ImageRow", issues)
    _check_marker_pair(load_file, WP_TXT_TABLE_START, WP_TXT_TABLE_END, "表", issues)
    _check_marker_pair(load_file, WP_TXT_TABLE_START_EN, WP_TXT_TABLE_END_EN, "Table", issues)
    _check_empty_blocks(load_file, issues)
    _check_link_markers(load_file, issues)
    _check_image_markers(load_file, issues)
    _check_single_url_markers(load_file, "[音声:", VALID_AUDIO_MARKER_PATTERN, "音声", issues)
    _check_single_url_markers(load_file, "[Audio:", VALID_AUDIO_MARKER_PATTERN, "Audio", issues)
    _check_single_url_markers(load_file, "[動画:", VALID_VIDEO_MARKER_PATTERN, "動画", issues)
    _check_single_url_markers(load_file, "[Video:", VALID_VIDEO_MARKER_PATTERN, "Video", issues)
    _check_single_url_markers(load_file, "[ファイル:", VALID_FILE_MARKER_PATTERN, "ファイル", issues)
    _check_single_url_markers(load_file, "[File:", VALID_FILE_MARKER_PATTERN, "File", issues)
    _check_spacer_markers(load_file, issues)
    _check_table_blocks(load_file, issues)
    return issues


def has_errors(issues: list[LintIssue]) -> bool:
    """lint結果にエラーが含まれるか確認します。"""
    return any(issue.level == "error" for issue in issues)


def format_lint_issues(issues: list[LintIssue]) -> str:
    """ダイアログ表示用にlint結果を整形します。"""
    if not issues:
        return "lint結果: 問題は見つかりませんでした。"

    lines = []
    for issue in issues:
        label = "エラー" if issue.level == "error" else "警告"
        lines.append(f"[{label}] {issue.line}行目: {issue.message}\n  {issue.hint}")
    return "\n\n".join(lines)


def _check_marker_pair(
    load_file: str,
    start_marker: str,
    end_marker: str,
    marker_name: str,
    issues: list[LintIssue],
) -> None:
    start_count = load_file.count(start_marker)
    end_count = load_file.count(end_marker)
    if start_count == end_count:
        return

    issues.append(
        LintIssue(
            "error",
            _find_marker_line(load_file, start_marker if start_count > end_count else end_marker),
            f"[{marker_name}] の開始マーカーと終了マーカーの数が合っていません。",
            f"{start_marker} と {end_marker} を対にしてください。",
        )
    )


def _check_empty_blocks(load_file: str, issues: list[LintIssue]) -> None:
    for start_marker, end_marker, marker_name in (
        (WP_TXT_CODE_START, WP_TXT_CODE_END, "コード"),
        (WP_TXT_CODE_START_EN, WP_TXT_CODE_END_EN, "Code"),
        (WP_TXT_BOX_START, WP_TXT_BOX_END, "囲い込み"),
        (WP_TXT_BOX_START_EN, WP_TXT_BOX_END_EN, "Box"),
        (WP_TXT_BOLD_START, WP_TXT_BOLD_END, "太字"),
        (WP_TXT_BOLD_START_EN, WP_TXT_BOLD_END_EN, "Bold"),
        (WP_TXT_EMPHASIS_CODE_START, WP_TXT_EMPHASIS_CODE_END, "強調コード"),
        (WP_TXT_EMPHASIS_CODE_START_EN, WP_TXT_EMPHASIS_CODE_END_EN, "EmphasisCode"),
        (WP_TXT_HTML_EXEC_START, WP_TXT_HTML_EXEC_END, "HTML"),
        (WP_TXT_LIST_START, WP_TXT_LIST_END, "リスト"),
        (WP_TXT_LIST_START_EN, WP_TXT_LIST_END_EN, "List"),
        (WP_TXT_NOTICE_START, WP_TXT_NOTICE_END, "注意"),
        (WP_TXT_NOTICE_START_EN, WP_TXT_NOTICE_END_EN, "Notice"),
        (WP_TXT_ORDERED_LIST_START, WP_TXT_ORDERED_LIST_END, "番号リスト"),
        (WP_TXT_ORDERED_LIST_START_EN, WP_TXT_ORDERED_LIST_END_EN, "OrderedList"),
        (WP_TXT_PARAGRAPH_START, WP_TXT_PARAGRAPH_END, "段落"),
        (WP_TXT_STEPS_START, WP_TXT_STEPS_END, "手順"),
        (WP_TXT_STEPS_START_EN, WP_TXT_STEPS_END_EN, "Steps"),
        (WP_TXT_SUPPLEMENT_START, WP_TXT_SUPPLEMENT_END, "補足"),
        (WP_TXT_SUPPLEMENT_START_EN, WP_TXT_SUPPLEMENT_END_EN, "Supplement"),
        (WP_TXT_HTML_START, WP_TXT_HTML_END, "HTML"),
        (WP_TXT_TABLE_START, WP_TXT_TABLE_END, "表"),
        (WP_TXT_TABLE_START_EN, WP_TXT_TABLE_END_EN, "Table"),
    ):
        pattern = re.compile(
            rf"{re.escape(start_marker)}\s*{re.escape(end_marker)}",
            re.DOTALL,
        )
        for marker_match in pattern.finditer(load_file):
            issues.append(
                LintIssue(
                    "warning",
                    _line_number(load_file, marker_match.start()),
                    f"[{marker_name}] の本文が空です。",
                    "開始マーカーと終了マーカーの間に本文を入れてください。",
                )
            )


def _check_link_markers(load_file: str, issues: list[LintIssue]) -> None:
    for marker_start, marker_name, hint in (
        ("[リンク:", "リンク", "[リンク:表示文字|https://example.com/] の形にしてください。"),
        ("[Link:", "Link", "[Link:Label|https://example.com/] の形にしてください。"),
    ):
        for line_number, marker_text in _iter_line_markers(load_file, marker_start):
            if VALID_LINK_MARKER_PATTERN.match(marker_text):
                continue
            issues.append(
                LintIssue(
                    "error",
                    line_number,
                    f"{marker_name}マーカーの形式が崩れています。",
                    hint,
                )
            )


def _check_image_markers(load_file: str, issues: list[LintIssue]) -> None:
    for marker_start, marker_name, hint in (
        ("[画像:", "画像", "[画像:https://example.com/image.jpg|代替テキスト] の形にしてください。"),
        ("[Image:", "Image", "[Image:https://example.com/image.jpg|Alt text] の形にしてください。"),
    ):
        for line_number, marker_text in _iter_line_markers(load_file, marker_start):
            if VALID_IMAGE_MARKER_PATTERN.match(marker_text):
                continue
            issues.append(
                LintIssue(
                    "error",
                    line_number,
                    f"{marker_name}マーカーの形式が崩れています。",
                    hint,
                )
            )


def _check_single_url_markers(
    load_file: str,
    marker_start: str,
    marker_pattern: re.Pattern[str],
    marker_name: str,
    issues: list[LintIssue],
) -> None:
    for line_number, marker_text in _iter_line_markers(load_file, marker_start):
        if marker_pattern.match(marker_text):
            continue
        issues.append(
            LintIssue(
                "error",
                line_number,
                f"{marker_name}マーカーの形式が崩れています。",
                f"{marker_start}https://example.com/file] の形にしてください。",
            )
        )


def _check_spacer_markers(load_file: str, issues: list[LintIssue]) -> None:
    for marker_match in SPACER_MARKER_PATTERN.finditer(load_file):
        raw_height = marker_match.group(1).strip()
        if raw_height.isdigit() and int(raw_height) > 0:
            continue
        issues.append(
            LintIssue(
                "error",
                _line_number(load_file, marker_match.start()),
                "余白マーカーの数値が不正です。",
                "[余白:25] のように、1以上の数字を指定してください。",
            )
        )


def _check_table_blocks(load_file: str, issues: list[LintIssue]) -> None:
    table_pattern = re.compile(
        rf"{re.escape(WP_TXT_TABLE_START)}(.*?){re.escape(WP_TXT_TABLE_END)}",
        re.DOTALL,
    )
    for table_match in table_pattern.finditer(load_file):
        table_body = table_match.group(1).strip()
        if "|" in table_body:
            continue
        issues.append(
            LintIssue(
                "warning",
                _line_number(load_file, table_match.start()),
                "[表] ブロック内に | がありません。",
                "項目|説明 のように、列の区切りに | を入れてください。",
            )
        )


def _find_marker_line(load_file: str, marker: str) -> int:
    marker_index = load_file.find(marker)
    if marker_index == -1:
        return 1
    return _line_number(load_file, marker_index)


def _line_number(load_file: str, index: int) -> int:
    return load_file.count("\n", 0, index) + 1


def _iter_line_markers(load_file: str, marker_start: str) -> list[tuple[int, str]]:
    markers: list[tuple[int, str]] = []

    for line_number, line in enumerate(load_file.splitlines(), start=1):
        search_start = 0
        while True:
            marker_index = line.find(marker_start, search_start)
            if marker_index == -1:
                break

            marker_end = line.find("]", marker_index)
            if marker_end == -1:
                markers.append((line_number, line[marker_index:]))
                break

            markers.append((line_number, line[marker_index:marker_end + 1]))
            search_start = marker_end + 1

    return markers
