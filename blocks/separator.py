def create_separator_block() -> str:
    """区切り線をWordPress Gutenbergのseparatorブロックに変換します。"""
    return (
        "<!-- wp:separator -->\n"
        '<hr class="wp-block-separator has-alpha-channel-opacity"/>\n'
        "<!-- /wp:separator -->"
    )
