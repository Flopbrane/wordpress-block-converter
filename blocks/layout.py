"""LP向けレイアウトをWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import json
from html import escape

from blocks.heading import create_heading_block
from blocks.image import create_image_block
from blocks.paragraph import create_paragraph_block


def create_media_text_block(
    image: str,
    alt: str = "",
    title: str = "",
    text: str = "",
    media_position: str = "left",
    media_width: int = 40,
) -> str:
    """画像＋文章をWordPressのmedia-textブロックに変換します。"""
    safe_image = escape(image.strip(), quote=True)
    safe_alt = escape(alt.strip(), quote=True)
    safe_position = "right" if media_position == "right" else "left"
    safe_width = min(max(media_width, 20), 80)
    attributes = {
        "mediaPosition": safe_position,
        "mediaType": "image",
        "mediaWidth": safe_width,
    }
    attribute_text = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))
    content_blocks = []

    if title.strip():
        content_blocks.append(create_heading_block(title, 2))
    if text.strip():
        content_blocks.append(create_paragraph_block(text))

    content_html = "\n\n".join(content_blocks)
    return (
        f"<!-- wp:media-text {attribute_text} -->\n"
        '<div class="wp-block-media-text is-stacked-on-mobile">'
        '<figure class="wp-block-media-text__media">'
        f'<img src="{safe_image}" alt="{safe_alt}"/>'
        "</figure>"
        '<div class="wp-block-media-text__content">\n'
        f"{content_html}\n"
        "</div></div>\n"
        "<!-- /wp:media-text -->"
    )


def create_image_columns_block(images: list[dict[str, str]], gap: str = "24px") -> str:
    """複数画像をWordPressのcolumnsブロックに変換します。"""
    clean_images = [
        image_data
        for image_data in images
        if image_data.get("image", "").strip()
    ]
    if not clean_images:
        return ""

    attributes = {"style": {"spacing": {"blockGap": _normalize_gap(gap)}}}
    attribute_text = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))
    column_blocks = []

    for image_data in clean_images:
        column_blocks.append(
            "<!-- wp:column -->\n"
            '<div class="wp-block-column">\n'
            f"{create_image_block(image_data.get('image', ''), image_data.get('alt', ''))}\n"
            "</div>\n"
            "<!-- /wp:column -->"
        )

    return (
        f"<!-- wp:columns {attribute_text} -->\n"
        '<div class="wp-block-columns">\n'
        + "\n\n".join(column_blocks)
        + "\n</div>\n"
        "<!-- /wp:columns -->"
    )


def create_cta_block(title: str, text: str, button: str, url: str) -> str:
    """CTAを見出し、段落、ボタンブロックに変換します。"""
    blocks = []
    if title.strip():
        blocks.append(create_heading_block(title, 2))
    if text.strip():
        blocks.append(create_paragraph_block(text))
    if button.strip() and url.strip():
        safe_url = escape(url.strip(), quote=True)
        safe_button = escape(button.strip())
        blocks.append(
            "<!-- wp:buttons -->\n"
            '<div class="wp-block-buttons">'
            "<!-- wp:button -->"
            f'<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="{safe_url}">{safe_button}</a></div>'
            "<!-- /wp:button -->"
            "</div>\n"
            "<!-- /wp:buttons -->"
        )

    return "\n\n".join(blocks)


def create_card_columns_block(cards: list[dict[str, str]], gap: str = "24px") -> str:
    """カード型情報をcolumnsブロックに変換します。"""
    clean_cards = [
        card
        for card in cards
        if card.get("title", "").strip() or card.get("text", "").strip()
    ]
    if not clean_cards:
        return ""

    attributes = {"style": {"spacing": {"blockGap": _normalize_gap(gap)}}}
    attribute_text = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))
    column_blocks = []

    for card in clean_cards:
        card_blocks = []
        if card.get("title", "").strip():
            card_blocks.append(create_heading_block(card["title"], 3))
        if card.get("text", "").strip():
            card_blocks.append(create_paragraph_block(card["text"]))
        column_blocks.append(
            "<!-- wp:column -->\n"
            '<div class="wp-block-column">\n'
            + "\n\n".join(card_blocks)
            + "\n</div>\n"
            "<!-- /wp:column -->"
        )

    return (
        f"<!-- wp:columns {attribute_text} -->\n"
        '<div class="wp-block-columns">\n'
        + "\n\n".join(column_blocks)
        + "\n</div>\n"
        "<!-- /wp:columns -->"
    )


def _normalize_gap(gap: str) -> str:
    clean_gap = gap.strip()
    if clean_gap.isdigit():
        return f"{clean_gap}px"
    if clean_gap.endswith(("px", "em", "rem", "%")):
        return clean_gap
    return "24px"
