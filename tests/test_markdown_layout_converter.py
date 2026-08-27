"""Markdown独自レイアウト記法のテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from converters.markdown_converter import convert_markdown_to_gutenberg


def test_convert_markdown_image_text_left_layout() -> None:
    """画像＋文章の独自レイアウトをmedia-textへ変換するテストです。"""
    load_file = """
:::image_text_left
image: https://example.com/service.jpg
alt: サービス紹介画像
title: 私たちのサービス
text: ここに説明文を入れます。
width: 40
:::
"""

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<!-- wp:media-text" in save_file
    assert '"mediaPosition":"left"' in save_file
    assert '"mediaWidth":40' in save_file
    assert '<img src="https://example.com/service.jpg" alt="サービス紹介画像"/>' in save_file
    assert '<h2 class="wp-block-heading">私たちのサービス</h2>' in save_file
    assert "<p>ここに説明文を入れます。</p>" in save_file


def test_convert_markdown_image_row_3_layout() -> None:
    """画像横並びの独自レイアウトをcolumnsへ変換するテストです。"""
    load_file = """
:::image_row_3
gap: 0
image1: https://example.com/one.jpg
alt1: 画像1
image2: https://example.com/two.jpg
alt2: 画像2
image3: https://example.com/three.jpg
alt3: 画像3
:::
"""

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<!-- wp:columns" in save_file
    assert '"blockGap":"0px"' in save_file
    assert save_file.count("<!-- wp:column -->") == 3
    assert '<img src="https://example.com/three.jpg" alt="画像3"/>' in save_file


def test_convert_markdown_cta_layout() -> None:
    """CTA独自レイアウトを見出し、段落、ボタンへ変換するテストです。"""
    load_file = """
:::cta
title: まずはご相談ください
text: 初回相談は無料です。
button: お問い合わせ
url: https://example.com/contact
:::
"""

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<h2 class="wp-block-heading">まずはご相談ください</h2>' in save_file
    assert "<p>初回相談は無料です。</p>" in save_file
    assert "<!-- wp:buttons -->" in save_file
    assert 'href="https://example.com/contact"' in save_file
    assert ">お問い合わせ</a>" in save_file


def test_convert_markdown_faq_layout() -> None:
    """FAQ独自レイアウトを見出しと段落へ変換するテストです。"""
    load_file = """
:::faq
title: よくある質問
q1: 相談できますか？
a1: はい、可能です。
q2: 見積もりは無料ですか？
a2: 無料です。
:::
"""

    save_file = convert_markdown_to_gutenberg(load_file)

    assert '<h2 class="wp-block-heading">よくある質問</h2>' in save_file
    assert '<h3 class="wp-block-heading">相談できますか？</h3>' in save_file
    assert "<p>はい、可能です。</p>" in save_file
    assert '<h3 class="wp-block-heading">見積もりは無料ですか？</h3>' in save_file
    assert "<p>無料です。</p>" in save_file


def test_convert_markdown_cards_layout() -> None:
    """カード型独自レイアウトをcolumnsへ変換するテストです。"""
    load_file = """
:::cards
gap: 24
title1: 企画
text1: 構成を作ります。
title2: 制作
text2: ページを作ります。
:::
"""

    save_file = convert_markdown_to_gutenberg(load_file)

    assert "<!-- wp:columns" in save_file
    assert '"blockGap":"24px"' in save_file
    assert '<h3 class="wp-block-heading">企画</h3>' in save_file
    assert "<p>ページを作ります。</p>" in save_file
