"""main.pyの変換モードのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from pathlib import Path
from unittest import TestCase

from converters.document_converter import (
    convert_doc_to_gutenberg,
    convert_pdf_to_gutenberg,
    convert_rtf_to_gutenberg,
)
from main import convert_file


def test_convert_file_applies_hi_security_mode(tmp_path: Path) -> None:
    """hi-securityのときだけ安全化フィルターを通すテストです。"""
    load_file_path = tmp_path / "sample.md"
    save_file_path = tmp_path / "sample_safe_wordpress.html"
    load_file_path.write_text(
        "# タイトル\n\nhttps://www.youtube.com/watch?v=abc",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="hi-security")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "<!-- wp:embed" not in save_file
    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">タイトル</h2>' in save_file
    assert '<a href="https://www.youtube.com/watch?v=abc">' in save_file


def test_convert_file_keeps_normal_mode_output(tmp_path: Path) -> None:
    """normalではHi-Securityフィルターを通さないテストです。"""
    load_file_path = tmp_path / "sample.md"
    save_file_path = tmp_path / "sample_wordpress.html"
    load_file_path.write_text(
        "# タイトル\n\nhttps://www.youtube.com/watch?v=abc",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="normal")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert '<!-- wp:heading {"level":1} -->' in save_file
    assert '<h1 class="wp-block-heading">タイトル</h1>' in save_file
    assert "<!-- wp:embed" in save_file


def test_future_document_converters_are_prepared() -> None:
    """将来の文書変換メソッドが用意されていることを確認するテストです。"""
    test_case = TestCase()

    with test_case.assertRaisesRegex(NotImplementedError, "RTF変換"):
        convert_rtf_to_gutenberg("{\\rtf1 本文}")

    with test_case.assertRaisesRegex(NotImplementedError, "Word文書変換"):
        convert_doc_to_gutenberg(Path("sample.docx"))

    with test_case.assertRaisesRegex(NotImplementedError, "PDF変換"):
        convert_pdf_to_gutenberg(Path("sample.pdf"))


def test_convert_file_supports_csv_table(tmp_path: Path) -> None:
    """CSVファイルをtableブロックへ変換するテストです。"""
    load_file_path = tmp_path / "sample.csv"
    save_file_path = tmp_path / "sample_wordpress.html"
    load_file_path.write_text("名前,価格\n商品A,1000", encoding="utf-8")

    convert_file(load_file_path, save_file_path)

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "<!-- wp:table -->" in save_file
    assert "<th>名前</th>" in save_file
    assert "<td>商品A</td>" in save_file


def test_convert_file_supports_json_sections(tmp_path: Path) -> None:
    """JSONファイルを見出し・段落ブロックへ変換するテストです。"""
    load_file_path = tmp_path / "sample.json"
    save_file_path = tmp_path / "sample_wordpress.html"
    load_file_path.write_text(
        '{"title":"サービス紹介","sections":[{"heading":"強み","text":"本文です。"}]}',
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path)

    save_file = save_file_path.read_text(encoding="utf-8")
    assert '<h1 class="wp-block-heading">サービス紹介</h1>' in save_file
    assert '<h2 class="wp-block-heading">強み</h2>' in save_file
    assert "<p>本文です。</p>" in save_file
