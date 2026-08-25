"""Hi-Security Modeの安全化フィルターのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.hi_security_filter import apply_hi_security_filter


def test_apply_hi_security_filter_removes_blocked_tags_and_attributes() -> None:
    """危険タグ、危険属性、危険URLを削除するテストです。"""
    load_file = (
        '<h1 class="wp-block-heading">見出し</h1>'
        '<p style="color:red" onclick="alert(1)">本文'
        '<a href="javascript:alert(1)">危険リンク</a>'
        '<a href="https://example.com">安全リンク</a>'
        "</p>"
        "<script>alert(1)</script>"
    )

    save_file = apply_hi_security_filter(load_file)

    assert "<h2>見出し</h2>" in save_file
    assert "style=" not in save_file
    assert "onclick=" not in save_file
    assert "javascript:" not in save_file
    assert "<script>" not in save_file
    assert "alert(1)" not in save_file
    assert '<a href="https://example.com">安全リンク</a>' in save_file


def test_apply_hi_security_filter_converts_embed_block_to_link() -> None:
    """embedブロックを通常リンクへ戻すテストです。"""
    load_file = (
        '<!-- wp:embed {"url":"https://www.youtube.com/watch?v=abc"} -->\n'
        '<figure class="wp-block-embed is-provider-youtube">\n'
        '<div class="wp-block-embed__wrapper">\n'
        "https://www.youtube.com/watch?v=abc\n"
        "</div>\n"
        "</figure>\n"
        "<!-- /wp:embed -->"
    )

    save_file = apply_hi_security_filter(load_file)

    assert "<figure" not in save_file
    assert "<div" not in save_file
    assert '<a href="https://www.youtube.com/watch?v=abc">' in save_file


def test_apply_hi_security_filter_converts_short_html_code_examples() -> None:
    """短いHTMLコード例を段落内codeへ変換するテストです。"""
    load_file = (
        "<p>短い例: <code>&lt;h3&gt;</code></p>"
        "<pre><code>&lt;p&gt;本文&lt;/p&gt;</code></pre>"
    )

    save_file = apply_hi_security_filter(load_file)

    assert "<code>&lt;h3&gt;</code>" in save_file
    assert "<pre>" not in save_file
    assert "<p><code>&lt;p&gt;本文&lt;/p&gt;</code></p>" in save_file


def test_apply_hi_security_filter_converts_short_html_list_example() -> None:
    """短いul/li例を実リストではなく段落内codeへ変換するテストです。"""
    load_file = (
        "<!-- wp:code -->\n"
        '<pre class="wp-block-code"><code>&lt;ul&gt;\n'
        "  &lt;li&gt;りんご&lt;/li&gt;\n"
        "  &lt;li&gt;みかん&lt;/li&gt;\n"
        "  &lt;li&gt;バナナ&lt;/li&gt;\n"
        "&lt;/ul&gt;</code></pre>\n"
        "<!-- /wp:code -->"
    )

    save_file = apply_hi_security_filter(load_file)

    assert "<pre" not in save_file
    assert "<ul>" not in save_file
    assert "<code>&lt;ul&gt;</code>" in save_file
    assert "<code>&lt;li&gt;りんご&lt;/li&gt;</code>" in save_file


def test_apply_hi_security_filter_keeps_long_code_blocks() -> None:
    """長いコードブロックはpre/codeとして残すテストです。"""
    load_file = (
        "<pre><code>"
        "line1\nline2\nline3\nline4\nline5\nline6\nline7"
        "</code></pre>"
    )

    save_file = apply_hi_security_filter(load_file)

    assert "<pre><code>" in save_file
