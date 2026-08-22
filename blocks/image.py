import json
from html import escape


def create_image_block(src: str, alt: str = "") -> str:
    """画像URLをWordPress Gutenbergのimageブロックに変換します。"""
    safe_src = escape(src.strip(), quote=True)
    safe_alt = escape(alt.strip(), quote=True)
    attributes = {"url": src.strip(), "alt": alt.strip()}
    attribute_text = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))

    return (
        f"<!-- wp:image {attribute_text} -->\n"
        '<figure class="wp-block-image">'
        f'<img src="{safe_src}" alt="{safe_alt}"/>'
        "</figure>\n"
        "<!-- /wp:image -->"
    )
