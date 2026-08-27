"""JSON converterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.json_converter import convert_json_to_gutenberg


def test_convert_json_sections_to_heading_and_paragraph_blocks() -> None:
    """JSONのtitleとsectionsを見出し・段落へ変換するテストです。"""
    load_file = """
    {
      "title": "サービス紹介",
      "sections": [
        {
          "heading": "私たちの強み",
          "text": "ここに本文を入れます。"
        },
        {
          "heading": "対応できること",
          "text": "ここに本文を入れます。"
        }
      ]
    }
    """

    save_file = convert_json_to_gutenberg(load_file)

    assert '<h1 class="wp-block-heading">サービス紹介</h1>' in save_file
    assert '<h2 class="wp-block-heading">私たちの強み</h2>' in save_file
    assert "<p>ここに本文を入れます。</p>" in save_file


def test_convert_json_items_to_list_block() -> None:
    """JSONのitemsをリストへ変換するテストです。"""
    load_file = '{"heading":"対応内容","items":["制作","保守","改善"]}'

    save_file = convert_json_to_gutenberg(load_file)

    assert "<!-- wp:list -->" in save_file
    assert "<li>制作</li>" in save_file
    assert "<li>改善</li>" in save_file


def test_convert_json_table_rows_to_table_block() -> None:
    """JSONのtableを表へ変換するテストです。"""
    load_file = """
    {
      "table": [
        {"商品": "Aプラン", "価格": "1000円"},
        {"商品": "Bプラン", "価格": "2000円"}
      ]
    }
    """

    save_file = convert_json_to_gutenberg(load_file)

    assert "<!-- wp:table -->" in save_file
    assert "<th>商品</th>" in save_file
    assert "<td>Aプラン</td>" in save_file
    assert "<td>2000円</td>" in save_file


def test_convert_json_faq_to_heading_and_paragraph_blocks() -> None:
    """JSONのFAQを見出しと段落へ変換するテストです。"""
    load_file = """
    {
      "title": "よくある質問",
      "faq": [
        {"question": "相談できますか？", "answer": "はい、可能です。"},
        {"q": "見積もりは無料ですか？", "a": "無料です。"}
      ]
    }
    """

    save_file = convert_json_to_gutenberg(load_file)

    assert '<h2 class="wp-block-heading">相談できますか？</h2>' in save_file
    assert "<p>はい、可能です。</p>" in save_file
    assert '<h2 class="wp-block-heading">見積もりは無料ですか？</h2>' in save_file
    assert "<p>無料です。</p>" in save_file


def test_convert_json_raises_value_error_for_invalid_json() -> None:
    """壊れたJSONは分かりやすいエラーにするテストです。"""
    try:
        convert_json_to_gutenberg("{")
    except ValueError as error:
        assert "JSONの読み込みに失敗しました" in str(error)
    else:
        raise AssertionError("ValueErrorが発生しませんでした。")
