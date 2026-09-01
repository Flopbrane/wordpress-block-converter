"""修復モードのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from repair_mode import repair_wordpress_html


def test_repair_wordpress_html_keeps_normal_mode_without_rewrite() -> None:
    """normal修復では構文修復だけを行うテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "キャリカク岡山：F.K.\n"
        "<!-- /wp:paragraph -->\n"
    )

    save_file = repair_wordpress_html(load_file, mode="normal")

    assert "<p>キャリカク岡山：F.K.</p>" in save_file
    assert "<code>F</code>" not in save_file


def test_repair_wordpress_html_keeps_valid_blocks_unchanged() -> None:
    """正常な既存WPブロックは変更しないテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p>文章です。</p>\n"
        "<!-- /wp:paragraph -->\n\n"
        "<!-- wp:table -->\n"
        '<figure class="wp-block-table"><table><tbody><tr><td>内容</td></tr></tbody></table></figure>\n'
        "<!-- /wp:table -->\n"
    )

    save_file = repair_wordpress_html(load_file, mode="normal")

    assert save_file == load_file


def test_repair_wordpress_html_does_not_increase_valid_paragraph_blocks() -> None:
    """正常なparagraphブロックを増やさないテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        "<p>1つ目の文章です。</p>\n"
        "<!-- /wp:paragraph -->\n\n"
        "<!-- wp:paragraph -->\n"
        "<p>2つ目の文章です。</p>\n"
        "<!-- /wp:paragraph -->\n"
    )

    save_file = repair_wordpress_html(load_file, mode="normal")

    assert save_file.count("<!-- wp:paragraph -->") == 2
    assert save_file == load_file


def test_repair_wordpress_html_applies_middle_mode_rewrite() -> None:
    """middle修復では表示調整も行うテストです。"""
    load_file = (
        '<!-- wp:heading {"level":3} -->\n'
        '<h3 class="wp-block-heading">タイトル</h3>\n'
        "<!-- /wp:heading -->\n\n"
        "<!-- wp:paragraph -->\n"
        "<p>paragraph の説明です。<br></p>\n"
        "<!-- /wp:paragraph -->\n"
    )

    save_file = repair_wordpress_html(load_file, mode="middle")

    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">タイトル</h2>' in save_file
    assert "<code>paragraph</code> の説明です。<br><br>" in save_file


def test_repair_wordpress_html_applies_middle_mode_security_filter() -> None:
    """middle修復では危険属性を除去するテストです。"""
    load_file = (
        "<!-- wp:paragraph -->\n"
        '<p onclick="alert(1)">本文</p>\n'
        "<!-- /wp:paragraph -->"
    )

    save_file = repair_wordpress_html(load_file, mode="middle")

    assert "onclick" not in save_file
    assert "alert(1)" not in save_file
