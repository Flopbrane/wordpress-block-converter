"""file_checkerの内容判定テストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from file_checker import select_converter


def test_select_converter_keeps_existing_wp_html_even_if_extension_is_md() -> None:
    """拡張子がmdでも既存WP HTMLなら二重変換しないテストです。"""
    load_file = "<!-- wp:paragraph -->\n<p>本文です。</p>\n<!-- /wp:paragraph -->"

    converter = select_converter("sample.md", load_file)
    save_file = converter(load_file)

    assert save_file == load_file


def test_select_converter_detects_markdown_heading_from_content() -> None:
    """拡張子がtxtでもMarkdown見出しならMarkdown変換するテストです。"""
    load_file = "# タイトル\n\n本文です。"

    converter = select_converter("sample.txt", load_file)
    save_file = converter(load_file)

    assert '<h1 class="wp-block-heading">タイトル</h1>' in save_file


def test_select_converter_detects_html_from_content() -> None:
    """拡張子がtxtでもHTMLタグならHTML変換するテストです。"""
    load_file = "<!DOCTYPE html>\n<html><body><p>本文です。</p></body></html>"

    converter = select_converter("sample.txt", load_file)
    save_file = converter(load_file)

    assert "<!-- wp:paragraph -->" in save_file
    assert "<p>本文です。</p>" in save_file


def test_select_converter_detects_json_before_html_tags_in_json_text() -> None:
    """JSON内にHTMLタグ風の文字があってもJSON変換するテストです。"""
    load_file = '{"title":"紹介","sections":[{"heading":"本文","text":"<p>説明</p>"}]}'

    converter = select_converter("sample.txt", load_file)
    save_file = converter(load_file)

    assert '<h1 class="wp-block-heading">紹介</h1>' in save_file
    assert "<!-- wp:html -->" not in save_file


def test_select_converter_detects_wp_txt_from_content() -> None:
    """拡張子がtxtでもWP-TXT記法ならWP-TXT変換するテストです。"""
    load_file = "【サービス紹介】\n\n本文です。"

    converter = select_converter("sample.txt", load_file)
    save_file = converter(load_file)

    assert '<h2 class="wp-block-heading">サービス紹介</h2>' in save_file


def test_select_converter_detects_csv_from_content() -> None:
    """拡張子がtxtでもCSVらしければ表変換するテストです。"""
    load_file = "名前,価格\n商品A,1000"

    converter = select_converter("sample.txt", load_file)
    save_file = converter(load_file)

    assert "<!-- wp:table -->" in save_file
    assert "<th>名前</th>" in save_file
    assert "<td>商品A</td>" in save_file
