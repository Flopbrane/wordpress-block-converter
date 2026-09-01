"""rewrite_styleのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import json
from pathlib import Path

from rewrite_style import apply_rewrite_style


def test_apply_rewrite_style_passes_normal_mode() -> None:
    """normal modeでは書き換えないテストです。"""
    save_file = (
        '<!-- wp:heading {"level":2} -->\n'
        '<h2 class="wp-block-heading">最初</h2>\n'
        "<!-- /wp:heading -->\n\n"
        '<!-- wp:heading {"level":2} -->\n'
        '<h2 class="wp-block-heading">次</h2>\n'
        "<!-- /wp:heading -->"
    )

    rewritten_file = apply_rewrite_style(save_file, mode="normal")

    assert rewritten_file == save_file


def test_apply_rewrite_style_wraps_alphabet_and_normalizes_breaks() -> None:
    """middle modeでは英字とコード範囲、改行を整えるテストです。"""
    save_file = (
        "<!-- wp:paragraph -->\n"
        "<p>これは paragraph の説明です。<br>\n"
        "&lt;!-- wp:paragraph --&gt;<br><br>\n"
        "<code>&lt;!-- wp:paragraph --&gt; のような部分は、<br></code><br>\n"
        "<code>print</code><br><br></p>\n"
        "<!-- /wp:paragraph -->"
    )

    rewritten_file = apply_rewrite_style(save_file, mode="middle")

    assert "これは <code>paragraph</code> の説明です。<br><br>" in rewritten_file
    assert "<code>&lt;!-- wp:paragraph --&gt;</code><br>" in rewritten_file
    assert "<code>&lt;!-- wp:paragraph --&gt;</code> のような部分は、<br><br>" in rewritten_file
    assert "<code>print</code><br>" in rewritten_file


def test_apply_rewrite_style_uses_correct_data_ignore_words() -> None:
    """correct_data.jsonの除外ワードはcode囲みしないテストです。"""
    save_file = (
        "<!-- wp:paragraph -->\n"
        "<p>WordPress と paragraph と HTML の説明です。<br></p>\n"
        "<!-- /wp:paragraph -->"
    )

    rewritten_file = apply_rewrite_style(save_file, mode="middle")

    assert "WordPress" in rewritten_file
    assert "HTML" in rewritten_file
    assert "<code>WordPress</code>" not in rewritten_file
    assert "<code>HTML</code>" not in rewritten_file
    assert "<code>paragraph</code>" in rewritten_file


def test_apply_rewrite_style_can_change_ignore_words_with_json(tmp_path: Path) -> None:
    """外部JSONを変更するとcode囲み除外基準が変わるテストです。"""
    correct_data_path = tmp_path / "correct_data.json"
    correct_data_path.write_text(
        json.dumps({"code_wrap_ignore_words": ["paragraph"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    save_file = (
        "<!-- wp:paragraph -->\n"
        "<p>WordPress と paragraph の説明です。<br></p>\n"
        "<!-- /wp:paragraph -->"
    )

    rewritten_file = apply_rewrite_style(
        save_file,
        mode="middle",
        correct_data_path=correct_data_path,
    )

    assert "<code>WordPress</code>" in rewritten_file
    assert "<code>paragraph</code>" not in rewritten_file


def test_apply_rewrite_style_normalizes_heading_blocks() -> None:
    """最初の見出しをh2、2個目以降のh2をh3へ変更するテストです。"""
    save_file = (
        '<!-- wp:heading {"level":3} -->\n'
        '<h3 class="wp-block-heading">最初</h3>\n'
        "<!-- /wp:heading -->\n\n"
        '<!-- wp:heading {"level":2} -->\n'
        '<h2 class="wp-block-heading">次</h2>\n'
        "<!-- /wp:heading -->\n\n"
        '<!-- wp:heading {"level":2} -->\n'
        '<h2 class="wp-block-heading">さらに次</h2>\n'
        "<!-- /wp:heading -->"
    )

    rewritten_file = apply_rewrite_style(save_file, mode="high-security")

    assert '<!-- wp:heading {"level":2} -->' in rewritten_file
    assert '<h2 class="wp-block-heading">最初</h2>' in rewritten_file
    assert '<h3 class="wp-block-heading">次</h3>' in rewritten_file
    assert '<h3 class="wp-block-heading">さらに次</h3>' in rewritten_file
    assert rewritten_file.count('<!-- wp:heading {"level":2} -->') == 1
    assert rewritten_file.count('<!-- wp:heading {"level":3} -->') == 2
