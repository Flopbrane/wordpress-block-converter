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


def test_convert_file_applies_high_security_mode_alias(tmp_path: Path) -> None:
    """high-securityでも安全化フィルターを通すテストです。"""
    load_file_path = tmp_path / "sample.md"
    save_file_path = tmp_path / "sample_safe_wordpress.html"
    load_file_path.write_text(
        "# タイトル\n\nhttps://www.youtube.com/watch?v=abc",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="high-security")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "<!-- wp:embed" not in save_file
    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">タイトル</h2>' in save_file


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


def test_convert_file_keeps_normal_mode_without_rewrite_style(tmp_path: Path) -> None:
    """normalではrewrite_styleを通さないテストです。"""
    load_file_path = tmp_path / "sample.md"
    save_file_path = tmp_path / "sample_wordpress.html"
    load_file_path.write_text("paragraph の説明です。", encoding="utf-8")

    convert_file(load_file_path, save_file_path, mode="normal")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "<p>paragraph の説明です。</p>" in save_file
    assert "<code>paragraph</code>" not in save_file


def test_convert_file_applies_rewrite_style_to_middle_mode(tmp_path: Path) -> None:
    """middleではrewrite_styleを通すテストです。"""
    load_file_path = tmp_path / "sample.md"
    save_file_path = tmp_path / "sample_wordpress.html"
    load_file_path.write_text("paragraph の説明です。", encoding="utf-8")

    convert_file(load_file_path, save_file_path, mode="middle")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "<code>paragraph</code> の説明です。" in save_file


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


def test_convert_file_supports_wp_txt(tmp_path: Path) -> None:
    """WP-TXTファイルを見出し・リストへ変換するテストです。"""
    load_file_path = tmp_path / "sample.wp_txt"
    save_file_path = tmp_path / "sample_wordpress.html"
    load_file_path.write_text(
        "【サービス紹介】\n\n"
        "本文です。\n\n"
        "・相談\n"
        "・制作\n",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path)

    save_file = save_file_path.read_text(encoding="utf-8")
    assert '<h2 class="wp-block-heading">サービス紹介</h2>' in save_file
    assert "<p>本文です。</p>" in save_file
    assert "<li>相談</li>" in save_file


def test_convert_file_applies_office_mode_like_hi_security(tmp_path: Path) -> None:
    """office modeで事業所WP向け安全化フィルターを通すテストです。"""
    load_file_path = tmp_path / "office.md"
    save_file_path = tmp_path / "office_wordpress.html"
    load_file_path.write_text(
        "# 大きな区切り\n\n"
        "通常本文です。 \\\\ 明示改行です。\n\n"
        "HTMLでは `<h2>見出し</h2>` のように書きます。\n\n"
        "| 項目 | 説明 |\n"
        "|---|---|\n"
        "| h2 | 大きな区切り |\n",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="office")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">大きな区切り</h2>' in save_file
    assert "<!-- wp:paragraph -->" in save_file
    assert "通常本文です。 <br><br> 明示改行です。" in save_file
    assert "<code>&lt;h2&gt;見出し&lt;/h2&gt;</code>" in save_file
    assert "<!-- wp:table -->" in save_file
    assert '<figure class="wp-block-table">' in save_file


def test_convert_file_applies_middle_mode_like_office(tmp_path: Path) -> None:
    """middle modeでも事業所WP向け安全化フィルターを通すテストです。"""
    load_file_path = tmp_path / "middle.md"
    save_file_path = tmp_path / "middle_wordpress.html"
    load_file_path.write_text(
        "# 大きな区切り\n\n"
        "本文です。\n",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="middle")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">大きな区切り</h2>' in save_file
    assert "<!-- wp:paragraph -->" in save_file


def test_convert_file_office_mode_removes_dangerous_html(tmp_path: Path) -> None:
    """office modeで危険タグや危険属性を除去するテストです。"""
    load_file_path = tmp_path / "danger.html"
    save_file_path = tmp_path / "danger_wordpress.html"
    load_file_path.write_text(
        '<p onclick="alert(1)">本文<a href="javascript:alert(1)">危険</a></p>'
        "<script>alert(1)</script>"
        "<iframe src=\"https://example.com\"></iframe>"
        "<style>p{color:red}</style>",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="office")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "onclick=" not in save_file
    assert "javascript:" not in save_file
    assert "<script" not in save_file
    assert "<iframe" not in save_file
    assert "<style" not in save_file
    assert "alert(1)" not in save_file
