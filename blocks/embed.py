import json
from html import escape


def create_embed_block(
    url: str,
    provider_name_slug: str,
    embed_type: str = "video",
    responsive: bool = True,
) -> str:
    """外部URLをWordPress Gutenbergのembedブロックに変換します。"""
    safe_url = escape(url.strip())
    class_names = [
        "wp-block-embed",
        f"is-type-{embed_type}",
        f"is-provider-{provider_name_slug}",
        f"wp-block-embed-{provider_name_slug}",
    ]
    attributes = {
        "url": url.strip(),
        "type": embed_type,
        "providerNameSlug": provider_name_slug,
        "responsive": responsive,
    }

    if provider_name_slug in {"youtube", "vimeo"}:
        class_names.extend(["wp-embed-aspect-16-9", "wp-has-aspect-ratio"])
        attributes["className"] = "wp-embed-aspect-16-9 wp-has-aspect-ratio"

    attribute_text = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))
    class_text = " ".join(class_names)

    return (
        f"<!-- wp:embed {attribute_text} -->\n"
        f'<figure class="{class_text}">\n'
        '<div class="wp-block-embed__wrapper">\n'
        f"{safe_url}\n"
        "</div>\n"
        "</figure>\n"
        "<!-- /wp:embed -->"
    )
