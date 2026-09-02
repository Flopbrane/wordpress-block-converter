"""WP-TXT converterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.wp_txt_converter import convert_wp_txt_to_gutenberg


def test_convert_wp_txt_basic_blocks() -> None:
    """WP-TXT記法を基本ブロックへ変換するテストです。"""
    load_file = (
        "【WordPressとは】\n\n"
        "WordPressは、ホームページを作る仕組みです。\n\n"
        "《できること》\n\n"
        "・記事を書く\n"
        "・画像を入れる\n\n"
        "---\n\n"
        "[余白:50]\n"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">WordPressとは</h2>' in save_file
    assert '<!-- wp:heading {"level":3} -->' in save_file
    assert '<h3 class="wp-block-heading">できること</h3>' in save_file
    assert "<!-- wp:paragraph -->" in save_file
    assert "<p>WordPressは、ホームページを作る仕組みです。</p>" in save_file
    assert "<!-- wp:list -->" in save_file
    assert "<li>記事を書く</li>" in save_file
    assert "<!-- wp:separator -->" in save_file
    assert '<!-- wp:spacer {"height":"50px"} -->' in save_file


def test_convert_wp_txt_links_images_code_and_table() -> None:
    """リンク・画像・コード・表を変換するテストです。"""
    load_file = (
        "詳しくは [リンク:公式サイト|https://example.com/] をご覧ください。\n\n"
        "[画像:https://example.com/image.jpg|説明画像]\n\n"
        "[コード]\n"
        "<p>これは段落です。</p>\n"
        "[/コード]\n\n"
        "[表]\n"
        "項目|説明\n"
        "h2|大きな区切り\n"
        "[/表]\n"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<a href="https://example.com/">公式サイト</a>' in save_file
    assert "<!-- wp:image" in save_file
    assert '<img src="https://example.com/image.jpg" alt="説明画像"/>' in save_file
    assert "&lt;p&gt;これは段落です。&lt;/p&gt;" in save_file
    assert "<!-- wp:table -->" in save_file
    assert '<figure class="wp-block-table">' in save_file
    assert "<th>項目</th>" in save_file
    assert "<td>大きな区切り</td>" in save_file


def test_convert_wp_txt_ordered_list_and_quote() -> None:
    """番号付きリストと引用を変換するテストです。"""
    load_file = (
        "1. 最初\n"
        "2. 次\n\n"
        "> 引用文です。\n"
        "> 2行目です。"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<!-- wp:list {"ordered":true} -->' in save_file
    assert '<ol class="wp-block-list">' in save_file
    assert "<li>最初</li>" in save_file
    assert "<!-- wp:quote -->" in save_file
    assert "引用文です。<br>2行目です。" in save_file
