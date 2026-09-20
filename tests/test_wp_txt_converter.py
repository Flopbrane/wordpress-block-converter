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


def test_convert_wp_txt_english_markers_to_wordpress_blocks() -> None:
    """英語PRE-WPマーカーをWordPressブロックへ変換するテストです。"""
    load_file = (
        "[Heading:About WordPress]\n\n"
        "[Subheading:What it can do]\n\n"
        "- Write articles\n"
        "- Insert images\n\n"
        "[Spacer:50]\n\n"
        "See [Link:Official site|https://example.com/] for details.\n\n"
        "[Image:https://example.com/image.jpg|Example image]\n\n"
        "[Code]\n"
        "<p>This is code.</p>\n"
        "[/Code]\n\n"
        "[EmphasisCode]\n"
        "functions.php\n"
        "[/EmphasisCode]\n\n"
        "[Table]\n"
        "Item|Description\n"
        "h2|Large section\n"
        "[/Table]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<h2 class="wp-block-heading">About WordPress</h2>' in save_file
    assert '<h3 class="wp-block-heading">What it can do</h3>' in save_file
    assert "<li>Write articles</li>" in save_file
    assert '<!-- wp:spacer {"height":"50px"} -->' in save_file
    assert '<a href="https://example.com/">Official site</a>' in save_file
    assert '<img src="https://example.com/image.jpg" alt="Example image"/>' in save_file
    assert "&lt;p&gt;This is code.&lt;/p&gt;" in save_file
    assert "<code>functions.php</code>" in save_file
    assert "<!-- wp:table -->" in save_file
    assert "[Heading:" not in save_file
    assert "[Code]" not in save_file
    assert "[Table]" not in save_file


def test_convert_wp_txt_english_semantic_blocks() -> None:
    """英語の意味付きPRE-WPブロックを変換するテストです。"""
    load_file = (
        "[List]\n"
        "First\n"
        "Second\n"
        "[/List]\n\n"
        "[OrderedList]\n"
        "First\n"
        "Second\n"
        "[/OrderedList]\n\n"
        "[Box]\n"
        "Box text\n"
        "[/Box]\n\n"
        "[Notice]\n"
        "Notice text\n"
        "[/Notice]\n\n"
        "[Supplement]\n"
        "Supplement text\n"
        "[/Supplement]\n\n"
        "[Steps]\n"
        "Open editor\n"
        "Save file\n"
        "[/Steps]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<li>First</li>" in save_file
    assert '<!-- wp:list {"ordered":true} -->' in save_file
    assert "Box text" in save_file
    assert "<strong>Notice</strong><br>Notice text" in save_file
    assert "<strong>Supplement</strong><br>Supplement text" in save_file
    assert "<li>Open editor</li>" in save_file
    assert "[List]" not in save_file
    assert "[Notice]" not in save_file


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


def test_convert_wp_txt_media_markers_to_wordpress_blocks() -> None:
    """音声・動画・ファイルのPRE-WPマーカーをWPブロックへ変換するテストです。"""
    load_file = (
        "[音声:https://example.com/audio.mp3]\n\n"
        "[動画:https://example.com/video.mp4]\n\n"
        "[ファイル:https://example.com/manual.pdf]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<!-- wp:audio {"src":"https://example.com/audio.mp3"} -->' in save_file
    assert '<audio controls src="https://example.com/audio.mp3"></audio>' in save_file
    assert "<!-- /wp:audio -->" in save_file
    assert '<!-- wp:video {"src":"https://example.com/video.mp4"} -->' in save_file
    assert '<video controls src="https://example.com/video.mp4"></video>' in save_file
    assert "<!-- /wp:video -->" in save_file
    assert '<!-- wp:file {"href":"https://example.com/manual.pdf"} -->' in save_file
    assert '<a href="https://example.com/manual.pdf">manual.pdf</a>' in save_file
    assert "<!-- /wp:file -->" in save_file
    assert "[音声:" not in save_file
    assert "[動画:" not in save_file
    assert "[ファイル:" not in save_file


def test_convert_wp_txt_emphasis_code_to_html_block() -> None:
    """強調コードをwp:html内のstyle付きpre/codeへ変換するテストです。"""
    load_file = (
        "[強調コード]\n"
        "functions.php\n"
        "[/強調コード]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:html -->" in save_file
    assert '<pre class="wp-block-code" style="display:inline-block;' in save_file
    assert "<code>functions.php</code>" in save_file
    assert "<!-- /wp:html -->" in save_file


def test_convert_wp_txt_emphasis_code_escapes_html_chars() -> None:
    """強調コード内の<>&をescapeし、引用符は保持するテストです。"""
    load_file = (
        "[強調コード]\n"
        '<p data-name="A">A & B</p>\n'
        "[/強調コード]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '&lt;p data-name="A"&gt;A &amp; B&lt;/p&gt;' in save_file
    assert "<code><p" not in save_file
    assert "&quot;" not in save_file


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


def test_convert_wp_txt_box_wraps_text_in_styled_html_block() -> None:
    """囲い込みマーカーを枠付きHTMLブロックへ変換するテストです。"""
    load_file = (
        "[囲い込み]\n"
        "注意文です。\n"
        "<script>alert(\"x\")</script>\n\n"
        "次の段落です。\n"
        "[/囲い込み]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:html -->" in save_file
    assert '<div style="border:1px solid #999;padding:16px;' in save_file
    assert "注意文です。<br>&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;" in save_file
    assert "<br><br>次の段落です。" in save_file
    assert "<script>" not in save_file
    assert "[囲い込み]" not in save_file
    assert "[/囲い込み]" not in save_file
    assert "<!-- /wp:html -->" in save_file


def test_convert_wp_txt_html_exec_block_keeps_raw_html() -> None:
    """[HTML]は実行HTMLとしてwp:htmlへ出力するテストです。"""
    load_file = (
        "[HTML]\n"
        '<div style="display:flex;gap:24px;">HTML本文</div>\n'
        "[/HTML]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:html -->" in save_file
    assert '<div style="display:flex;gap:24px;">HTML本文</div>' in save_file
    assert "&lt;div" not in save_file
    assert "<!-- /wp:html -->" in save_file


def test_convert_wp_txt_bold_marker_inside_paragraph() -> None:
    """[太字]を本文中のstrongへ変換するテストです。"""
    save_file = convert_wp_txt_to_gutenberg("これは[太字]重要[/太字]です。")

    assert "<p>これは<strong>重要</strong>です。</p>" in save_file
    assert "[太字]" not in save_file
    assert "[/太字]" not in save_file


def test_convert_wp_txt_notice_and_supplement_blocks() -> None:
    """注意枠と補足枠を意味付きの枠へ変換するテストです。"""
    load_file = (
        "[注意]\n"
        "保存前に確認してください。\n"
        "[/注意]\n\n"
        "[補足]\n"
        "必要に応じて使います。\n"
        "[/補足]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:html -->") == 2
    assert "<strong>注意</strong><br>保存前に確認してください。" in save_file
    assert "<strong>補足</strong><br>必要に応じて使います。" in save_file
    assert "[注意]" not in save_file
    assert "[補足]" not in save_file


def test_convert_wp_txt_steps_block_to_ordered_list() -> None:
    """[手順]を番号付きリストへ変換するテストです。"""
    load_file = (
        "[手順]\n"
        "管理画面を開く\n"
        "投稿を確認する\n"
        "保存する\n"
        "[/手順]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert '<!-- wp:list {"ordered":true} -->' in save_file
    assert "<li>管理画面を開く</li>" in save_file
    assert "<li>投稿を確認する</li>" in save_file
    assert "<li>保存する</li>" in save_file


def test_convert_wp_txt_image_row_block() -> None:
    """[画像横並び]をgap付きHTMLブロックへ変換するテストです。"""
    load_file = (
        "[画像横並び:24px]\n"
        "https://example.com/a.jpg\n"
        "[画像:https://example.com/b.jpg|画像B]\n"
        "[画像:画像C|https://example.com/c.jpg]\n"
        "[/画像横並び]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert "<!-- wp:html -->" in save_file
    assert 'style="display:flex;gap:24px;' in save_file
    assert '<img src="https://example.com/a.jpg" alt=""' in save_file
    assert '<img src="https://example.com/b.jpg" alt="画像B"' in save_file
    assert '<img src="https://example.com/c.jpg" alt="画像C"' in save_file
    assert "[画像横並び:24px]" not in save_file
    assert "[/画像横並び]" not in save_file


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


def test_convert_wp_txt_code_and_emphasis_code_use_different_wp_blocks() -> None:
    """通常コードと強調コードを別のWordPressブロックとして出力するテストです。"""
    load_file = (
        "[コード]\n"
        "print(\"hello\")\n"
        "[/コード]\n\n"
        "[強調コード]\n"
        '"mediaId":123\n'
        "[/強調コード]"
    )

    save_file = convert_wp_txt_to_gutenberg(load_file)

    assert save_file.count("<!-- wp:code -->") == 1
    assert save_file.count("<!-- /wp:code -->") == 1
    assert save_file.count("<!-- wp:html -->") == 1
    assert save_file.count("<!-- /wp:html -->") == 1
    assert 'print("hello")' in save_file
    assert '"mediaId":123' in save_file


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
