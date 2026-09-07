"""prewp_txt linterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from text_editor.linter import lint_prewp_txt


def test_lint_reports_unclosed_emphasis_code_marker() -> None:
    """強調コードの閉じ忘れを検出するテストです。"""
    issues = lint_prewp_txt("[強調コード]\nfunctions.php")

    assert any(issue.level == "error" and "強調コード" in issue.message for issue in issues)


def test_lint_reports_unclosed_code_marker() -> None:
    """コードの閉じ忘れを検出するテストです。"""
    issues = lint_prewp_txt("[コード]\nprint('hello')")

    assert any(issue.level == "error" and "コード" in issue.message for issue in issues)


def test_lint_reports_unclosed_table_marker() -> None:
    """表の閉じ忘れを検出するテストです。"""
    issues = lint_prewp_txt("[表]\n項目|説明")

    assert any(issue.level == "error" and "表" in issue.message for issue in issues)


def test_lint_reports_broken_link_marker() -> None:
    """不正なリンクマーカーを検出するテストです。"""
    issues = lint_prewp_txt("[リンク:公式サイト]")

    assert any(issue.level == "error" and "リンク" in issue.message for issue in issues)


def test_lint_reports_unclosed_link_marker() -> None:
    """閉じ]がないリンクマーカーを検出するテストです。"""
    issues = lint_prewp_txt("[リンク:公式サイト|https://example.com/")

    assert any(issue.level == "error" and "リンク" in issue.message for issue in issues)


def test_lint_reports_broken_image_marker() -> None:
    """不正な画像マーカーを検出するテストです。"""
    issues = lint_prewp_txt("[画像:https://example.com/image.jpg]")

    assert any(issue.level == "error" and "画像" in issue.message for issue in issues)


def test_lint_reports_unclosed_image_marker() -> None:
    """閉じ]がない画像マーカーを検出するテストです。"""
    issues = lint_prewp_txt("[画像:https://example.com/image.jpg|説明画像")

    assert any(issue.level == "error" and "画像" in issue.message for issue in issues)


def test_lint_reports_broken_spacer_marker() -> None:
    """不正な余白マーカーを検出するテストです。"""
    issues = lint_prewp_txt("[余白:abc]")

    assert any(issue.level == "error" and "余白" in issue.message for issue in issues)


def test_lint_reports_table_without_pipe() -> None:
    """表ブロック内に|がない場合に警告するテストです。"""
    issues = lint_prewp_txt("[表]\n項目 説明\n[/表]")

    assert any(issue.level == "warning" and "| がありません" in issue.message for issue in issues)


def test_lint_reports_empty_marker_body() -> None:
    """開始マーカーだけで本文が空のブロックを警告するテストです。"""
    issues = lint_prewp_txt("[コード]\n[/コード]")

    assert any(issue.level == "warning" and "本文が空" in issue.message for issue in issues)
