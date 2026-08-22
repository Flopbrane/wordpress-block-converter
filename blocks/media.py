import json
from html import escape


def create_video_block(src: str) -> str:
    """動画ファイルURLをWordPress Gutenbergのvideoブロックに変換します。"""
    safe_src = escape(src.strip(), quote=True)
    attribute_text = json.dumps({"src": src.strip()}, ensure_ascii=False, separators=(",", ":"))
    return (
        f"<!-- wp:video {attribute_text} -->\n"
        '<figure class="wp-block-video">'
        f'<video controls src="{safe_src}"></video>'
        "</figure>\n"
        "<!-- /wp:video -->"
    )


def create_audio_block(src: str) -> str:
    """音声ファイルURLをWordPress Gutenbergのaudioブロックに変換します。"""
    safe_src = escape(src.strip(), quote=True)
    attribute_text = json.dumps({"src": src.strip()}, ensure_ascii=False, separators=(",", ":"))
    return (
        f"<!-- wp:audio {attribute_text} -->\n"
        '<figure class="wp-block-audio">'
        f'<audio controls src="{safe_src}"></audio>'
        "</figure>\n"
        "<!-- /wp:audio -->"
    )


def create_file_block(url: str) -> str:
    """ファイルURLをWordPress Gutenbergのfileブロックに変換します。"""
    safe_url = escape(url.strip(), quote=True)
    file_name = url.strip().rstrip("/").split("/")[-1] or "download"
    safe_file_name = escape(file_name)
    attribute_text = json.dumps({"href": url.strip()}, ensure_ascii=False, separators=(",", ":"))
    return (
        f"<!-- wp:file {attribute_text} -->\n"
        f'<div class="wp-block-file"><a href="{safe_url}">{safe_file_name}</a></div>\n'
        "<!-- /wp:file -->"
    )
