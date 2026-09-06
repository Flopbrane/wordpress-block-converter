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
