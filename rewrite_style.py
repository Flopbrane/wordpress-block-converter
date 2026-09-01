"""Middle / High-Security向けの表示スタイル調整です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

from dictionaries.hi_security_dict import (
    HIGH_SECURITY_MODE,
    MIDDLE_MODE,
    NORMAL_MODE,
    normalize_conversion_mode,
)

CORRECT_DATA_FILE_NAME = "correct_data.json"
DEFAULT_CODE_WRAP_IGNORE_WORDS: set[str] = {
    "css",
    "html",
    "url",
    "wordpress",
    "python",
    "px",
}
REWRITE_STYLE_MODES: set[str] = {MIDDLE_MODE, HIGH_SECURITY_MODE}
HEADING_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*wp:heading\b[^>]*-->\s*"
    r"<h([1-6])(\s[^>]*)?>(.*?)</h\1>\s*"
    r"<!--\s*/wp:heading\s*-->",
    re.IGNORECASE | re.DOTALL,
)
PARAGRAPH_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    r"(<!--\s*wp:paragraph\s*-->\s*)"
    r"(<p\b[^>]*>)(.*?)(</p>)"
    r"(\s*<!--\s*/wp:paragraph\s*-->)",
    re.IGNORECASE | re.DOTALL,
)
PROTECTED_INLINE_HTML_PATTERN: re.Pattern[str] = re.compile(
    r"(<code\b[^>]*>.*?</code>|<a\b[^>]*>.*?</a>|<[^>]+>)",
    re.IGNORECASE | re.DOTALL,
)
ESCAPED_TAG_EXAMPLE_PATTERN: re.Pattern[str] = re.compile(
    r"(&lt;/?[a-zA-Z!][^&]*?&gt;)",
)
ALPHABET_WORD_PATTERN: re.Pattern[str] = re.compile(
    r"(?<![&/#])\b[A-Za-z][A-Za-z0-9_-]*\b",
)
TRAILING_BREAKS_PATTERN: re.Pattern[str] = re.compile(
    r"((?:\s*<br\s*/?>\s*)+)$",
    re.IGNORECASE,
)
JAPANESE_TEXT_PATTERN: re.Pattern[str] = re.compile(r"[ぁ-んァ-ヶ一-龠々ー]")
LEADING_SPACE_PATTERN: re.Pattern[str] = re.compile(r"^[ \t　]+")


def apply_rewrite_style(
    save_file: str,
    mode: str = NORMAL_MODE,
    correct_data_path: str | Path | None = None,
) -> str:
    """modeに応じて、WordPressに貼りやすい表示スタイルへ整えます。"""
    normalized_mode = normalize_conversion_mode(mode)
    if normalized_mode not in REWRITE_STYLE_MODES:
        return save_file

    code_wrap_ignore_words = load_code_wrap_ignore_words(correct_data_path)
    save_file = _normalize_heading_blocks(save_file)
    return PARAGRAPH_BLOCK_PATTERN.sub(
        lambda paragraph_match: _rewrite_paragraph_block(
            paragraph_match,
            code_wrap_ignore_words,
        ),
        save_file,
    )


def load_code_wrap_ignore_words(correct_data_path: str | Path | None = None) -> set[str]:
    """correct_data.jsonからcode囲み除外ワードを読み込みます。"""
    load_path = Path(correct_data_path) if correct_data_path is not None else _find_correct_data_path()
    if load_path is None or not load_path.exists():
        return DEFAULT_CODE_WRAP_IGNORE_WORDS.copy()

    try:
        correct_data = json.loads(load_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CODE_WRAP_IGNORE_WORDS.copy()

    ignore_words = _extract_code_wrap_ignore_words(correct_data)
    if not ignore_words:
        return DEFAULT_CODE_WRAP_IGNORE_WORDS.copy()

    return ignore_words


def _find_correct_data_path() -> Path | None:
    for base_path in _candidate_correct_data_dirs():
        correct_data_path = base_path / CORRECT_DATA_FILE_NAME
        if correct_data_path.exists():
            return correct_data_path

    return None


def _candidate_correct_data_dirs() -> list[Path]:
    candidate_dirs: list[Path] = []
    if getattr(sys, "frozen", False):
        candidate_dirs.append(Path(sys.executable).resolve().parent)

    candidate_dirs.append(Path(__file__).resolve().parent)
    candidate_dirs.append(Path.cwd())
    return candidate_dirs


def _extract_code_wrap_ignore_words(correct_data: Any) -> set[str]:
    if not isinstance(correct_data, dict):
        return set()

    raw_words = correct_data.get("code_wrap_ignore_words", [])
    if not isinstance(raw_words, list):
        return set()

    return {
        word.strip().casefold()
        for word in raw_words
        if isinstance(word, str) and word.strip()
    }


def _normalize_heading_blocks(save_file: str) -> str:
    found_first_heading = False

    def replace_heading(heading_match: re.Match[str]) -> str:
        nonlocal found_first_heading

        level = int(heading_match.group(1))
        attrs = heading_match.group(2) or ""
        text = heading_match.group(3)

        if not found_first_heading:
            found_first_heading = True
            return _create_heading_block(2, attrs, text)

        if level == 2:
            return _create_heading_block(3, attrs, text)

        return heading_match.group(0)

    return HEADING_BLOCK_PATTERN.sub(replace_heading, save_file)


def _create_heading_block(level: int, attrs: str, text: str) -> str:
    return (
        f'<!-- wp:heading {{"level":{level}}} -->\n'
        f"<h{level}{attrs}>{text}</h{level}>\n"
        "<!-- /wp:heading -->"
    )


def _rewrite_paragraph_block(
    paragraph_match: re.Match[str],
    code_wrap_ignore_words: set[str],
) -> str:
    start_comment = paragraph_match.group(1)
    start_tag = paragraph_match.group(2)
    body = paragraph_match.group(3)
    end_tag = paragraph_match.group(4)
    end_comment = paragraph_match.group(5)
    rewritten_body = _rewrite_paragraph_body(body, code_wrap_ignore_words)
    return f"{start_comment}{start_tag}{rewritten_body}{end_tag}{end_comment}"


def _rewrite_paragraph_body(body: str, code_wrap_ignore_words: set[str]) -> str:
    rewritten_lines: list[str] = []
    found_first_text_line = False

    for line in body.splitlines():
        if line.strip() and found_first_text_line:
            line = _remove_leading_spaces(line)
        elif line.strip():
            found_first_text_line = True
        rewritten_lines.append(_rewrite_paragraph_line(line, code_wrap_ignore_words))

    return "\n".join(rewritten_lines)


def _remove_leading_spaces(line: str) -> str:
    return LEADING_SPACE_PATTERN.sub("", line)


def _rewrite_paragraph_line(line: str, code_wrap_ignore_words: set[str]) -> str:
    trailing_break = ""
    break_match = TRAILING_BREAKS_PATTERN.search(line)
    if break_match:
        trailing_break = _select_line_break(line[:break_match.start()])
        line = line[:break_match.start()]

    rewritten_line = _rewrite_inline_code_scope(line)
    rewritten_line = _wrap_alphabet_text(rewritten_line, code_wrap_ignore_words)
    return f"{rewritten_line}{trailing_break}"


def _rewrite_inline_code_scope(line: str) -> str:
    def replace_code(code_match: re.Match[str]) -> str:
        code_body = code_match.group(1)
        escaped_end_index = code_body.find("&gt;")
        if escaped_end_index == -1:
            return code_match.group(0)

        code_text = code_body[:escaped_end_index + len("&gt;")]
        description_text = code_body[escaped_end_index + len("&gt;"):]
        if not description_text.strip() or "&lt;" in description_text:
            return code_match.group(0)

        return f"<code>{code_text}</code>{description_text}"

    return re.sub(r"<code>(.*?)</code>", replace_code, line, flags=re.IGNORECASE | re.DOTALL)


def _wrap_alphabet_text(line: str, code_wrap_ignore_words: set[str]) -> str:
    parts = PROTECTED_INLINE_HTML_PATTERN.split(line)
    return "".join(
        part if PROTECTED_INLINE_HTML_PATTERN.fullmatch(part) else _wrap_text_part(
            part,
            code_wrap_ignore_words,
        )
        for part in parts
    )


def _wrap_text_part(text: str, code_wrap_ignore_words: set[str]) -> str:
    placeholders: dict[str, str] = {}

    def save_escaped_tag(tag_match: re.Match[str]) -> str:
        placeholder = f"\x00{len(placeholders)}\x00"
        placeholders[placeholder] = f"<code>{tag_match.group(1)}</code>"
        return placeholder

    text = ESCAPED_TAG_EXAMPLE_PATTERN.sub(save_escaped_tag, text)
    text = ALPHABET_WORD_PATTERN.sub(
        lambda word_match: _wrap_alphabet_word(
            word_match,
            code_wrap_ignore_words,
        ),
        text,
    )

    for placeholder, code_html in placeholders.items():
        text = text.replace(placeholder, code_html)

    return text


def _wrap_alphabet_word(word_match: re.Match[str], code_wrap_ignore_words: set[str]) -> str:
    word = word_match.group(0)
    if word.casefold() in code_wrap_ignore_words:
        return word

    return f"<code>{word}</code>"


def _select_line_break(line_without_break: str) -> str:
    tail_text = _text_after_last_code(line_without_break)
    if JAPANESE_TEXT_PATTERN.search(tail_text):
        return "<br><br>"

    return "<br>"


def _text_after_last_code(line: str) -> str:
    code_end_index = line.lower().rfind("</code>")
    if code_end_index == -1:
        return re.sub(r"<[^>]+>", "", line)

    return re.sub(r"<[^>]+>", "", line[code_end_index + len("</code>"):])
