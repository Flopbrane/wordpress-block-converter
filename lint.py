"""WordPress HTMLの簡易lint機能です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

try:
    from .dictionaries.hi_security_dict import BLOCKED_TAGS
except ImportError:
    from dictionaries.hi_security_dict import BLOCKED_TAGS


@dataclass
class LintIssue:
    """lintで見つかった問題です。"""

    line_number: int
    message: str
    hint: str

    def format(self) -> str:
        """CLI表示用の文字列にします。"""
        return f"{self.line_number}行目: {self.message}\n  ヒント: {self.hint}"


BLOCK_COMMENT_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*(/)?wp:([a-zA-Z0-9_-]+)(?:\s+(\{.*?\}))?\s*-->",
)
PARAGRAPH_START_PATTERN: re.Pattern[str] = re.compile(r"<p\b[^>]*>", re.IGNORECASE)
PARAGRAPH_END_PATTERN: re.Pattern[str] = re.compile(r"</p>", re.IGNORECASE)
EMPTY_PARAGRAPH_PATTERN: re.Pattern[str] = re.compile(
    r"<p\b[^>]*>(?:\s|&nbsp;|\u00a0|<br\s*/?>)*</p>",
    re.IGNORECASE,
)
HEADING_TAG_PATTERN: re.Pattern[str] = re.compile(r"<h([2-5])\b[^>]*>", re.IGNORECASE)
TABLE_FIGURE_PATTERN: re.Pattern[str] = re.compile(
    r"<figure\b[^>]*class\s*=\s*['\"][^'\"]*\bwp-block-table\b[^'\"]*['\"]",
    re.IGNORECASE,
)
TABLE_TAG_PATTERN: re.Pattern[str] = re.compile(r"<table\b[^>]*>", re.IGNORECASE)

VOID_TAGS: set[str] = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta"}
BLOCKED_ATTRIBUTES: set[str] = {
    "onclick",
    "onload",
    "onerror",
    "onmouseover",
    "style",
}
BLOCKED_URL_PREFIXES: tuple[str, ...] = ("javascript:", "data:", "vbscript:")


def lint_wp_html(load_file: str) -> list[LintIssue]:
    """WordPress HTML文字列を検査して、問題一覧を返します。"""
    issues: list[LintIssue] = []
    issues.extend(_lint_block_comments(load_file))
    issues.extend(_lint_html_tags(load_file))
    return sorted(issues, key=lambda issue: issue.line_number)


def lint_file(load_file_path: str | Path) -> list[LintIssue]:
    """ファイルを読み込んでWordPress HTMLを検査します。"""
    load_file_path = Path(load_file_path)
    load_file = load_file_path.read_text(encoding="utf-8-sig")
    return lint_wp_html(load_file)


def main() -> None:
    """CLIからWordPress HTMLを検査します。"""
    parser = argparse.ArgumentParser(
        description="WordPressブロックHTMLの閉じ忘れや属性不足を確認します。"
    )
    parser.add_argument("load_file_path", help="検査したい.wp_htmlまたはHTMLファイルのパス")
    args = parser.parse_args()

    issues = lint_file(args.load_file_path)
    if not issues:
        print("問題は見つかりませんでした。")
        return

    for issue in issues:
        print(issue.format())

    raise SystemExit(1)


def _lint_block_comments(load_file: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    block_stack: list[dict[str, str | int]] = []

    for line_number, line in enumerate(load_file.splitlines(), start=1):
        for block_match in BLOCK_COMMENT_PATTERN.finditer(line):
            is_end_comment = bool(block_match.group(1))
            block_name = block_match.group(2)
            block_attrs = block_match.group(3) or ""

            if is_end_comment:
                _close_block_comment(issues, block_stack, block_name, line_number)
                continue

            block_stack.append({
                "name": block_name,
                "attrs": block_attrs,
                "line_number": line_number,
                "content": "",
            })

        for block_info in block_stack:
            block_info["content"] = f"{block_info['content']}{line}\n"

    for block_info in block_stack:
        block_name = str(block_info["name"])
        issues.append(LintIssue(
            int(block_info["line_number"]),
            f"wp:{block_name} ブロックが閉じられていません。",
            f"<!-- /wp:{block_name} --> を追加してください。",
        ))

    return issues


def _close_block_comment(
    issues: list[LintIssue],
    block_stack: list[dict[str, str | int]],
    block_name: str,
    line_number: int,
) -> None:
    if not block_stack:
        issues.append(LintIssue(
            line_number,
            f"閉じる wp:{block_name} ブロックに対応する開始コメントがありません。",
            f"先に <!-- wp:{block_name} --> を追加してください。",
        ))
        return

    block_info = block_stack.pop()
    start_block_name = str(block_info["name"])
    if start_block_name != block_name:
        issues.append(LintIssue(
            line_number,
            f"wp:{start_block_name} ブロックを開いていますが、wp:{block_name} で閉じています。",
            f"<!-- /wp:{start_block_name} --> で閉じてください。",
        ))
        return

    content = str(block_info["content"])
    start_line_number = int(block_info["line_number"])
    if block_name == "paragraph":
        _lint_paragraph_block(issues, content, start_line_number)
    elif block_name == "heading":
        _lint_heading_block(issues, content, str(block_info["attrs"]), start_line_number)
    elif block_name == "table":
        _lint_table_block(issues, content, start_line_number)


def _lint_paragraph_block(
    issues: list[LintIssue],
    content: str,
    line_number: int,
) -> None:
    if not PARAGRAPH_START_PATTERN.search(content):
        issues.append(LintIssue(
            line_number,
            "paragraph ブロック内に <p> がありません。",
            "<!-- wp:paragraph --> の中に <p>本文</p> を入れてください。",
        ))
    if not PARAGRAPH_END_PATTERN.search(content):
        issues.append(LintIssue(
            _find_issue_line_number(content, PARAGRAPH_START_PATTERN, line_number),
            "paragraph ブロック内の <p> が閉じられていません。",
            "</p> を追加してください。",
        ))
    elif EMPTY_PARAGRAPH_PATTERN.search(content):
        issues.append(LintIssue(
            _find_issue_line_number(content, EMPTY_PARAGRAPH_PATTERN, line_number),
            "paragraph ブロックが空です。",
            "空の paragraph ブロックは削除するか、本文を入れてください。",
        ))


def _lint_heading_block(
    issues: list[LintIssue],
    content: str,
    attrs: str,
    line_number: int,
) -> None:
    level = _extract_heading_level(attrs)
    heading_match = HEADING_TAG_PATTERN.search(content)
    if not heading_match:
        issues.append(LintIssue(
            line_number,
            "heading ブロック内に h2/h3/h4/h5 がありません。",
            "本文用の見出しとして <h2> から <h5> を使ってください。",
        ))
        return

    html_level = int(heading_match.group(1))
    if level is None:
        issues.append(LintIssue(
            line_number,
            "heading ブロックコメントに level が明記されていません。",
            f'<!-- wp:heading {{"level":{html_level}}} --> のようにしてください。',
        ))
        return

    if level != html_level:
        issues.append(LintIssue(
            line_number,
            f"wp:heading level={level} ですが、HTML側が <h{html_level}> になっています。",
            f'ブロックコメントの level と <h{level}> を一致させてください。',
        ))


def _lint_table_block(
    issues: list[LintIssue],
    content: str,
    line_number: int,
) -> None:
    if not TABLE_FIGURE_PATTERN.search(content):
        issues.append(LintIssue(
            line_number,
            'table ブロック内に <figure class="wp-block-table"> がありません。',
            '<figure class="wp-block-table"><table>...</table></figure> の形にしてください。',
        ))
    if not TABLE_TAG_PATTERN.search(content):
        issues.append(LintIssue(
            line_number,
            "table ブロック内に <table> がありません。",
            "<table>...</table> を追加してください。",
        ))


def _extract_heading_level(attrs: str) -> int | None:
    if not attrs:
        return None

    try:
        parsed_attrs = json.loads(attrs)
    except json.JSONDecodeError:
        return None

    level = parsed_attrs.get("level")
    if isinstance(level, int):
        return level

    return None


def _find_issue_line_number(content: str, pattern: re.Pattern[str], base_line_number: int) -> int:
    match = pattern.search(content)
    if not match:
        return base_line_number

    return base_line_number + content[:match.start()].count("\n")


def _lint_html_tags(load_file: str) -> list[LintIssue]:
    parser = WpHtmlTagLintParser()
    parser.feed(load_file)
    parser.close()
    return parser.issues


class WpHtmlTagLintParser(HTMLParser):
    """HTMLタグの閉じ忘れと属性不足を確認するHTMLParserです。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.issues: list[LintIssue] = []
        self._open_tags: list[tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = tag.lower()
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        line_number = self.getpos()[0]

        self._lint_dangerous_tag(clean_tag, line_number)
        self._lint_dangerous_attributes(clean_tag, attrs_dict, line_number)

        if clean_tag == "a":
            self._lint_anchor(attrs_dict, line_number)
        elif clean_tag == "img":
            self._lint_image(attrs_dict, line_number)

        if clean_tag not in VOID_TAGS:
            self._open_tags.append((clean_tag, line_number))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = tag.lower()
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        line_number = self.getpos()[0]

        self._lint_dangerous_tag(clean_tag, line_number)
        self._lint_dangerous_attributes(clean_tag, attrs_dict, line_number)

        if clean_tag == "a":
            self._lint_anchor(attrs_dict, line_number)
        elif clean_tag == "img":
            self._lint_image(attrs_dict, line_number)

    def handle_endtag(self, tag: str) -> None:
        clean_tag = tag.lower()
        line_number = self.getpos()[0]

        if self._open_tags and self._open_tags[-1][0] == clean_tag:
            self._open_tags.pop()
            return

        for index in range(len(self._open_tags) - 2, -1, -1):
            open_tag, _open_line_number = self._open_tags[index]
            if open_tag != clean_tag:
                continue

            unclosed_tags = self._open_tags[index + 1:]
            for unclosed_tag, unclosed_line_number in unclosed_tags:
                self.issues.append(LintIssue(
                    unclosed_line_number,
                    f"<{unclosed_tag}> が閉じられていません。",
                    f"</{unclosed_tag}> を </{clean_tag}> より前に追加してください。",
                ))
            del self._open_tags[index:]
            return

        self.issues.append(LintIssue(
            line_number,
            f"</{clean_tag}> に対応する開始タグがありません。",
            f"<{clean_tag}> と </{clean_tag}> の対応を確認してください。",
        ))

    def close(self) -> None:
        super().close()
        for open_tag, line_number in self._open_tags:
            self.issues.append(LintIssue(
                line_number,
                f"<{open_tag}> が閉じられていません。",
                f"</{open_tag}> を追加してください。",
            ))

    def _lint_dangerous_tag(self, tag: str, line_number: int) -> None:
        if tag not in BLOCKED_TAGS:
            return

        self.issues.append(LintIssue(
            line_number,
            f"<{tag}> はmiddle / high-security modeでは危険扱いです。",
            f"<{tag}> を削除するか、安全なGutenberg標準ブロックへ置き換えてください。",
        ))

    def _lint_dangerous_attributes(
        self,
        tag: str,
        attrs: dict[str, str],
        line_number: int,
    ) -> None:
        for attr_name, attr_value in attrs.items():
            if attr_name in BLOCKED_ATTRIBUTES:
                self.issues.append(LintIssue(
                    line_number,
                    f"<{tag}> タグに危険または崩れやすい属性 {attr_name} があります。",
                    f'{attr_name} を削除してください。',
                ))

            if attr_name in {"href", "src"} and _starts_with_blocked_url(attr_value):
                self.issues.append(LintIssue(
                    line_number,
                    f"<{tag}> タグに危険なURLがあります。",
                    "javascript:、data:、vbscript: は使わないでください。",
                ))

    def _lint_anchor(self, attrs: dict[str, str], line_number: int) -> None:
        if "href" not in attrs or not attrs["href"].strip():
            self.issues.append(LintIssue(
                line_number,
                "<a> タグに href がありません。",
                '<a href="https://example.com">リンク</a> の形にしてください。',
            ))

        if attrs.get("target") == "_blank" and "noopener" not in attrs.get("rel", "").split():
            self.issues.append(LintIssue(
                line_number,
                'target="_blank" がありますが rel="noopener" がありません。',
                'rel="noopener" を追加してください。',
            ))

    def _lint_image(self, attrs: dict[str, str], line_number: int) -> None:
        if "src" not in attrs or not attrs["src"].strip():
            self.issues.append(LintIssue(
                line_number,
                "<img> タグに src がありません。",
                '<img src="画像URL" alt="画像説明"> の形にしてください。',
            ))
        if "alt" not in attrs:
            self.issues.append(LintIssue(
                line_number,
                "<img> タグに alt がありません。",
                'alt="画像説明" を追加してください。',
            ))


def _starts_with_blocked_url(url: str) -> bool:
    return url.lower().strip().startswith(BLOCKED_URL_PREFIXES)


if __name__ == "__main__":
    main()
