"""Markdown編集用lintの回帰テストです。"""
from __future__ import annotations

from text_editor.markdown_linter import lint_markdown


def test_markdown_lint_accepts_standard_editor_template() -> None:
    load_file = (
        "## 見出し\n\n"
        "- 項目\n\n"
        "[公式](https://example.com/)\n\n"
        "```\nprint('ok')\n```"
    )

    assert lint_markdown(load_file) == []


def test_markdown_lint_reports_unclosed_code_fence() -> None:
    issues = lint_markdown("本文\n\n```\nprint('open')")

    assert len(issues) == 1
    assert issues[0].line == 3
    assert issues[0].level == "error"
    assert "コードブロック" in issues[0].message


def test_markdown_lint_reports_heading_without_space() -> None:
    issues = lint_markdown("##見出し")

    assert len(issues) == 1
    assert issues[0].level == "warning"
    assert "半角スペース" in issues[0].message


def test_markdown_lint_reports_unclosed_link_parenthesis() -> None:
    issues = lint_markdown("[公式](https://example.com/")

    assert len(issues) == 1
    assert issues[0].level == "error"
    assert "閉じ丸括弧" in issues[0].message


def test_markdown_lint_reports_unpaired_inline_backtick() -> None:
    issues = lint_markdown("`font-size を使います。")

    assert len(issues) == 1
    assert issues[0].level == "warning"
    assert "バッククォート" in issues[0].message


def test_markdown_lint_ignores_markdown_symbols_inside_code_fence() -> None:
    load_file = "```\n##見出し\n[リンク](broken\n`code\n```"

    assert lint_markdown(load_file) == []
