"""区切り値ファイルconverterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.separated_values_converter import convert_separated_values_to_gutenberg


def test_convert_csv_to_table_block() -> None:
    """CSVをtableブロックへ変換するテストです。"""
    load_file = '名前,説明\n"商品A","軽くて,丈夫"\n商品B,水洗い可'

    save_file = convert_separated_values_to_gutenberg(load_file, ".csv")

    assert "<!-- wp:table -->" in save_file
    assert "<th>名前</th>" in save_file
    assert "<th>説明</th>" in save_file
    assert "<td>商品A</td>" in save_file
    assert "<td>軽くて,丈夫</td>" in save_file


def test_convert_tsv_to_table_block() -> None:
    """TSVをtableブロックへ変換するテストです。"""
    load_file = "名前\t価格\n商品A\t1000\n商品B\t1500"

    save_file = convert_separated_values_to_gutenberg(load_file, ".tsv")

    assert "<th>名前</th>" in save_file
    assert "<th>価格</th>" in save_file
    assert "<td>1500</td>" in save_file


def test_convert_ssv_space_to_table_block() -> None:
    """スペース区切りSSVをtableブロックへ変換するテストです。"""
    load_file = '名前 価格\n"商品 A" 1000\n商品B 1500'

    save_file = convert_separated_values_to_gutenberg(load_file, ".ssv")

    assert "<th>名前</th>" in save_file
    assert "<td>商品 A</td>" in save_file
    assert "<td>1500</td>" in save_file


def test_convert_semicolon_values_to_table_block() -> None:
    """セミコロン区切りもtableブロックへ変換するテストです。"""
    load_file = "名前;価格\n商品A;1000\n商品B;1500"

    save_file = convert_separated_values_to_gutenberg(load_file, ".ssv")

    assert "<th>名前</th>" in save_file
    assert "<td>商品B</td>" in save_file
    assert "<td>1500</td>" in save_file


def test_convert_pipe_values_to_table_block() -> None:
    """パイプ区切りをtableブロックへ変換するテストです。"""
    load_file = "名前|価格\n商品A|1000\n商品B|1500"

    save_file = convert_separated_values_to_gutenberg(load_file, ".psv")

    assert "<th>名前</th>" in save_file
    assert "<td>商品A</td>" in save_file
    assert "<td>1000</td>" in save_file
