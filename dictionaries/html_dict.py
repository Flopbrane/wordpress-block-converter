import re

from blocks.code import create_code_block
from blocks.embed import create_embed_block
from blocks.heading import create_heading_block
from blocks.html_block import create_html_block
from blocks.list_block import create_list_block
from blocks.paragraph import create_paragraph_block
from blocks.quote import create_quote_block
from blocks.spacer import create_spacer_block


HTML_EXTENSIONS = {".html", ".htm"}

HTML_FORMAT_NAME = "html"

WORDPRESS_CORE_BLOCKS = {
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

PRIORITY_BLOCK_COMMENT_NAMES = {
    "paragraph": "paragraph",
    "heading": "heading",
    "html": "html",
    "list": "list",
    "code": "code",
    "spacer": "spacer",
}

VIDEO_EMBED_PROVIDERS = {
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

ALLOWED_HTML_TAGS = {
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
}

# 今後使用
FUTURE_ALLOWED_HTML_TAGS = {
    "image",
    "audio",
    "video",
    "file",
}

HTML_PARAGRAPH_PATTERN = re.compile(r"<p\b[^>]*>(.*?)</p>", re.IGNORECASE | re.DOTALL)
HTML_HEADING_PATTERN = re.compile(r"<h([1-6])\b[^>]*>(.*?)</h\1>", re.IGNORECASE | re.DOTALL)
HTML_UNORDERED_LIST_PATTERN = re.compile(r"<ul\b[^>]*>(.*?)</ul>", re.IGNORECASE | re.DOTALL)
HTML_ORDERED_LIST_PATTERN = re.compile(r"<ol\b[^>]*>(.*?)</ol>", re.IGNORECASE | re.DOTALL)
HTML_LIST_ITEM_PATTERN = re.compile(r"<li\b[^>]*>(.*?)</li>", re.IGNORECASE | re.DOTALL)
HTML_QUOTE_PATTERN = re.compile(r"<blockquote\b[^>]*>(.*?)</blockquote>", re.IGNORECASE | re.DOTALL)
HTML_CODE_PATTERN = re.compile(
    r"<pre\b[^>]*>(.*?)</pre>|<code\b[^>]*>(.*?)</code>",
    re.IGNORECASE | re.DOTALL,
)
HTML_TABLE_PATTERN = re.compile(r"<table\b[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL)
HTML_SPACER_PATTERN = re.compile(r"<hr\b[^>]*>", re.IGNORECASE)
EMBED_URL_PATTERN = re.compile(r"^https?://[^\s<]+$", re.IGNORECASE)
HTML_BR_PATTERN = re.compile(r"<br\s*/?>", re.IGNORECASE)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")

HTML_BLOCK_RULES = {
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
        "converter": create_html_block,
    },
    "spacer": {
        "name": "spacer",
        "pattern": HTML_SPACER_PATTERN,
        "converter": create_spacer_block,
        "height": 40,
    },
}

HTML_EMBED_RULE = {
    "name": "embed",
    "pattern": EMBED_URL_PATTERN,
    "converter": create_embed_block,
    "providers": VIDEO_EMBED_PROVIDERS,
}
