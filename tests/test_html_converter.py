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


def test_convert_html_simple_table_uses_table_block() -> None:
    """styleなしの単純なHTML表はtableブロックへ変換するテストです。"""
    load_file = (
        "<table>"
        "<thead><tr><th>種類</th><th>役割</th></tr></thead>"
        "<tbody><tr><td>Aロール</td><td>メイン映像</td></tr></tbody>"
        "</table>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert "<!-- wp:table -->" in save_file
    assert '<figure class="wp-block-table"><table class="has-fixed-layout">' in save_file
    assert "<th>種類</th>" in save_file
    assert "<td>メイン映像</td>" in save_file
    assert "<!-- wp:html -->" not in save_file


def test_convert_html_styled_cell_table_uses_custom_html() -> None:
    """td/thにstyleがある装飾表はCustom HTMLへ退避するテストです。"""
    load_file = (
        '<table style="border-collapse:collapse;width:100%;color:#333333;">'
        "<thead><tr>"
        '<th style="background-color:#eef8ff;color:#1f3b57;">種類</th>'
        '<th style="background-color:#eef8ff;color:#1f3b57;">役割</th>'
        "</tr></thead>"
        "<tbody><tr>"
        '<td style="background-color:#ffffff;padding:10px;"><strong>Aロール</strong></td>'
        '<td style="background-color:#ffffff;padding:10px;">メイン映像</td>'
        "</tr></tbody>"
        "</table>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert "<!-- wp:table -->" not in save_file
    assert '<table style="border-collapse:collapse;width:100%;color:#333333;">' in save_file
    assert '<th style="background-color:#eef8ff;color:#1f3b57;">種類</th>' in save_file
    assert '<td style="background-color:#ffffff;padding:10px;">' in save_file
    assert save_file.endswith("<!-- /wp:html -->")


def test_convert_html_styled_row_table_uses_custom_html() -> None:
    """trにstyleがある装飾表もCustom HTMLへ退避するテストです。"""
    load_file = (
        "<table>"
        "<tbody>"
        '<tr style="background-color:#f9f9f9;">'
        "<td>Aロール</td><td>メイン映像</td>"
        "</tr>"
        "</tbody>"
        "</table>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert "<!-- wp:table -->" not in save_file
    assert '<tr style="background-color:#f9f9f9;">' in save_file
    assert "<td>Aロール</td>" in save_file


def test_convert_html_figure_wrapped_styled_table_keeps_figure_in_custom_html() -> None:
    """figure付きの装飾表はfigureごとCustom HTMLへ退避するテストです。"""
    load_file = (
        '<figure class="wp-block-table">'
        '<table style="border-collapse:collapse;width:100%;">'
        "<tbody><tr>"
        '<td style="background-color:#ffffff;color:#333333;">Aロール</td>'
        "<td>メイン映像</td>"
        "</tr></tbody>"
        "</table>"
        "</figure>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert "<!-- wp:table -->" not in save_file
    assert '<figure class="wp-block-table">' in save_file
    assert '<table style="border-collapse:collapse;width:100%;">' in save_file
    assert '<td style="background-color:#ffffff;color:#333333;">Aロール</td>' in save_file
    assert save_file.endswith("<!-- /wp:html -->")


def test_convert_html_figure_style_and_caption_stay_together_in_custom_html() -> None:
    """figure装飾・caption・strongを落とさずCustom HTMLへ退避するテストです。"""
    load_file = (
        '<figure class="wp-block-table" style="max-width:600px;margin:2em auto;">'
        '<table class="comparison"><thead><tr>'
        '<th scope="col"><strong>種類</strong></th><th scope="col">役割</th>'
        "</tr></thead><tbody><tr>"
        '<td colspan="2">共通内容</td>'
        "</tr></tbody></table>"
        '<figcaption class="wp-element-caption">比較表</figcaption>'
        "</figure>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert "<!-- wp:table -->" not in save_file
    assert '<figure class="wp-block-table" style="max-width:600px;margin:2em auto;">' in save_file
    assert '<th scope="col"><strong>種類</strong></th>' in save_file
    assert '<td colspan="2">共通内容</td>' in save_file
    assert '<figcaption class="wp-element-caption">比較表</figcaption>' in save_file


def test_convert_html_core_supported_cell_attributes_and_caption_use_table_block() -> None:
    """コアが保存できるscope・span・配置・captionは標準表で保持するテストです。"""
    load_file = (
        '<figure class="wp-block-table">'
        "<table><thead><tr>"
        '<th scope="col" colspan="2"><strong>種類</strong></th>'
        "</tr></thead><tbody><tr>"
        '<th scope="row" rowspan="2">A</th>'
        '<td class="has-text-align-center" data-align="center">内容</td>'
        "</tr></tbody></table>"
        '<figcaption class="wp-element-caption">比較表</figcaption>'
        "</figure>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:table -->")
    assert '<table class="has-fixed-layout">' in save_file
    assert '<th scope="col" colspan="2"><strong>種類</strong></th>' in save_file
    assert '<th scope="row" rowspan="2">A</th>' in save_file
    assert '<td class="has-text-align-center" data-align="center">内容</td>' in save_file
    assert '<figcaption class="wp-element-caption">比較表</figcaption>' in save_file


def test_convert_html_existing_styled_table_block_becomes_one_custom_html_block() -> None:
    """既存wp:tableの装飾表を二重コメントなしでCustom HTMLへ退避するテストです。"""
    load_file = (
        "<!-- wp:table -->\n"
        '<figure class="wp-block-table"><table style="width:600px;">'
        "<tbody><tr><td>内容</td></tr></tbody>"
        "</table></figure>\n"
        "<!-- /wp:table -->"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:html -->") == 1
    assert save_file.count("<!-- /wp:html -->") == 1
    assert "<!-- wp:table -->" not in save_file
    assert "<!-- /wp:table -->" not in save_file
    assert '<table style="width:600px;">' in save_file


def test_convert_html_existing_auto_layout_table_keeps_comment_and_class_in_sync() -> None:
    """hasFixedLayout=falseをクラスなしtableと対応させて保持するテストです。"""
    load_file = (
        '<!-- wp:table {"hasFixedLayout":false} -->\n'
        '<figure class="wp-block-table"><table><tbody><tr>'
        "<td>内容</td>"
        "</tr></tbody></table></figure>\n"
        "<!-- /wp:table -->"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith('<!-- wp:table {"hasFixedLayout":false} -->')
    assert '<figure class="wp-block-table"><table><tbody>' in save_file
    assert "has-fixed-layout" not in save_file
    assert save_file.endswith("<!-- /wp:table -->")


def test_convert_html_existing_table_with_unhandled_core_attributes_is_unchanged() -> None:
    """未対応コア属性を持つ既存表を推測で作り直さないテストです。"""
    load_file = (
        '<!-- wp:table {"className":"is-style-stripes"} -->\n'
        '<figure class="wp-block-table is-style-stripes">'
        '<table class="has-fixed-layout"><tbody><tr><td>内容</td></tr></tbody></table>'
        "</figure>\n"
        "<!-- /wp:table -->"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file == load_file


def test_convert_html_table_inside_plain_wrapper_keeps_wrapper_in_custom_html() -> None:
    """表を囲むdivは装飾がなくても削らずCustom HTMLとして保持するテストです。"""
    load_file = (
        '<div class="table-scroll"><table><tbody><tr>'
        "<td>内容</td>"
        "</tr></tbody></table></div>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert '<div class="table-scroll"><table>' in save_file
    assert save_file.endswith("<!-- /wp:html -->")


def test_convert_html_mixed_direct_and_section_rows_do_not_drop_direct_row() -> None:
    """tbody外の行が混ざる表は単純化せず全体を保持するテストです。"""
    load_file = (
        "<table>"
        "<tr><td>先頭行</td></tr>"
        "<tbody><tr><td>本文行</td></tr></tbody>"
        "</table>"
    )

    save_file = convert_html_to_gutenberg(load_file)

    assert save_file.startswith("<!-- wp:html -->")
    assert "<tr><td>先頭行</td></tr>" in save_file
    assert "<tbody><tr><td>本文行</td></tr></tbody>" in save_file
