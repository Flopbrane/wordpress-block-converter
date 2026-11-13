"""text_editor向けの小さなMarkdown文法チェックです。"""
from __future__ import annotations

import re

from text_editor.linter import LintIssue

CODE_FENCE_PATTERN = re.compile(r"^\s*```")
HEADING_WITHOUT_SPACE_PATTERN = re.compile(r"^\s{0,3}#{1,6}[^#\s]")
LINK_START_PATTERN = re.compile(r"!?\[[^\]]*\]\(")
UNESCAPED_BACKTICK_PATTERN = re.compile(r"(?<!\\)`")


def lint_markdown(load_file: str) -> list[LintIssue]:
    """構造を壊しやすいMarkdown記法だけを確認します。"""
    issues: list[LintIssue] = []
    in_code_fence = False
    code_fence_start_line = 0

    for line_number, line in enumerate(load_file.splitlines(), start=1):
        if CODE_FENCE_PATTERN.match(line):
            if in_code_fence:
                in_code_fence = False
            else:
                in_code_fence = True
                code_fence_start_line = line_number
            continue
        if in_code_fence:
            continue

        if HEADING_WITHOUT_SPACE_PATTERN.match(line):
            issues.append(
                LintIssue(
                    "warning",
                    line_number,
                    "Markdown見出しの#直後に半角スペースがありません。",
                    "# 見出し、## 見出しのように半角スペースを入れてください。",
                )
            )

        for link_match in LINK_START_PATTERN.finditer(line):
            if ")" not in line[link_match.end():]:
                issues.append(
                    LintIssue(
                        "error",
                        line_number,
                        "Markdownリンクまたは画像の閉じ丸括弧がありません。",
                        "[表示名](URL) または ![代替テキスト](URL) の形にしてください。",
                    )
                )
                break

        inline_backticks = UNESCAPED_BACKTICK_PATTERN.findall(line)
        if len(inline_backticks) % 2:
            issues.append(
                LintIssue(
                    "warning",
                    line_number,
                    "インラインコードのバッククォートが対になっていません。",
                    "`code` のように、同じ行で前後を囲んでください。",
                )
            )

    if in_code_fence:
        issues.append(
            LintIssue(
                "error",
                code_fence_start_line,
                "Markdownコードブロックが閉じられていません。",
                "コードの最後に ``` を追加してください。",
            )
        )
    return issues
