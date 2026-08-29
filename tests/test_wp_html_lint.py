"""wp_html_lint機能のテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from lint import lint_wp_html


def test_lint_reports_unclosed_paragraph_block() -> None:
    """paragraphブロックコメントの閉じ忘れを検出するテストです。"""
    load_file = "<!-- wp:paragraph -->\n<p>本文</p>\n"

    issues = lint_wp_html(load_file)

    assert any("wp:paragraph ブロックが閉じられていません" in issue.message for issue in issues)


def test_lint_reports_missing_paragraph_end_tag() -> None:
    """paragraph内のp閉じ忘れを検出するテストです。"""
    load_file = "<!-- wp:paragraph -->\n<p>本文\n<!-- /wp:paragraph -->"

    issues = lint_wp_html(load_file)

    assert any("paragraph ブロック内の <p> が閉じられていません" in issue.message for issue in issues)


def test_lint_reports_empty_paragraph_block() -> None:
    """空のparagraphブロックを検出するテストです。"""
    load_file = "<!-- wp:paragraph -->\n<p></p>\n<!-- /wp:paragraph -->"

    issues = lint_wp_html(load_file)

    assert any(
        issue.line_number == 2 and issue.message == "paragraph ブロックが空です。"
        for issue in issues
    )


def test_lint_reports_blank_like_paragraph_block() -> None:
    """空白やbrだけのparagraphブロックを検出するテストです。"""
    load_file = "<!-- wp:paragraph -->\n<p> <br> &nbsp; </p>\n<!-- /wp:paragraph -->"

    issues = lint_wp_html(load_file)

    assert any(issue.message == "paragraph ブロックが空です。" for issue in issues)


def test_lint_reports_nested_html_tag_mismatch() -> None:
    """HTMLタグの入れ子ミスを検出するテストです。"""
    load_file = "<p><strong>大事な文章</p>"

    issues = lint_wp_html(load_file)

    assert any("<strong> が閉じられていません" in issue.message for issue in issues)
    assert any("</strong> を </p> より前に追加してください" in issue.hint for issue in issues)


def test_lint_reports_dangerous_tags_attributes_and_urls() -> None:
    """危険タグ、危険属性、危険URLを警告するテストです。"""
    load_file = (
        "<script>alert(1)</script>\n"
        '<iframe src="https://example.com"></iframe>\n'
        "<style>p{color:red}</style>\n"
        '<p onclick="alert(1)" style="color:red">本文</p>\n'
        '<a href="javascript:alert(1)">危険リンク</a>\n'
        '<img src="data:image/png;base64,abc" alt="危険画像">\n'
    )

    issues = lint_wp_html(load_file)

    assert any("<script> はHi-Security / office modeでは危険扱いです" in issue.message for issue in issues)
    assert any("<iframe> はHi-Security / office modeでは危険扱いです" in issue.message for issue in issues)
    assert any("<style> はHi-Security / office modeでは危険扱いです" in issue.message for issue in issues)
    assert any("属性 onclick" in issue.message for issue in issues)
    assert any("属性 style" in issue.message for issue in issues)
    assert any("危険なURL" in issue.message for issue in issues)


def test_lint_reports_office_blocked_tags() -> None:
    """事業所WP向けに危険扱いするタグを警告するテストです。"""
    load_file = (
        '<object data="sample.swf"></object>\n'
        '<embed src="sample.swf">\n'
        '<form action="/send"></form>\n'
        '<input type="text">\n'
        '<button>送信</button>\n'
        '<textarea>本文</textarea>\n'
        '<select><option>項目</option></select>\n'
    )

    issues = lint_wp_html(load_file)

    for tag_name in ("object", "embed", "form", "input", "button", "textarea", "select"):
        assert any(
            f"<{tag_name}> はHi-Security / office modeでは危険扱いです" in issue.message
            for issue in issues
        )


def test_lint_reports_heading_level_mismatch() -> None:
    """headingのlevelとHTML見出しタグ不一致を検出するテストです。"""
    load_file = (
        '<!-- wp:heading {"level":3} -->\n'
        '<h2 class="wp-block-heading">小見出し</h2>\n'
        "<!-- /wp:heading -->"
    )

    issues = lint_wp_html(load_file)

    assert any("wp:heading level=3" in issue.message for issue in issues)


def test_lint_reports_missing_heading_level() -> None:
    """headingのlevel未指定を検出するテストです。"""
    load_file = (
        "<!-- wp:heading -->\n"
        '<h2 class="wp-block-heading">見出し</h2>\n'
        "<!-- /wp:heading -->"
    )

    issues = lint_wp_html(load_file)

    assert any("level が明記されていません" in issue.message for issue in issues)


def test_lint_reports_table_missing_figure_and_table() -> None:
    """tableブロック内のfigure/table不足を検出するテストです。"""
    load_file = "<!-- wp:table -->\n<p>表ではありません</p>\n<!-- /wp:table -->"

    issues = lint_wp_html(load_file)

    assert any('figure class="wp-block-table"' in issue.message for issue in issues)
    assert any("<table> がありません" in issue.message for issue in issues)


def test_lint_reports_anchor_and_image_attribute_issues() -> None:
    """a/img属性不足を検出するテストです。"""
    load_file = (
        '<p><a target="_blank">リンク</a></p>\n'
        '<p><a href="https://example.com" target="_blank">別窓</a></p>\n'
        '<img src="https://example.com/image.jpg">\n'
        '<img alt="説明">\n'
    )

    issues = lint_wp_html(load_file)

    assert any("<a> タグに href がありません" in issue.message for issue in issues)
    assert any('rel="noopener" がありません' in issue.message for issue in issues)
    assert any("<img> タグに alt がありません" in issue.message for issue in issues)
    assert any("<img> タグに src がありません" in issue.message for issue in issues)


def test_lint_passes_safe_wp_html() -> None:
    """安全なWP_HTMLでは問題を出さないテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p>本文<a href=\"https://example.com\" target=\"_blank\" rel=\"noopener\">リンク</a></p>\n"
        "<!-- /wp:paragraph -->\n\n"
        '<!-- wp:heading {"level":3} -->\n'
        '<h3 class="wp-block-heading">小見出し</h3>\n'
        "<!-- /wp:heading -->\n\n"
        "<!-- wp:table -->\n"
        '<figure class="wp-block-table"><table><tbody><tr><td>内容</td></tr></tbody></table></figure>\n'
        "<!-- /wp:table -->\n"
        '<img src="https://example.com/image.jpg" alt="説明">'
    )

    issues = lint_wp_html(load_file)

    assert issues == []
