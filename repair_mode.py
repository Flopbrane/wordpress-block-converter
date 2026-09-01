"""既存のWordPressブロックHTMLを修復するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re

from converters.hi_security_filter import apply_hi_security_filter
from dictionaries.hi_security_dict import (
    NORMAL_MODE,
    SAFE_CONVERSION_MODES,
    normalize_conversion_mode,
)
from rewrite_style import apply_rewrite_style

WORDPRESS_BLOCK_COMMENT_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*/?wp:[a-zA-Z0-9_-]+(?:\s+.*?)?\s*-->",
)
BLOCK_COMMENT_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*(/)?wp:([a-zA-Z0-9_-]+)(?:\s+.*?)?\s*-->",
)
WP_HEADING_START_PATTERN: re.Pattern[str] = re.compile(r"<!--\s*wp:heading\s*-->")
WP_HEADING_TAG_PATTERN: re.Pattern[str] = re.compile(r"<h([1-6])\b", re.IGNORECASE)
EMPTY_PARAGRAPH_LINE_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*<p\b[^>]*>(?:\s|&nbsp;|\u00a0|<br\s*/?>)*</p>\s*$",
    re.IGNORECASE,
)
STANDALONE_BREAK_LINE_PATTERN: re.Pattern[str] = re.compile(r"^\s*<br\s*/?>\s*$", re.IGNORECASE)
TRAILING_BREAKS_PATTERN: re.Pattern[str] = re.compile(r"((?:\s*<br\s*/?>\s*)+)$", re.IGNORECASE)
CODE_LINE_PATTERN: re.Pattern[str] = re.compile(r"^(\s*(?:<p\b[^>]*>)?)<code>(.*)$", re.IGNORECASE)
MISORDERED_CODE_PARAGRAPH_END_PATTERN: re.Pattern[str] = re.compile(
    r"(<code\b[^>]*>.*?)(</p>)(</code>)",
    re.IGNORECASE,
)
CODE_END_WITHOUT_LINE_START_PATTERN: re.Pattern[str] = re.compile(
    r"^(\s*)((?!.*<code\b).*</code>(?:<br\s*/?>)?)\s*$",
    re.IGNORECASE,
)
UNCLOSED_STRONG_BEFORE_PARAGRAPH_END_PATTERN: re.Pattern[str] = re.compile(
    r"(<strong\b[^>]*>)([^<]*)(</p>)",
    re.IGNORECASE,
)


def repair_wordpress_html(load_file: str, mode: str = NORMAL_MODE) -> str:
    """既存WPコードを、全体変換せずに修復します。"""
    normalized_mode = normalize_conversion_mode(mode)
    save_file = _repair_block_syntax(load_file)

    if normalized_mode in SAFE_CONVERSION_MODES:
        save_file = apply_hi_security_filter(save_file)

    return apply_rewrite_style(save_file, normalized_mode)


def _repair_block_syntax(load_file: str) -> str:
    normalized_load_file = load_file.replace("\r\n", "\n").replace("\r", "\n")
    if not WORDPRESS_BLOCK_COMMENT_PATTERN.search(normalized_load_file):
        return normalized_load_file

    repaired_file = _repair_lines(normalized_load_file)
    repaired_file = _remove_empty_paragraph_before_blocks(repaired_file)
    repaired_file = _close_paragraph_before_separator(repaired_file)
    repaired_file = _wrap_bare_paragraph_block_text(repaired_file)
    repaired_file = _remove_duplicate_block_end_comments(repaired_file)
    repaired_file = _drop_unmatched_block_end_comments(repaired_file)
    return _restore_final_newline(repaired_file, normalized_load_file)


def _repair_lines(load_file: str) -> str:
    lines = load_file.splitlines()
    repaired_lines: list[str] = []

    for line_index, line in enumerate(lines):
        if EMPTY_PARAGRAPH_LINE_PATTERN.match(line) or STANDALONE_BREAK_LINE_PATTERN.match(line):
            continue

        repaired_line = _fix_heading_start_line(line, lines[line_index + 1:])
        repaired_line = _fix_code_line(repaired_line)
        repaired_line = _fix_common_inline_tag_mistakes(repaired_line)
        repaired_lines.append(repaired_line)

    return "\n".join(repaired_lines)


def _fix_heading_start_line(line: str, following_lines: list[str]) -> str:
    if not WP_HEADING_START_PATTERN.search(line):
        return line

    for following_line in following_lines:
        heading_match = WP_HEADING_TAG_PATTERN.search(following_line)
        if heading_match:
            level = heading_match.group(1)
            return WP_HEADING_START_PATTERN.sub(f'<!-- wp:heading {{"level":{level}}} -->', line)

        if WORDPRESS_BLOCK_COMMENT_PATTERN.search(following_line):
            break

    return line


def _fix_code_line(line: str) -> str:
    if "wp-block-separator" in line:
        return line.replace("<code>", "").replace("</code>", "")

    code_line_match = CODE_LINE_PATTERN.match(line)
    if code_line_match is None:
        return line

    prefix = code_line_match.group(1)
    body = code_line_match.group(2)
    break_html = ""

    body = body.replace("<code>", "").replace("</code>", "").replace("&gt;/code&gt;", "&gt;").strip()
    break_match = TRAILING_BREAKS_PATTERN.search(body)
    if break_match:
        break_html = _normalize_break_html(break_match.group(1))
        body = body[:break_match.start()].strip()

    split_body = _split_inline_code_and_description(body)
    if split_body is not None:
        code_text, description_text = split_body
        if break_html:
            return f"{prefix}<code>{code_text}</code>{description_text}{break_html}"
        return f"{prefix}<code>{code_text}</code>{description_text}"

    if break_html:
        return f"{prefix}<code>{body}</code>{break_html}"

    return f"{prefix}<code>{body}</code>"


def _normalize_break_html(break_html: str) -> str:
    break_count = len(re.findall(r"<br\s*/?>", break_html, flags=re.IGNORECASE))
    if break_count >= 2:
        return "<br><br>"

    return "<br>"


def _split_inline_code_and_description(body: str) -> tuple[str, str] | None:
    if not body.startswith("&lt;"):
        return None

    escaped_end_index = body.find("&gt;")
    if escaped_end_index == -1:
        return None

    code_text = body[:escaped_end_index + len("&gt;")]
    description_text = body[escaped_end_index + len("&gt;"):]
    if not description_text.strip() or "&lt;" in description_text:
        return None

    return code_text, description_text


def _fix_common_inline_tag_mistakes(line: str) -> str:
    repaired_line = MISORDERED_CODE_PARAGRAPH_END_PATTERN.sub(r"\1\3\2", line)
    repaired_line = CODE_END_WITHOUT_LINE_START_PATTERN.sub(r"\1<code>\2", repaired_line)
    return UNCLOSED_STRONG_BEFORE_PARAGRAPH_END_PATTERN.sub(r"\1\2</strong>\3", repaired_line)


def _remove_empty_paragraph_before_blocks(load_file: str) -> str:
    return re.sub(
        r"<!--\s*wp:paragraph\s*-->\s*(?=<!--\s*wp:(?:separator|heading|html|table|list)\b)",
        "",
        load_file,
    )


def _close_paragraph_before_separator(load_file: str) -> str:
    return re.sub(
        r"<!--\s*wp:separator\s*-->\s*</p>(\s*<hr\b[^>]*>)",
        r"</p>\n<!-- /wp:paragraph -->\n<!-- wp:separator -->\n\1",
        load_file,
        flags=re.IGNORECASE,
    )


def _wrap_bare_paragraph_block_text(load_file: str) -> str:
    def replace_bare_text(match: re.Match[str]) -> str:
        content = match.group(1).strip()
        if not content or re.search(r"<p\b", content, re.IGNORECASE):
            return match.group(0)

        return f"<!-- wp:paragraph -->\n<p>{content}</p>\n<!-- /wp:paragraph -->"

    return re.sub(
        r"<!--\s*wp:paragraph\s*-->\s*(.*?)\s*<!--\s*/wp:paragraph\s*-->",
        replace_bare_text,
        load_file,
        flags=re.DOTALL,
    )


def _remove_duplicate_block_end_comments(load_file: str) -> str:
    return re.sub(
        r"(<!--\s*/wp:([a-zA-Z0-9_-]+)\s*-->)\s*\n\s*<!--\s*/wp:\2\s*-->",
        r"\1",
        load_file,
    )


def _drop_unmatched_block_end_comments(load_file: str) -> str:
    repaired_lines: list[str] = []
    block_stack: list[str] = []

    for line in load_file.splitlines():
        block_match = BLOCK_COMMENT_PATTERN.fullmatch(line.strip())
        if block_match is None:
            repaired_lines.append(line)
            continue

        is_end_comment = bool(block_match.group(1))
        block_name = block_match.group(2)
        if not is_end_comment:
            block_stack.append(block_name)
            repaired_lines.append(line)
            continue

        if block_stack and block_stack[-1] == block_name:
            block_stack.pop()
            repaired_lines.append(line)

    return "\n".join(repaired_lines)


def _restore_final_newline(repaired_file: str, original_file: str) -> str:
    if original_file.endswith("\n"):
        return f"{repaired_file}\n"

    return repaired_file
