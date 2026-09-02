"""Markdown converterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.markdown_converter import convert_markdown_to_gutenberg


def test_convert_markdown_converts_h2_to_heading_block() -> None:
    """##をparagraphではなくh2見出しへ変換するテストです。"""
    load_file = "## CSSについて\n\n単独です。"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">CSSについて</h2>' in save_file
    assert "<p>## CSSについて" not in save_file
    assert "# CSSについて" not in save_file


def test_convert_markdown_converts_h3_to_heading_block() -> None:
    """###をh3見出しへ変換するテストです。"""
    load_file = "### 見出し\n\n本文です。"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<!-- wp:heading {"level":3} -->' in save_file
    assert '<h3 class="wp-block-heading">見出し</h3>' in save_file
    assert "<p>### 見出し" not in save_file


def test_convert_markdown_keeps_h1_as_heading() -> None:
    """#は今まで通り見出しとして変換するテストです。"""
    load_file = "# 記事タイトル\n\n本文です。"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<!-- wp:heading {"level":1} -->' in save_file
    assert '<h1 class="wp-block-heading">記事タイトル</h1>' in save_file


def test_convert_markdown_separates_table_list_and_code_from_paragraph() -> None:
    """table/list/codeをparagraphの外に分離するテストです。"""
    load_file = (
        "前の文章です。\n"
        "| 名前 | 値 |\n"
        "|---|---|\n"
        "| A | 1 |\n"
        "- 項目1\n"
        "- 項目2\n"
        "```python\n"
        "print('hello')\n"
        "```\n"
        "後の文章です。"
    )

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<p>前の文章です。</p>" in save_file
    assert "<!-- wp:table -->" in save_file
    assert "<!-- wp:list -->" in save_file
    assert "<!-- wp:list-item -->" in save_file
    assert "<!-- wp:code -->" in save_file
    assert "<p>後の文章です。</p>" in save_file
    assert "<p>前の文章です。<br><br>| 名前 | 値 |" not in save_file
    assert "<p>- 項目1" not in save_file
    assert "<p>```python" not in save_file


def test_convert_markdown_adds_ordered_list_attributes() -> None:
    """番号付きリストはordered属性とwp-block-list classを付けるテストです。"""
    load_file = "1. 最初\n2. 次"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<!-- wp:list {"ordered":true} -->' in save_file
    assert '<ol class="wp-block-list">' in save_file
    assert "<!-- wp:list-item -->" in save_file
    assert "<li>最初</li>" in save_file


def test_convert_markdown_keeps_non_table_line_before_heading() -> None:
    """表ではない|行を直後の見出しより前のparagraphにするテストです。"""
    load_file = "| 普通の文章 |\n## 見出し"

    save_file = convert_markdown_to_gutenberg(load_file)

    paragraph_position = save_file.index("<p>| 普通の文章 |</p>")
    heading_position = save_file.index('<h2 class="wp-block-heading">見出し</h2>')
    assert paragraph_position < heading_position
    assert "<!-- wp:table -->" not in save_file


def test_convert_markdown_converts_inline_code() -> None:
    """単一バッククォートをinline codeへ変換するテストです。"""
    load_file = "`font-size` を使います。"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<code>font-size</code> を使います。" in save_file
    assert "`font-size`" not in save_file


def test_convert_markdown_converts_single_code_line_to_code_block() -> None:
    """1行だけのバッククォートコードはwp:codeへ変換するテストです。"""
    load_file = "`font-size`"

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<!-- wp:code -->" in save_file
    assert '<pre class="wp-block-code"><code>font-size</code></pre>' in save_file
    assert "<!-- /wp:code -->" in save_file
    assert "<!-- wp:paragraph -->" not in save_file
    assert "`font-size`" not in save_file


def test_convert_markdown_does_not_parse_markdown_inside_fenced_code() -> None:
    """fenced code内の##やtable記法を見出しや表にしないテストです。"""
    load_file = (
        "```python\n"
        "## 見出しではありません\n"
        "| A | B |\n"
        "|---|---|\n"
        'print("<x>&")\n'
        "```\n"
    )

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<!-- wp:code -->" in save_file
    assert "<!-- wp:heading" not in save_file
    assert "<!-- wp:table -->" not in save_file
    assert "## 見出しではありません" in save_file
    assert "print(&quot;&lt;x&gt;&amp;&quot;)" in save_file
