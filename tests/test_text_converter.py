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
