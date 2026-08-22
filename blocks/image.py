"""画像をWordPress Gutenberg向けHTMLに変換するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import json
from html import escape


def create_image_block(src: str, alt: str = "") -> str:
    """画像URLをWordPress Gutenbergのimageブロックに変換します。"""
    safe_src: str = escape(src.strip(), quote=True)
    safe_alt: str = escape(alt.strip(), quote=True)
    attributes: dict[str, str] = {"url": src.strip(), "alt": alt.strip()}
    attribute_text: str = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))

    return (
        f"<!-- wp:image {attribute_text} -->\n"
        '<figure class="wp-block-image">'
        f'<img src="{safe_src}" alt="{safe_alt}"/>'
        "</figure>\n"
        "<!-- /wp:image -->"
    )
