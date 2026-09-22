"""wp_html_lint機能のテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from unittest.mock import patch

from lint import lint_css, lint_file, lint_wp_html


def test_lint_reports_unclosed_paragraph_block() -> None:
    """paragraphブロックコメントの閉じ忘れを検出するテストです。"""
    load_file = "<!-- wp:paragraph -->\n<p>本文</p>\n"

    issues = lint_wp_html(load_file)

    assert any("wp:paragraph ブロックが閉じられていません" in issue.message for issue in issues)


def test_lint_reports_group_block_comment_missing_end_slash() -> None:
    """groupの閉じコメントで / が抜けた事故を検出するテストです。"""
    load_file = (
        "<!-- wp:group -->\n"
        "<div>本文</div>\n"
        "<!-- wp:group -->"
    )

    issues = lint_wp_html(load_file, mode="normal")

    assert any("/ が抜けている可能性" in issue.message for issue in issues)
    assert any("wp:group ブロックが閉じられていません" in issue.message for issue in issues)


def test_lint_reports_malformed_angle_brackets() -> None:
    """< や > の重複、タグの > 抜けを検出するテストです。"""
    load_file = "<<p>本文</p>\n<p>本文</p>>\n<p class=\"note\""

    issues = lint_wp_html(load_file, mode="normal")

    assert any('"<<"' in issue.message for issue in issues)
    assert any('">>"' in issue.message for issue in issues)
    assert any('" が抜けている可能性' in issue.message for issue in issues)


def test_lint_reports_malformed_block_comment() -> None:
    """WPブロックコメントの > や --> 抜けを検出するテストです。"""
    load_file = "<!-- wp:paragraph --\n<p>本文</p>\n<!-- /wp:paragraph -->"

    issues = lint_wp_html(load_file, mode="normal")

    assert any("--> がありません" in issue.message for issue in issues)


def test_lint_reports_malformed_block_comment_attrs() -> None:
    """WPブロックコメントのJSONパラメータ崩れを検出するテストです。"""
    load_file = (
        "<!-- wp:heading {level:3} -->\n"
        '<h3 class="wp-block-heading">見出し</h3>\n'
        "<!-- /wp:heading -->"
    )

    issues = lint_wp_html(load_file, mode="normal")

    assert any("パラメータJSONが壊れています" in issue.message for issue in issues)


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


def test_lint_reports_unclosed_html_tag_inside_core_block() -> None:
    """コアブロック内のHTMLタグ閉じ忘れを検出するテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p><strong>重要な本文</p>\n"
        "<!-- /wp:paragraph -->"
    )

    issues = lint_wp_html(load_file)

    assert any("<strong> が閉じられていません" in issue.message for issue in issues)
    assert any("</strong> を </p> より前に追加してください" in issue.hint for issue in issues)


def test_lint_reports_html_tag_typo_in_plain_html() -> None:
    """HTML単体でもタグ名typoを検出するテストです。"""
    load_file = "<p><strnog>重要</strnog></p>"

    issues = lint_wp_html(load_file, mode="normal")

    assert any("<strnog> は既知のHTMLタグではありません" in issue.message for issue in issues)
    assert any("<strong>" in issue.hint for issue in issues)


def test_lint_reports_html_tag_typo_inside_core_block() -> None:
    """WP_HTML内でもタグ名typoを検出するテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p><spna>本文</spna></p>\n"
        "<!-- /wp:paragraph -->"
    )

    issues = lint_wp_html(load_file, mode="normal")

    assert any("<spna> は既知のHTMLタグではありません" in issue.message for issue in issues)
    assert any("<span>" in issue.hint for issue in issues)


def test_lint_reports_html_attribute_typo() -> None:
    """HTML属性名のよくあるtypoを検出するテストです。"""
    load_file = '<p clas="lead"><a herf="https://example.com">リンク</a></p>'

    issues = lint_wp_html(load_file, mode="normal")

    assert any("属性 clas はlint参照用JSONにない綴り" in issue.message for issue in issues)
    assert any("class=" in issue.hint for issue in issues)
    assert any("属性 herf はlint参照用JSONにない綴り" in issue.message for issue in issues)
    assert any("href=" in issue.hint for issue in issues)


def test_lint_uses_startup_reference_cache_without_rereading_json() -> None:
    """lint実行時は起動時キャッシュを使い、参照JSONを読み直さないテストです。"""
    with patch("pathlib.Path.read_text") as read_text:
        issues = lint_wp_html('<p clas="lead">本文</p>', mode="normal")

    read_text.assert_not_called()
    assert any("属性 clas はlint参照用JSONにない綴り" in issue.message for issue in issues)


def test_lint_accepts_reference_json_attribute_prefixes() -> None:
    """参照JSONで許可した属性prefixはtypo警告しないテストです。"""
    load_file = '<p data-note-id="1" aria-label="説明">本文</p>'

    issues = lint_wp_html(load_file, mode="normal")

    assert not any("lint参照用JSONにない綴り" in issue.message for issue in issues)


def test_lint_reports_core_block_name_typo() -> None:
    """WPコアブロック名typoを検出するテストです。"""
    load_file = (
        "<!-- wp:paragaph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:paragaph -->"
    )

    issues = lint_wp_html(load_file)

    assert any("wp:paragaph ブロックコメントは既知のコアブロック名ではありません" in issue.message for issue in issues)
    assert any("wp:paragraph" in issue.hint for issue in issues)


def test_lint_accepts_core_prefixed_block_comments() -> None:
    """core/付きWPコアブロックコメントも同じコアブロックとして検査するテストです。"""
    load_file = (
        "<!-- wp:core/paragraph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:core/paragraph -->"
    )

    issues = lint_wp_html(load_file, mode="normal")

    assert issues == []


def test_lint_reports_dangerous_tags_attributes_and_urls() -> None:
    """危険タグ、危険属性、危険URLを警告するテストです。"""
    load_file = (
        "<script>alert(1)</script>\n"
        '<iframe src="https://example.com"></iframe>\n'
        "<style>p{color:red}</style>\n"
        '<p onclick="alert(1)" style="color:red">本文</p>\n'
        '<a href="javascript:alert(1)">危険リンク</a>\n'
        '<a href="http://example.com">httpリンク</a>\n'
        '<img src="data:image/png;base64,abc" alt="危険画像">\n'
    )

    issues = lint_wp_html(load_file, mode="high-security")

    assert any("<script> はmiddle / high-security modeでは危険扱いです" in issue.message for issue in issues)
    assert any("<iframe> はmiddle / high-security modeでは危険扱いです" in issue.message for issue in issues)
    assert any("<style> はmiddle / high-security modeでは危険扱いです" in issue.message for issue in issues)
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

    issues = lint_wp_html(load_file, mode="high-security")

    for tag_name in ("object", "embed", "form", "input", "button", "textarea", "select"):
        assert any(
            f"<{tag_name}> はmiddle / high-security modeでは危険扱いです" in issue.message
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


def test_lint_reports_raw_block_comment_inside_html_block() -> None:
    """htmlブロック内の生ブロックコメントを検出するテストです。"""
    load_file = (
        "<!-- wp:html -->\n"
        "<div>説明</div>\n"
        "<!-- wp:paragraph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- /wp:html -->"
    )

    issues = lint_wp_html(load_file)

    assert any("wp:html ブロック内に生の wp:paragraph コメント" in issue.message for issue in issues)


def test_lint_reports_raw_block_comment_inside_code_block() -> None:
    """codeブロック内の生ブロックコメントを検出するテストです。"""
    load_file = (
        "<!-- wp:code -->\n"
        '<pre class="wp-block-code"><code>\n'
        "<!-- wp:paragraph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:paragraph -->\n"
        "</code></pre>\n"
        "<!-- /wp:code -->"
    )

    issues = lint_wp_html(load_file)

    assert any("wp:code ブロック内に生の wp:paragraph コメント" in issue.message for issue in issues)


def test_lint_reports_block_comment_inside_paragraph_block() -> None:
    """paragraphブロック内の独立ブロックコメントを検出するテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p>文章です。\n"
        "<!-- wp:code -->\n"
        '<pre class="wp-block-code"><code>print("hello")</code></pre>\n'
        "<!-- /wp:code -->\n"
        "文章の続きです。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    issues = lint_wp_html(load_file)

    assert any("paragraph ブロック内に wp:code ブロックコメント" in issue.message for issue in issues)


def test_lint_reports_unstable_nested_core_block() -> None:
    """入れ子が不安定になりやすいコアブロック組み合わせを警告するテストです。"""
    load_file = (
        "<!-- wp:heading -->\n"
        '<h2 class="wp-block-heading">見出し</h2>\n'
        "<!-- wp:paragraph -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- /wp:heading -->"
    )

    issues = lint_wp_html(load_file, mode="normal")

    assert any("wp:heading ブロック内に wp:paragraph ブロック" in issue.message for issue in issues)


def test_lint_reports_non_normal_unstable_core_blocks() -> None:
    """非normalモードで表示が不安定なコアブロックを警告するテストです。"""
    load_file = (
        "<!-- wp:embed -->\n"
        '<figure class="wp-block-embed"><div>https://www.youtube.com/watch?v=test</div></figure>\n'
        "<!-- /wp:embed -->\n"
        "<!-- wp:shortcode -->\n"
        "[contact-form-7 id=\"1\"]\n"
        "<!-- /wp:shortcode -->\n"
        "<!-- wp:columns -->\n"
        "<!-- wp:column -->\n"
        "<p>本文</p>\n"
        "<!-- /wp:column -->\n"
        "<!-- /wp:columns -->\n"
    )

    issues = lint_wp_html(load_file, mode="middle")

    assert any("core/embed" in issue.message and "表示されない" in issue.message for issue in issues)
    assert any("core/shortcode" in issue.message and "実行されない" in issue.message for issue in issues)
    assert any("core/columns" in issue.message and "列崩れ" in issue.message for issue in issues)
    assert any("core/column" in issue.message and "不安定" in issue.message for issue in issues)


def test_lint_skips_non_normal_display_warnings_in_normal_mode() -> None:
    """normalモードでは非normal向けの表示警告を出さないテストです。"""
    load_file = (
        "<!-- wp:embed -->\n"
        '<figure class="wp-block-embed"><div>https://www.youtube.com/watch?v=test</div></figure>\n'
        "<!-- /wp:embed -->\n"
        '<p class="hidden-post" style="display:none">本文</p>\n'
        "<script>alert(1)</script>\n"
    )

    issues = lint_wp_html(load_file, mode="normal")

    assert not any("core/embed" in issue.message for issue in issues)
    assert not any("表示が不安定" in issue.message for issue in issues)
    assert not any("危険扱い" in issue.message for issue in issues)


def test_lint_reports_display_unstable_classes_and_styles() -> None:
    """非normalモードでCSS由来の非表示・不安定表示を警告するテストです。"""
    load_file = (
        '<p class="hidden-post samearea-otheroffice">非表示候補</p>\n'
        '<p class="swiper modal">JS依存候補</p>\n'
        '<p style="pointer-events:none">クリック不可候補</p>\n'
    )

    issues = lint_wp_html(load_file, mode="high-security")

    assert any("hidden-post" in issue.message for issue in issues)
    assert any("samearea-otheroffice" in issue.message for issue in issues)
    assert any("swiper" in issue.message for issue in issues)
    assert any("modal" in issue.message for issue in issues)
    assert any("style に表示・操作を制限する指定" in issue.message for issue in issues)
    assert any("ホバー表示のツールチップ" in issue.hint for issue in issues)


def test_lint_css_reports_display_restrictions() -> None:
    """CSSファイルモードで表示・操作制限を検出するテストです。"""
    load_file = (
        ".hidden-post { display: none; }\n"
        ".cta { pointer-events: none; opacity: 0; }\n"
        ".table-wrap { overflow-x: hidden; }\n"
        "@import url('https://example.com/base.css');\n"
    )

    issues = lint_css(load_file)

    assert any("display:none" in issue.message for issue in issues)
    assert any("pointer-events:none" in issue.message for issue in issues)
    assert any("opacity:0" in issue.message for issue in issues)
    assert any("overflow:hidden" in issue.message for issue in issues)
    assert any("@import" in issue.message for issue in issues)


def test_lint_css_ignores_commented_restrictions() -> None:
    """コメント内のCSS制限指定は警告しないテストです。"""
    load_file = (
        "/* .old { display: none; }\n"
        ".old-link { pointer-events: none; } */\n"
        ".active { display: block; }\n"
    )

    issues = lint_css(load_file)

    assert issues == []


def test_lint_file_auto_detects_css(tmp_path) -> None:
    """拡張子.cssのファイルはCSSファイルモードとして検査するテストです。"""
    css_path = tmp_path / "style.css"
    css_path.write_text(".modal { visibility: hidden; }", encoding="utf-8")

    issues = lint_file(css_path)

    assert any("visibility:hidden" in issue.message for issue in issues)


def test_lint_css_reports_unmatched_braces() -> None:
    """CSSの波括弧不一致を検出するテストです。"""
    issues = lint_css(".card { display: block;")

    assert any("波括弧" in issue.message for issue in issues)


def test_lint_passes_inline_code_inside_paragraph_block() -> None:
    """paragraphブロック内のインラインcodeタグは通すテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p>Pythonでは <code>print()</code> を使います。</p>\n"
        "<!-- /wp:paragraph -->"
    )

    issues = lint_wp_html(load_file)

    assert issues == []


def test_lint_passes_escaped_block_comment_inside_code_block() -> None:
    """codeブロック内のエスケープ済みブロックコメントは通すテストです。"""
    load_file = (
        "<!-- wp:code -->\n"
        '<pre class="wp-block-code"><code>\n'
        "&lt;!-- wp:paragraph --&gt;\n"
        "&lt;p&gt;本文&lt;/p&gt;\n"
        "&lt;!-- /wp:paragraph --&gt;\n"
        "</code></pre>\n"
        "<!-- /wp:code -->"
    )

    issues = lint_wp_html(load_file)

    assert issues == []


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
