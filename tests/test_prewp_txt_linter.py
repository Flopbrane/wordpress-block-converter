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


def test_lint_reports_unclosed_box_marker() -> None:
    """囲い込みの閉じ忘れを検出するテストです。"""
    issues = lint_prewp_txt("[囲い込み]\n注意文です。")

    assert any(issue.level == "error" and "囲い込み" in issue.message for issue in issues)


def test_lint_reports_unclosed_new_semantic_markers() -> None:
    """追加した意味付きマーカーの閉じ忘れを検出するテストです。"""
    load_file = (
        "[HTML]\n"
        "<div>本文</div>\n\n"
        "[注意]\n"
        "注意文\n\n"
        "[補足]\n"
        "補足文\n\n"
        "[手順]\n"
        "手順1\n\n"
        "[画像横並び:24px]\n"
        "https://example.com/a.jpg"
    )

    issues = lint_prewp_txt(load_file)

    for marker_name in ("HTML", "注意", "補足", "手順", "画像横並び"):
        assert any(
            issue.level == "error" and marker_name in issue.message
            for issue in issues
        )


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
