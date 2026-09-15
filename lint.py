"""WordPress HTMLの簡易lint機能です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import argparse
from difflib import get_close_matches
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

try:
    from .dictionaries.html_dict import (
        ALLOWED_HTML_TAGS,
        DISPLAY_UNSTABLE_CLASS_KEYWORDS,
        NON_NORMAL_UNSTABLE_CORE_BLOCKS,
        WORDPRESS_CORE_BLOCKS,
    )
    from .dictionaries.hi_security_dict import (
        BLOCKED_ATTRIBUTES,
        BLOCKED_TAGS,
        BLOCKED_URL_PREFIXES,
        HIGH_SECURITY_MODE,
        NORMAL_MODE,
        SAFE_CONVERSION_MODES,
        normalize_conversion_mode,
    )
except ImportError:
    from dictionaries.html_dict import (
        ALLOWED_HTML_TAGS,
        DISPLAY_UNSTABLE_CLASS_KEYWORDS,
        NON_NORMAL_UNSTABLE_CORE_BLOCKS,
        WORDPRESS_CORE_BLOCKS,
    )
    from dictionaries.hi_security_dict import (
        BLOCKED_ATTRIBUTES,
        BLOCKED_TAGS,
        BLOCKED_URL_PREFIXES,
        HIGH_SECURITY_MODE,
        NORMAL_MODE,
        SAFE_CONVERSION_MODES,
        normalize_conversion_mode,
    )


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
    r"<!--\s*(/)?wp:([a-zA-Z0-9_/-]+)(?:\s+(\{.*?\}))?\s*-->",
)
PARAGRAPH_START_PATTERN: re.Pattern[str] = re.compile(r"<p\b[^>]*>", re.IGNORECASE)
PARAGRAPH_END_PATTERN: re.Pattern[str] = re.compile(r"</p>", re.IGNORECASE)
PARAGRAPH_CONTENT_PATTERN: re.Pattern[str] = re.compile(
    r"<p\b[^>]*>(.*?)</p>",
    re.IGNORECASE | re.DOTALL,
)
PARAGRAPH_INNER_BLANK_LINE_PATTERN: re.Pattern[str] = re.compile(r"\n[ \t\u3000]*\n")
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

RAW_HTML_BLOCK_NAMES: set[str] = {"html", "code"}
VOID_TAGS: set[str] = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta"}
KNOWN_WORDPRESS_CORE_BLOCKS: set[str] = set(WORDPRESS_CORE_BLOCKS)
KNOWN_HTML_TAGS: set[str] = ALLOWED_HTML_TAGS | {
    "abbr",
    "address",
    "article",
    "aside",
    "base",
    "bdi",
    "bdo",
    "body",
    "br",
    "button",
    "caption",
    "cite",
    "col",
    "colgroup",
    "data",
    "dd",
    "del",
    "details",
    "dfn",
    "dialog",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "head",
    "header",
    "html",
    "iframe",
    "input",
    "ins",
    "kbd",
    "label",
    "legend",
    "main",
    "mark",
    "menu",
    "meta",
    "meter",
    "nav",
    "noscript",
    "object",
    "option",
    "output",
    "picture",
    "progress",
    "q",
    "rp",
    "rt",
    "ruby",
    "s",
    "samp",
    "script",
    "section",
    "select",
    "small",
    "source",
    "span",
    "style",
    "sub",
    "summary",
    "sup",
    "svg",
    "textarea",
    "tfoot",
    "time",
    "title",
    "track",
    "u",
    "var",
    "wbr",
}
COMMON_HTML_TAG_TYPOS: dict[str, str] = {
    "artcle": "article",
    "blcokquote": "blockquote",
    "bolckquote": "blockquote",
    "buton": "button",
    "dev": "div",
    "dvi": "div",
    "emph": "em",
    "figcaptionn": "figcaption",
    "figuer": "figure",
    "from": "form",
    "haeder": "header",
    "heder": "header",
    "iamge": "img",
    "imgae": "img",
    "imge": "img",
    "lable": "label",
    "paragaph": "p",
    "paragrah": "p",
    "secton": "section",
    "slect": "select",
    "sorce": "source",
    "spna": "span",
    "storng": "strong",
    "strnog": "strong",
    "strog": "strong",
    "tabl": "table",
    "tbale": "table",
    "texarea": "textarea",
    "tabel": "table",
}
INPUT_TYPE_AUTO = "auto"
INPUT_TYPE_WP_HTML = "wp-html"
INPUT_TYPE_CSS = "css"
LINT_INPUT_TYPES: tuple[str, ...] = (INPUT_TYPE_AUTO, INPUT_TYPE_WP_HTML, INPUT_TYPE_CSS)
CSS_EXTENSIONS: set[str] = {".css"}
CSS_COMMENT_PATTERN: re.Pattern[str] = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_RESTRICTION_RULES: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(r"\bdisplay\s*:\s*none\b", re.IGNORECASE),
        "CSSに display:none があり、対象要素が表示されません。",
        "事業所WPで必要な本文・ボタン・リンクに使うと、ブロックが存在しても画面に出ないことがあります。",
    ),
    (
        re.compile(r"\bvisibility\s*:\s*hidden\b", re.IGNORECASE),
        "CSSに visibility:hidden があり、対象要素が見えなくなります。",
        "領域だけ残って内容が見えない状態になるため、重要な本文や導線には使わないでください。",
    ),
    (
        re.compile(r"\bcontent-visibility\s*:\s*hidden\b", re.IGNORECASE),
        "CSSに content-visibility:hidden があり、対象要素の描画が抑止されます。",
        "ブラウザや埋め込み先によって表示確認が難しくなるため、通常ブロックでは避けてください。",
    ),
    (
        re.compile(r"\bopacity\s*:\s*0(?:\.0+)?\b", re.IGNORECASE),
        "CSSに opacity:0 があり、対象要素が透明になります。",
        "見えないままクリック判定だけ残ることがあるため、リンクやボタン周辺では特に注意してください。",
    ),
    (
        re.compile(r"\bpointer-events\s*:\s*none\b", re.IGNORECASE),
        "CSSに pointer-events:none があり、クリックやタップが無効化されます。",
        "リンク、ボタン、画像リンクに適用されると操作できなくなるため、導線には使わないでください。",
    ),
    (
        re.compile(r"\buser-select\s*:\s*none\b", re.IGNORECASE),
        "CSSに user-select:none があり、テキスト選択が制限されます。",
        "コピーが必要なコード、URL、案内文には使わないでください。",
    ),
    (
        re.compile(r"\boverflow(?:-[xy])?\s*:\s*hidden\b", re.IGNORECASE),
        "CSSに overflow:hidden があり、はみ出した内容が隠れます。",
        "モバイル幅や文字サイズ変更時に本文・画像・表の一部が欠けることがあります。",
    ),
    (
        re.compile(r"\bclip(?:-path)?\s*:", re.IGNORECASE),
        "CSSに clip / clip-path があり、表示範囲が切り抜かれます。",
        "本文や画像の一部が見えなくなることがあるため、装飾以外では避けてください。",
    ),
    (
        re.compile(r"\b(?:width|height|max-width|max-height)\s*:\s*0(?:px|em|rem|%)?\b", re.IGNORECASE),
        "CSSに幅または高さを0にする指定があります。",
        "要素が実質的に表示されないことがあります。非表示目的でない場合はサイズ指定を見直してください。",
    ),
    (
        re.compile(r"\btext-indent\s*:\s*-[0-9.]+(?:px|em|rem|%)", re.IGNORECASE),
        "CSSに負の text-indent があり、テキストが画面外へ移動する可能性があります。",
        "見出しやリンク文字が見えなくなることがあるため、画像置換などの古い手法は避けてください。",
    ),
    (
        re.compile(r"\bposition\s*:\s*fixed\b", re.IGNORECASE),
        "CSSに position:fixed があり、画面固定表示になります。",
        "WordPress管理バー、モーダル、スマホ表示と重なりやすいため、通常記事内では不安定です。",
    ),
    (
        re.compile(r"\bz-index\s*:\s*(?:999|[1-9][0-9]{3,})\b", re.IGNORECASE),
        "CSSに大きい z-index があり、他のUIに重なる可能性があります。",
        "固定ヘッダーやポップアップが本文や操作UIを覆う原因になります。",
    ),
    (
        re.compile(r"\bcursor\s*:\s*(?:not-allowed|no-drop)\b", re.IGNORECASE),
        "CSSに操作不可を示す cursor 指定があります。",
        "ユーザーにクリックできない印象を与えるため、リンクやボタンに適用されていないか確認してください。",
    ),
    (
        re.compile(r"(?:::-webkit-scrollbar|\bscrollbar-width\s*:\s*none\b)", re.IGNORECASE),
        "CSSにスクロールバーを隠す指定があります。",
        "横長の表やコードブロックで、スクロール可能なことが分かりにくくなります。",
    ),
    (
        re.compile(r"@media\s+print\b", re.IGNORECASE),
        "CSSに印刷時だけの表示制御があります。",
        "印刷・PDF化で本文や画像が消える可能性があります。display:none と組み合わせていないか確認してください。",
    ),
    (
        re.compile(r"@import\b", re.IGNORECASE),
        "CSSに @import があり、外部CSS依存が増えます。",
        "事業所WPや高制限環境では外部CSSが読み込まれないことがあります。",
    ),
    (
        re.compile(r"url\(\s*['\"]?https?://", re.IGNORECASE),
        "CSSに外部URL参照があります。",
        "外部画像・フォント・CSSは制限環境で読み込まれないことがあります。",
    ),
)


def lint_wp_html(load_file: str, mode: str = HIGH_SECURITY_MODE) -> list[LintIssue]:
    """WordPress HTML文字列を検査して、問題一覧を返します。"""
    normalized_mode = normalize_conversion_mode(mode)
    issues: list[LintIssue] = []
    issues.extend(_lint_block_comments(load_file, normalized_mode))
    issues.extend(_lint_html_tags(load_file, normalized_mode))
    return sorted(issues, key=lambda issue: issue.line_number)


def lint_css(load_file: str) -> list[LintIssue]:
    """CSS文字列を検査して、表示・操作制限になりやすい指定を返します。"""
    issues: list[LintIssue] = []
    issues.extend(_lint_css_braces(load_file))
    issues.extend(_lint_css_restrictions(load_file))
    return sorted(issues, key=lambda issue: issue.line_number)


def lint_file(
    load_file_path: str | Path,
    mode: str = HIGH_SECURITY_MODE,
    input_type: str = INPUT_TYPE_AUTO,
) -> list[LintIssue]:
    """ファイルを読み込んで、入力種別に応じたlintを実行します。"""
    load_file_path = Path(load_file_path)
    load_file = load_file_path.read_text(encoding="utf-8-sig")
    resolved_input_type = _resolve_lint_input_type(load_file_path, load_file, input_type)
    if resolved_input_type == INPUT_TYPE_CSS:
        return lint_css(load_file)
    return lint_wp_html(load_file, mode=mode)


def main() -> None:
    """CLIからWordPress HTMLを検査します。"""
    parser = argparse.ArgumentParser(
        description="WordPressブロックHTMLとCSSの表示制限を確認します。"
    )
    parser.add_argument("load_file_path", help="検査したい.wp_html、HTML、CSSファイルのパス")
    parser.add_argument(
        "--mode",
        choices=(NORMAL_MODE, *SAFE_CONVERSION_MODES),
        default=HIGH_SECURITY_MODE,
        help="想定する変換モードです。normalでは非normal向け表示警告を出しません。",
    )
    parser.add_argument(
        "--input-type",
        choices=LINT_INPUT_TYPES,
        default=INPUT_TYPE_AUTO,
        help="lint対象の種類です。autoでは拡張子と内容から自動判定します。",
    )
    args = parser.parse_args()

    issues = lint_file(args.load_file_path, mode=args.mode, input_type=args.input_type)
    if not issues:
        print("問題は見つかりませんでした。")
        return

    for issue in issues:
        print(issue.format())

    raise SystemExit(1)


def _lint_block_comments(load_file: str, mode: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    block_stack: list[dict[str, str | int]] = []
    should_lint_non_normal = mode in SAFE_CONVERSION_MODES

    for line_number, line in enumerate(load_file.splitlines(), start=1):
        for block_match in BLOCK_COMMENT_PATTERN.finditer(line):
            is_end_comment = bool(block_match.group(1))
            block_name = _normalize_block_comment_name(block_match.group(2))
            block_attrs = block_match.group(3) or ""
            _lint_unknown_core_block_comment(
                issues,
                block_name,
                is_end_comment,
                line_number,
            )
            _lint_raw_html_block_comment(
                issues,
                block_stack,
                block_name,
                is_end_comment,
                line_number,
            )
            _lint_block_comment_inside_paragraph(
                issues,
                block_stack,
                block_name,
                is_end_comment,
                line_number,
            )
            if should_lint_non_normal and not is_end_comment:
                _lint_non_normal_core_block(issues, block_name, line_number)

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


def _lint_non_normal_core_block(
    issues: list[LintIssue],
    block_name: str,
    line_number: int,
) -> None:
    block_rule = NON_NORMAL_UNSTABLE_CORE_BLOCKS.get(block_name)
    if block_rule is None:
        return

    issues.append(LintIssue(
        line_number,
        block_rule["message"],
        block_rule["hint"],
    ))


def _normalize_block_comment_name(block_name: str) -> str:
    clean_block_name = block_name.strip().lower()
    if clean_block_name.startswith("core/"):
        return clean_block_name.removeprefix("core/")
    return clean_block_name


def _lint_unknown_core_block_comment(
    issues: list[LintIssue],
    block_name: str,
    is_end_comment: bool,
    line_number: int,
) -> None:
    if "/" in block_name:
        return
    if block_name in KNOWN_WORDPRESS_CORE_BLOCKS:
        return

    suggestion = _find_closest_word(block_name, KNOWN_WORDPRESS_CORE_BLOCKS)
    open_or_close = "閉じる" if is_end_comment else "開始"
    hint = "WordPressコアブロック名のtypo、または未登録の独自ブロックでないか確認してください。"
    if suggestion:
        hint = f"もしかして wp:{suggestion} ではありませんか。コアブロック名を確認してください。"

    issues.append(LintIssue(
        line_number,
        f"{open_or_close} wp:{block_name} ブロックコメントは既知のコアブロック名ではありません。",
        hint,
    ))


def _lint_block_comment_inside_paragraph(
    issues: list[LintIssue],
    block_stack: list[dict[str, str | int]],
    block_name: str,
    is_end_comment: bool,
    line_number: int,
) -> None:
    if is_end_comment and block_name == "paragraph":
        return
    if _find_open_block_name(block_stack, "paragraph") is None:
        return

    issues.append(LintIssue(
        line_number,
        f"paragraph ブロック内に wp:{block_name} ブロックコメントがあります。",
        "独立ブロックは paragraph の外に出し、paragraph / code / paragraph のように兄弟ブロックとして並べてください。",
    ))


def _lint_raw_html_block_comment(
    issues: list[LintIssue],
    block_stack: list[dict[str, str | int]],
    block_name: str,
    is_end_comment: bool,
    line_number: int,
) -> None:
    raw_block_name = _find_open_raw_html_block_name(block_stack)
    if raw_block_name is None:
        return

    if is_end_comment and block_name == raw_block_name:
        return

    issues.append(LintIssue(
        line_number,
        f"wp:{raw_block_name} ブロック内に生の wp:{block_name} コメントがあります。",
        f"wp:{raw_block_name} の中では、ブロックコメントを &lt;!-- wp:{block_name} --&gt; のように文字として書いてください。",
    ))


def _find_open_block_name(block_stack: list[dict[str, str | int]], target_block_name: str) -> str | None:
    for block_info in reversed(block_stack):
        block_name = str(block_info["name"])
        if block_name == target_block_name:
            return block_name

    return None


def _find_open_raw_html_block_name(block_stack: list[dict[str, str | int]]) -> str | None:
    for block_info in reversed(block_stack):
        block_name = str(block_info["name"])
        if block_name in RAW_HTML_BLOCK_NAMES:
            return block_name

    return None


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
    else:
        _lint_paragraph_inner_blank_lines(issues, content, line_number)


def _lint_paragraph_inner_blank_lines(
    issues: list[LintIssue],
    content: str,
    line_number: int,
) -> None:
    for paragraph_match in PARAGRAPH_CONTENT_PATTERN.finditer(content):
        paragraph_body = paragraph_match.group(1)
        blank_line_match = PARAGRAPH_INNER_BLANK_LINE_PATTERN.search(paragraph_body)
        if blank_line_match is None:
            continue

        issue_line_number = (
            line_number
            + content[:paragraph_match.start(1)].count("\n")
            + paragraph_body[:blank_line_match.start()].count("\n")
            + 1
        )
        issues.append(LintIssue(
            issue_line_number,
            "paragraph ブロック内の <p> に空行があります。",
            "<p> の中に人間向けの空行を入れず、<br><br> を詰めるか、別の paragraph ブロックへ分けてください。",
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


def _lint_html_tags(load_file: str, mode: str) -> list[LintIssue]:
    parser = WpHtmlTagLintParser(mode)
    parser.feed(load_file)
    parser.close()
    return parser.issues


def _resolve_lint_input_type(load_file_path: Path, load_file: str, input_type: str) -> str:
    if input_type != INPUT_TYPE_AUTO:
        return input_type
    if load_file_path.suffix.lower() in CSS_EXTENSIONS:
        return INPUT_TYPE_CSS
    if "<!-- wp:" in load_file:
        return INPUT_TYPE_WP_HTML
    return INPUT_TYPE_WP_HTML


def _lint_css_braces(load_file: str) -> list[LintIssue]:
    css_without_comments = CSS_COMMENT_PATTERN.sub("", load_file)
    if css_without_comments.count("{") == css_without_comments.count("}"):
        return []

    return [LintIssue(
        1,
        "CSSの波括弧 { } の数が一致していません。",
        "閉じ忘れや余分な } があると、それ以降のCSSがまとめて効かなくなることがあります。",
    )]


def _lint_css_restrictions(load_file: str) -> list[LintIssue]:
    issues: list[LintIssue] = []
    in_block_comment = False
    for line_number, raw_line in enumerate(load_file.splitlines(), start=1):
        line, in_block_comment = _remove_css_comments_from_line(raw_line, in_block_comment)
        if not line.strip():
            continue

        for pattern, message, hint in CSS_RESTRICTION_RULES:
            if not pattern.search(line):
                continue
            issues.append(LintIssue(line_number, message, hint))

    return issues


def _remove_css_comments_from_line(line: str, in_block_comment: bool) -> tuple[str, bool]:
    output = ""
    index = 0
    while index < len(line):
        if in_block_comment:
            comment_end = line.find("*/", index)
            if comment_end == -1:
                return output, True
            index = comment_end + 2
            in_block_comment = False
            continue

        comment_start = line.find("/*", index)
        if comment_start == -1:
            output = f"{output}{line[index:]}"
            return output, False

        output = f"{output}{line[index:comment_start]}"
        comment_end = line.find("*/", comment_start + 2)
        if comment_end == -1:
            return output, True
        index = comment_end + 2

    return output, in_block_comment


def _find_closest_word(word: str, choices: set[str]) -> str | None:
    matches = get_close_matches(word, sorted(choices), n=1, cutoff=0.72)
    if not matches:
        return None
    return matches[0]


class WpHtmlTagLintParser(HTMLParser):
    """HTMLタグの閉じ忘れと属性不足を確認するHTMLParserです。"""

    def __init__(self, mode: str) -> None:
        super().__init__(convert_charrefs=False)
        self._should_lint_non_normal = mode in SAFE_CONVERSION_MODES
        self.issues: list[LintIssue] = []
        self._open_tags: list[tuple[str, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = tag.lower()
        attrs_dict = {name.lower(): value or "" for name, value in attrs}
        line_number = self.getpos()[0]

        self._lint_unknown_html_tag(clean_tag, line_number)
        self._lint_dangerous_tag(clean_tag, line_number)
        self._lint_dangerous_attributes(clean_tag, attrs_dict, line_number)
        self._lint_display_unstable_attributes(clean_tag, attrs_dict, line_number)

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

        self._lint_unknown_html_tag(clean_tag, line_number)
        self._lint_dangerous_tag(clean_tag, line_number)
        self._lint_dangerous_attributes(clean_tag, attrs_dict, line_number)
        self._lint_display_unstable_attributes(clean_tag, attrs_dict, line_number)

        if clean_tag == "a":
            self._lint_anchor(attrs_dict, line_number)
        elif clean_tag == "img":
            self._lint_image(attrs_dict, line_number)

    def handle_endtag(self, tag: str) -> None:
        clean_tag = tag.lower()
        line_number = self.getpos()[0]

        self._lint_unknown_html_tag(clean_tag, line_number)

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

    def _lint_unknown_html_tag(self, tag: str, line_number: int) -> None:
        if tag in KNOWN_HTML_TAGS:
            return
        if "-" in tag or ":" in tag:
            return

        suggestion = COMMON_HTML_TAG_TYPOS.get(tag)
        if suggestion is None:
            suggestion = _find_closest_word(tag, KNOWN_HTML_TAGS)

        hint = "HTMLタグ名のtypo、またはWordPressで使わない独自タグでないか確認してください。"
        if suggestion:
            hint = f"もしかして <{suggestion}> ではありませんか。タグ名を確認してください。"

        self.issues.append(LintIssue(
            line_number,
            f"<{tag}> は既知のHTMLタグではありません。",
            hint,
        ))

    def _lint_dangerous_tag(self, tag: str, line_number: int) -> None:
        if not self._should_lint_non_normal:
            return
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
        if not self._should_lint_non_normal:
            return

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

    def _lint_display_unstable_attributes(
        self,
        tag: str,
        attrs: dict[str, str],
        line_number: int,
    ) -> None:
        if not self._should_lint_non_normal:
            return

        class_value = attrs.get("class", "")
        if class_value:
            class_names = {
                class_name.strip().lower()
                for class_name in re.split(r"\s+", class_value)
                if class_name.strip()
            }
            for keyword, reason in DISPLAY_UNSTABLE_CLASS_KEYWORDS.items():
                if keyword not in class_names:
                    continue
                self.issues.append(LintIssue(
                    line_number,
                    f"<{tag}> タグの class に表示が不安定になりやすい指定 '{keyword}' があります。",
                    f"{reason} エディタ側ではこの警告文をホバー表示のツールチップとして使えます。",
                ))

        style_value = attrs.get("style", "").lower()
        if not style_value:
            return

        for css_text, reason in (
            ("display:none", "要素が表示されません。"),
            ("display: none", "要素が表示されません。"),
            ("visibility:hidden", "領域だけ残して見えなくなります。"),
            ("visibility: hidden", "領域だけ残して見えなくなります。"),
            ("opacity:0", "透明化され、見えないまま操作判定だけ残ることがあります。"),
            ("opacity: 0", "透明化され、見えないまま操作判定だけ残ることがあります。"),
            ("pointer-events:none", "クリックやタップが効かなくなります。"),
            ("pointer-events: none", "クリックやタップが効かなくなります。"),
            ("user-select:none", "テキスト選択やコピーがしづらくなります。"),
            ("user-select: none", "テキスト選択やコピーがしづらくなります。"),
            ("overflow:hidden", "はみ出した内容やスクロールが隠れます。"),
            ("overflow: hidden", "はみ出した内容やスクロールが隠れます。"),
        ):
            if css_text not in style_value:
                continue
            self.issues.append(LintIssue(
                line_number,
                f"<{tag}> タグの style に表示・操作を制限する指定があります。",
                f"{reason} middle / high-security modeではstyleを使わず標準ブロックへ寄せてください。",
            ))
            return

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
