"""WP-TXT converterのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re

from converters.wp_txt_converter import (
    convert_wp_txt_to_gutenberg,
    parse_prewp,
    render_wordpress,
)


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


def test_convert_wp_txt_emphasis_code_to_html_block() -> None:
    """強調コードをwp:codeのpre/codeへ変換するテストです。"""
    load_file = (
        "[強調コード]\n"
        "functions.php\n"
        "[/強調コード]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:code -->" in save_file
    assert '<pre class="wp-block-code" style="display:inline-block;' in save_file
    assert "<code>functions.php</code>" in save_file
    assert "<!-- /wp:code -->" in save_file


def test_convert_wp_txt_emphasis_code_escapes_html_chars() -> None:
    """強調コード内の<>&をHTMLエスケープするテストです。"""
    load_file = (
        "[強調コード]\n"
        "<p>A & B</p>\n"
        "[/強調コード]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "&lt;p&gt;A &amp; B&lt;/p&gt;" in save_file
    assert "<code><p>A & B</p></code>" not in save_file


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


def test_convert_wp_txt_code_block_uses_wp_code_and_keeps_quotes() -> None:
    """[コード]をwp:codeへ変換し、引用符はエスケープしないテストです。"""
    load_file = (
        "[コード]\n"
        '{"name":"A & B","text":"<tag>","quote":"\'"}\n'
        "[/コード]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:code -->" in save_file
    assert '<pre class="wp-block-code"><code>' in save_file
    assert '"name":"A &amp; B"' in save_file
    assert '"text":"&lt;tag&gt;"' in save_file
    assert '"quote":"\'"' in save_file
    assert "&quot;" not in save_file
    assert "&#x27;" not in save_file
    assert "<!-- /wp:code -->" in save_file


def test_convert_wp_txt_inline_position_code_marker_becomes_block() -> None:
    """文章途中の[コード]もPRE-WPタグとして解析するテストです。"""
    load_file = (
        "ただし、[コード]\n"
        '"mediaId":123\n'
        "[/コード] や [コード]\n"
        '"mediaType":"image"\n'
        "[/コード]などの内部パラメータを、"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:code -->") == 2
    assert '"mediaId":123' in save_file
    assert '"mediaType":"image"' in save_file
    assert "[コード]" not in save_file
    assert "[/コード]" not in save_file


def test_convert_wp_txt_explicit_list_converts_all_lines_to_list_items() -> None:
    """[リスト]内の全行をliへ変換するテストです。"""
    load_file = (
        "[リスト]\n"
        "項目1\n"
        "項目2\n"
        "項目3\n"
        "[/リスト]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:list -->" in save_file
    assert "<li>項目1</li>" in save_file
    assert "<li>項目2</li>" in save_file
    assert "<li>項目3</li>" in save_file


def test_convert_wp_txt_ordered_explicit_list() -> None:
    """[番号リスト]をolへ変換するテストです。"""
    load_file = (
        "[番号リスト]\n"
        "最初\n"
        "次\n"
        "[/番号リスト]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<!-- wp:list {"ordered":true} -->' in save_file
    assert '<ol class="wp-block-list">' in save_file
    assert "<li>最初</li>" in save_file
    assert "<li>次</li>" in save_file


def test_convert_wp_txt_explicit_paragraph_keeps_blank_line_as_double_break() -> None:
    """明示段落内では空行をbr2つ相当として扱うテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "1行目です。\n"
        "2行目です。\n\n"
        "3行目です。\n"
        "<!-- /wp:paragraph -->"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:paragraph -->" in save_file
    assert "<p>1行目です。<br>2行目です。<br><br>3行目です。</p>" in save_file
    assert "<!-- /wp:paragraph -->" in save_file


def test_convert_wp_txt_explicit_html_block_keeps_raw_html() -> None:
    """明示HTMLブロックではHTMLを実行HTMLとして残すテストです。"""
    load_file = (
        "<!-- wp:html -->\n"
        '<div class="box">A & B</div>\n'
        "<!-- /wp:html -->"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:html -->" in save_file
    assert '<div class="box">A & B</div>' in save_file
    assert "&lt;div" not in save_file
    assert "<!-- /wp:html -->" in save_file


def test_convert_wp_txt_separator_marker() -> None:
    """---をseparatorへ変換するテストです。"""
    save_file = convert_wp_txt_to_gutenberg("前文\n\n---\n\n後文")

    assert "<!-- wp:separator -->" in save_file
    assert '<hr class="wp-block-separator has-alpha-channel-opacity"/>' in save_file
    assert "<!-- /wp:separator -->" in save_file


def test_convert_wp_txt_does_not_leave_prewp_tags() -> None:
    """PRE-WPタグ文字列が最終HTMLへ残らないテストです。"""
    load_file = (
        "[コード]\nA\n[/コード]\n\n"
        "[強調コード]\nB\n[/強調コード]\n\n"
        "[リスト]\nC\n[/リスト]\n\n"
        "[番号リスト]\nD\n[/番号リスト]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    for marker in (
        "[コード]",
        "[/コード]",
        "[強調コード]",
        "[/強調コード]",
        "[リスト]",
        "[/リスト]",
        "[番号リスト]",
        "[/番号リスト]",
    ):
        assert marker not in save_file


def test_convert_wp_txt_block_comment_pairs_are_balanced() -> None:
    """WordPressブロックコメントの開始数と終了数が一致するテストです。"""
    load_file = (
        "【見出し】\n\n"
        "本文1\n本文2\n\n"
        "[コード]\nA\n[/コード]\n\n"
        "[強調コード]\nB\n[/強調コード]\n\n"
        "[リスト]\nC\nD\n[/リスト]\n\n"
        "---"
    )
    save_file = convert_wp_txt_to_gutenberg(load_file)

    starts, ends = _count_block_comments(save_file)

    assert starts == ends


def test_convert_wp_txt_can_render_editor_text_without_file_save() -> None:
    """Text Editorの文字列をファイル保存なしで変換できるコアのテストです。"""
    editor_text = "[コード]\nprint(\"hello\")\n[/コード]"

    save_file = render_wordpress(parse_prewp(editor_text))

    assert "<!-- wp:code -->" in save_file
    assert 'print("hello")' in save_file
    assert "<!-- /wp:code -->" in save_file


def _count_block_comments(save_file: str) -> tuple[dict[str, int], dict[str, int]]:
    starts: dict[str, int] = {}
    ends: dict[str, int] = {}
    for block_match in re.finditer(r"<!--\s*(/)?wp:([a-zA-Z0-9_-]+)(?:\s+.*?)?\s*-->", save_file):
        target = ends if block_match.group(1) else starts
        block_name = block_match.group(2)
        target[block_name] = target.get(block_name, 0) + 1
    return starts, ends
