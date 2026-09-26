"""HTML converterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.html_converter import convert_html_to_gutenberg


def test_convert_html_converts_unordered_list_to_list_block() -> None:
    """ul/liをWordPressのlist/list-itemブロックへ変換するテストです。"""
    load_file = "<ul><li>りんご</li><li>`code` の説明</li></ul>"

    save_file = convert_html_to_gutenberg(load_file)

    assert "<!-- wp:list -->" in save_file
    assert '<ul class="wp-block-list">' in save_file
    assert "<!-- wp:list-item -->" in save_file
    assert "<li>りんご</li>" in save_file
    assert "<li>`code` の説明</li>" in save_file
    assert "<!-- wp:html -->" not in save_file
    assert "<code>code</code>" not in save_file


def test_convert_html_converts_ordered_list_to_list_block() -> None:
    """ol/liをordered付きのWordPress listブロックへ変換するテストです。"""
    load_file = "<ol><li>最初</li><li>次</li></ol>"

    save_file = convert_html_to_gutenberg(load_file)

    assert '<!-- wp:list {"ordered":true} -->' in save_file
    assert '<ol class="wp-block-list">' in save_file
    assert "<!-- wp:list-item -->" in save_file
    assert "<li>最初</li>" in save_file
    assert "<li>次</li>" in save_file
    assert "<!-- wp:html -->" not in save_file


def test_convert_html_pre_code_is_display_code_not_executed_html() -> None:
    """pre/code内のHTMLは表示用コードとしてescapeするテストです。"""
    load_file = "<pre><code>&lt;h1&gt;Hello&lt;/h1&gt;</code></pre>"

    save_file = convert_html_to_gutenberg(load_file)

    assert "<!-- wp:code -->" in save_file
    assert "&lt;h1&gt;Hello&lt;/h1&gt;" in save_file
    assert "&amp;lt;h1&amp;gt;" not in save_file
    assert "<h1>Hello</h1>" not in save_file
    assert "<!-- /wp:code -->" in save_file


def test_convert_html_pre_code_keeps_indentation_and_line_breaks() -> None:
    """pre/code内のインデントと複数行改行を保持するテストです。"""
    load_file = (
        "<pre><code>if True:\n"
        "    print(&quot;Hello&quot;)\n"
        "    print(&quot;World&quot;)</code></pre>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert 'if True:\n    print("Hello")\n    print("World")' in save_file
    assert "<code>\nif True:" not in save_file


def test_convert_html_keeps_styled_div_article_as_custom_html() -> None:
    """囲み記事用のstyle付きdivは親子ごとCustom HTMLへ保護するテストです。"""
    load_file = (
        '<div style="border:1px solid #999;padding:16px 20px;'
        'border-radius:8px;background-color:#f9f9f9;max-width:720px">\n'
        '<p style="margin-top:0"><strong>目次</strong></p>\n'
        "<ul>\n"
        "<li>項目1</li>\n"
        "<li>項目2</li>\n"
        "</ul>\n"
        "</div>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert '<div style="border:1px solid #999;padding:16px 20px;' in save_file
    assert '<p style="margin-top:0"><strong>目次</strong></p>' in save_file
    assert "<li>項目1</li>" in save_file
    assert save_file.endswith("<!-- /wp:html -->")
    assert "<!-- wp:paragraph -->" not in save_file
    assert "<!-- wp:list -->" not in save_file


def test_convert_html_keeps_nested_styled_div_as_one_custom_html_block() -> None:
    """装飾付きdiv内の入れ子divも分解せず1つのCustom HTMLにするテストです。"""
    load_file = (
        '<div style="background:#fff;border:1px solid #ddd">'
        "<p>親の本文</p>"
        '<div class="inner"><p>子の本文</p></div>'
        "</div>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:html -->") == 1
    assert "<p>親の本文</p>" in save_file
    assert '<div class="inner"><p>子の本文</p></div>' in save_file
    assert "<!-- wp:paragraph -->" not in save_file


def test_convert_html_does_not_wrap_existing_custom_html_block_twice() -> None:
    """wp:html済みの入力を二重Custom HTMLにしないテストです。"""
    load_file = (
        "<!-- wp:html -->\n"
        '<div style="border:1px solid #999"><p>囲み記事</p></div>\n'
        "<!-- /wp:html -->"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file == load_file
    assert save_file.count("<!-- wp:html -->") == 1


def test_convert_html_removes_block_comments_inside_styled_div_article() -> None:
    """囲み枠内のGutenbergコメントを取り除き、通常HTMLだけで保護するテストです。"""
    load_file = (
        '<div style="border:2px solid #8bc34a;background-color:#f7fff2;padding:14px">\n'
        "<!-- wp:paragraph -->\n"
        "<p>本文です。</p>\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- wp:list -->\n"
        "<ul><li>確認1</li></ul>\n"
        "<!-- /wp:list -->\n"
        "</div>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:html -->") == 1
    assert "<!-- wp:paragraph -->" not in save_file
    assert "<!-- /wp:paragraph -->" not in save_file
    assert "<!-- wp:list -->" not in save_file
    assert "<p>本文です。</p>" in save_file
    assert "<ul><li>確認1</li></ul>" in save_file
    assert save_file.count("<!-- /wp:html -->") == 1


def test_convert_html_existing_custom_html_keeps_outer_block_but_removes_inner_comments() -> None:
    """既存wp:htmlは二重化せず、内部の別ブロックコメントだけ取り除くテストです。"""
    load_file = (
        "<!-- wp:html -->\n"
        '<div style="border:1px solid #999">\n'
        "<!-- wp:paragraph -->\n"
        "<p>囲み記事</p>\n"
        "<!-- /wp:paragraph -->\n"
        "</div>\n"
        "<!-- /wp:html -->"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:html -->") == 1
    assert save_file.count("<!-- /wp:html -->") == 1
    assert "<!-- wp:paragraph -->" not in save_file
    assert "<!-- /wp:paragraph -->" not in save_file
    assert "<p>囲み記事</p>" in save_file
