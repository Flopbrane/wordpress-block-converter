def create_spacer_block(height: int = 40) -> str:
    """余白をWordPress Gutenbergのspacerブロックに変換します。"""
    safe_height = min(max(height, 1), 400)
    return (
        f'<!-- wp:spacer {{"height":"{safe_height}px"}} -->\n'
        f'<div style="height:{safe_height}px" aria-hidden="true" class="wp-block-spacer"></div>\n'
        "<!-- /wp:spacer -->"
    )
