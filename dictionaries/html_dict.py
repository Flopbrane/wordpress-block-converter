"""HTML変換用の辞書ファイルです"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re

from blocks.code import create_code_block
from blocks.embed import create_embed_block
from blocks.heading import create_heading_block
from blocks.html_block import create_html_block
from blocks.image import create_image_block
from blocks.list_block import create_list_block
from blocks.media import create_audio_block, create_file_block, create_video_block
from blocks.paragraph import create_paragraph_block
from blocks.quote import create_quote_block
from blocks.separator import create_separator_block
from blocks.shortcode import create_shortcode_block
from blocks.table import create_table_block

HTML_EXTENSIONS: set[str] = {".html", ".htm", ".wp_html"}

HTML_FORMAT_NAME = "html"

WORDPRESS_CORE_BLOCKS: dict[str, str] = {
    "paragraph": "core/paragraph",
    "heading": "core/heading",
    "list": "core/list",
    "list_item": "core/list-item",
    "quote": "core/quote",
    "code": "core/code",
    "preformatted": "core/preformatted",
    "verse": "core/verse",
    "table": "core/table",
    "html": "core/html",
    "image": "core/image",
    "gallery": "core/gallery",
    "video": "core/video",
    "audio": "core/audio",
    "file": "core/file",
    "separator": "core/separator",
    "spacer": "core/spacer",
    "group": "core/group",
    "columns": "core/columns",
    "column": "core/column",
    "buttons": "core/buttons",
    "button": "core/button",
    "more": "core/more",
    "nextpage": "core/nextpage",
    "shortcode": "core/shortcode",
    "embed": "core/embed",
}

PRIORITY_BLOCK_COMMENT_NAMES: dict[str, str] = {
    "paragraph": "paragraph",
    "heading": "heading",
    "html": "html",
    "list": "list",
    "code": "code",
    "spacer": "spacer",
}

VIDEO_EMBED_PROVIDERS: dict[str, str] = {
    "youtube.com/shorts": "youtube",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "tiktok.com": "tiktok",
    "vimeo.com": "vimeo",
    # 今後使用
    "dailymotion.com": "dailymotion",
    "ted.com": "ted",
    "wordpress.tv": "wordpress-tv",
    "videopress.com": "videopress",
    "facebook.com": "facebook",
    "instagram.com": "instagram",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "twitch.tv": "twitch",
}

IMAGE_URL_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".avif"}
VIDEO_FILE_EXTENSIONS: set[str] = {".mp4", ".webm", ".mov", ".m4v"}
AUDIO_FILE_EXTENSIONS: set[str] = {".mp3", ".wav", ".ogg", ".m4a"}
DOWNLOAD_FILE_EXTENSIONS: set[str] = {
    ".pdf", ".zip", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
    }

EMBED_PROVIDER_RULES: dict[str, dict[str, str | bool | None]] = {
    "youtube.com/shorts": {
        "providerNameSlug": "youtube",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "youtube.com": {
        "providerNameSlug": "youtube",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "youtu.be": {
        "providerNameSlug": "youtube",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "tiktok.com": {
        "providerNameSlug": "tiktok",
        "type": "video",
        "responsive": True,
        "aspect": None,
    },
    "vimeo.com": {
        "providerNameSlug": "vimeo",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "instagram.com": {
        "providerNameSlug": "instagram",
        "type": "rich",
        "responsive": True,
        "aspect": None,
    },
    "twitter.com": {
        "providerNameSlug": "twitter",
        "type": "rich",
        "responsive": True,
        "aspect": None,
    },
    "x.com": {
        "providerNameSlug": "twitter",
        "type": "rich",
        "responsive": True,
        "aspect": None,
    },
    "dailymotion.com": {
        "providerNameSlug": "dailymotion",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "twitch.tv": {
        "providerNameSlug": "twitch",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "wordpress.tv": {
        "providerNameSlug": "wordpress-tv",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "videopress.com": {
        "providerNameSlug": "videopress",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "facebook.com": {
        "providerNameSlug": "facebook",
        "type": "rich",
        "responsive": True,
        "aspect": None,
    },
    "ted.com": {
        "providerNameSlug": "ted",
        "type": "video",
        "responsive": True,
        "aspect": "16-9",
    },
    "spotify.com": {
        "providerNameSlug": "spotify",
        "type": "rich",
        "responsive": True,
        "aspect": None,
    },
    "soundcloud.com": {
        "providerNameSlug": "soundcloud",
        "type": "rich",
        "responsive": True,
        "aspect": None,
    },
}

ALLOWED_HTML_TAGS: set[str] = {
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "pre",
    "code",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "hr",
    "img",
    "a",
    "strong",
    "b",
    "em",
    "i",
}

# 今後使用
FUTURE_ALLOWED_HTML_TAGS: set[str] = {
    "image",
    "audio",
    "video",
    "file",
}

HTML_PARAGRAPH_PATTERN: re.Pattern[str] = re.compile(
    r"<p\b[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL
    )
HTML_HEADING_PATTERN: re.Pattern[str] = re.compile(
    r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL
    )
HTML_UNORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(
    r"<ul\b[^>]*>(.*?)</ul>", re.IGNORECASE | re.DOTALL
)
HTML_ORDERED_LIST_PATTERN: re.Pattern[str] = re.compile(
    r"<ol\b[^>]*>(.*?)</ol>", re.IGNORECASE | re.DOTALL
)
HTML_LIST_ITEM_PATTERN: re.Pattern[str] = re.compile(
    r"<li\b[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL
)
HTML_QUOTE_PATTERN: re.Pattern[str] = re.compile(
    r"<blockquote\b[^>]*>(.*?)</blockquote>", re.IGNORECASE | re.DOTALL
)
HTML_LINK_PATTERN: re.Pattern[str] = re.compile(
    r"<a\b[^>]*href\s*=\s*['\"]([^'\"]+)['\"][^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
HTML_STRONG_PATTERN: re.Pattern[str] = re.compile(
    r"<(strong|b)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL
)
HTML_EMPHASIS_PATTERN: re.Pattern[str] = re.compile(
    r"<(em|i)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL
)
HTML_CODE_PATTERN: re.Pattern[str] = re.compile(
    r"<pre\b[^>]*>(.*?)</pre>|<code\b[^>]*>(.*?)</code>",
    re.IGNORECASE | re.DOTALL,
)
HTML_TABLE_PATTERN: re.Pattern[str] = re.compile(
    r"<table\b[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL
)
HTML_IMAGE_PATTERN: re.Pattern[str] = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
HTML_ATTRIBUTE_PATTERN: re.Pattern[str] = re.compile(
    r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*["\']([^"\']*)["\']'
)
HTML_SPACER_PATTERN: re.Pattern[str] = re.compile(r"<hr\b[^>]*>", re.IGNORECASE)
HTML_SHORTCODE_PATTERN: re.Pattern[str] = re.compile(r"^\s*\[[A-Za-z0-9_-]+(?:\s+[^\]]*)?\]\s*$")
EMBED_URL_PATTERN: re.Pattern[str] = re.compile(r"^https?://[^\s<]+$", re.IGNORECASE)
HTML_BR_PATTERN: re.Pattern[str] = re.compile(r"<br\s*/?>", re.IGNORECASE)
HTML_TAG_PATTERN: re.Pattern[str] = re.compile(r"<[^>]+>")

DIRECT_URL_RULES: dict[str, dict[str, object]] = {
    "image": {
        "extensions": IMAGE_URL_EXTENSIONS,
        "converter": create_image_block,
    },
    "video": {
        "extensions": VIDEO_FILE_EXTENSIONS,
        "converter": create_video_block,
    },
    "audio": {
        "extensions": AUDIO_FILE_EXTENSIONS,
        "converter": create_audio_block,
    },
    "file": {
        "extensions": DOWNLOAD_FILE_EXTENSIONS,
        "converter": create_file_block,
    },
}

HTML_BLOCK_RULES: dict[str, dict[str, object]] = {
    "paragraph": {
        "name": "paragraph",
        "pattern": HTML_PARAGRAPH_PATTERN,
        "converter": create_paragraph_block,
    },
    "heading": {
        "name": "heading",
        "pattern": HTML_HEADING_PATTERN,
        "converter": create_heading_block,
    },
    "unordered_list": {
        "name": "unordered_list",
        "pattern": HTML_UNORDERED_LIST_PATTERN,
        "converter": create_list_block,
        "ordered": False,
        "use_html_block": True,
    },
    "ordered_list": {
        "name": "ordered_list",
        "pattern": HTML_ORDERED_LIST_PATTERN,
        "converter": create_list_block,
        "ordered": True,
        "use_html_block": True,
    },
    "quote": {
        "name": "quote",
        "pattern": HTML_QUOTE_PATTERN,
        "converter": create_quote_block,
    },
    "code": {
        "name": "code",
        "pattern": HTML_CODE_PATTERN,
        "converter": create_code_block,
    },
    "table": {
        "name": "table",
        "pattern": HTML_TABLE_PATTERN,
        "converter": create_table_block,
        "fallback_converter": create_html_block,
    },
    "image": {
        "name": "image",
        "pattern": HTML_IMAGE_PATTERN,
        "converter": create_image_block,
    },
    "spacer": {
        "name": "separator",
        "pattern": HTML_SPACER_PATTERN,
        "converter": create_separator_block,
    },
}

HTML_SHORTCODE_RULE: dict[str, object] = {
    "name": "shortcode",
    "pattern": HTML_SHORTCODE_PATTERN,
    "converter": create_shortcode_block,
}

HTML_EMBED_RULE: dict[str, object] = {
    "name": "embed",
    "pattern": EMBED_URL_PATTERN,
    "converter": create_embed_block,
    "providers": VIDEO_EMBED_PROVIDERS,
}
