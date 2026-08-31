"""Test for text converter."""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.text_converter import convert_text_to_gutenberg


def test_convert_text_to_paragraph_blocks() -> None:
    """テキストを段落ブロックに変換するテストです。"""
    load_file = "これは1つ目の段落です。\n\nこれは2つ目の段落です。"

    save_file: str = convert_text_to_gutenberg(load_file)

    assert "<!-- wp:paragraph -->" in save_file
    assert "<p>これは1つ目の段落です。</p>" in save_file
    assert "<p>これは2つ目の段落です。</p>" in save_file


def test_convert_text_cleans_existing_wordpress_html() -> None:
    """既存のWordPressブロックHTML入り.txtを軽く補正するテストです。"""
    load_file = (
        "<!-- wp:heading -->\n"
        '<h2 class="wp-block-heading">画像ブロック image</h2>\n'
        "<!-- /wp:heading -->\n\n"
        "<p></p>\n"
        "<!-- wp:paragraph -->\n"
        "キャリカク岡山：F.K.\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- /wp:paragraph -->\n"
        "<!-- wp:paragraph -->\n"
        "<p>本文\n"
        "<!-- wp:separator -->\n"
        '</p><hr class="wp-block-separator has-alpha-channel-opacity">\n'
        "<!-- /wp:separator -->\n"
        "<!-- wp:paragraph -->\n"
        "<p><code>&lt;!-- wp:paragraph --&gt; のような部分は、<br></code><br>\n"
        "説明です。</p>\n"
        "<!-- /wp:paragraph -->\n"
    )

    save_file = convert_text_to_gutenberg(load_file)

    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert "<p></p>" not in save_file
    assert "<p>キャリカク岡山：F.K.</p>" in save_file
    assert "</p>\n<!-- /wp:paragraph -->\n<!-- wp:separator -->" in save_file
    assert "<code>&lt;!-- wp:paragraph --&gt;</code> のような部分は、<br><br>" in save_file
