"""Markdown converterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.markdown_converter import convert_markdown_to_gutenberg


def test_convert_markdown_groups_h2_section_into_paragraph() -> None:
    """##から次の##前までを1つの段落として変換するテストです。"""
    load_file = (
        "## 太字タグ\n\n"
        "文字を太く強調したいときは、**strong タグ**を使います。\n\n"
        "`<p>`の中でも使えます。\n\n"
        "## 斜体・強調タグ\n\n"
        "少し強調したいときは、em タグを使います。"
    )

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<!-- wp:heading -->" not in save_file
    assert "<p>## 太字タグ<br><br>" in save_file
    assert "<strong>strong タグ</strong>" in save_file
    assert "<code>&lt;p&gt;</code>" in save_file
    assert "<p>## 斜体・強調タグ<br><br>" in save_file


def test_convert_markdown_keeps_h1_as_heading() -> None:
    """#は今まで通り見出しとして変換するテストです。"""
    load_file = "# 記事タイトル\n\n本文です。"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<!-- wp:heading {"level":1} -->' in save_file
    assert '<h1 class="wp-block-heading">記事タイトル</h1>' in save_file
