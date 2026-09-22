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
