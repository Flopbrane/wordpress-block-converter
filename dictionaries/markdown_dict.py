import re

from blocks.code import create_code_block
from blocks.embed import create_embed_block
from blocks.heading import create_heading_block
from blocks.image import create_image_block
from blocks.list_block import create_list_block
from blocks.quote import create_quote_block
from blocks.spacer import create_spacer_block


MARKDOWN_EXTENSIONS = {".md", ".markdown"}

MARKDOWN_FORMAT_NAME = "markdown"

MARKDOWN_HEADING_MARK = "#"

MARKDOWN_UNORDERED_LIST_MARKS = {"-", "*", "+"}

MARKDOWN_CODE_FENCE = "```"

MARKDOWN_HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$")
MARKDOWN_UNORDERED_LIST_PATTERN = re.compile(r"^\s*[-*+]\s+(.+)$")
MARKDOWN_ORDERED_LIST_PATTERN = re.compile(r"^\s*\d+[.)]\s+(.+)$")
MARKDOWN_QUOTE_PATTERN = re.compile(r"^\s*>\s?(.+)$")
MARKDOWN_SPACER_PATTERN = re.compile(r"^\s*\[spacer(?::(\d+))?\]\s*$", re.IGNORECASE)
MARKDOWN_IMAGE_PATTERN = re.compile(r"^!\[([^\]]*)\]\((https?://[^\s)]+)\)$")
MARKDOWN_EMBED_URL_PATTERN = re.compile(r"^https?://[^\s<]+$", re.IGNORECASE)

MARKDOWN_HEADING_RULE = {
    "name": "heading",
    "pattern": MARKDOWN_HEADING_PATTERN,
    "converter": create_heading_block,
}

MARKDOWN_LIST_RULES = {
    "unordered": {
        "name": "unordered_list",
        "pattern": MARKDOWN_UNORDERED_LIST_PATTERN,
        "converter": create_list_block,
        "ordered": False,
        "use_html_block": True,
    },
    "ordered": {
        "name": "ordered_list",
        "pattern": MARKDOWN_ORDERED_LIST_PATTERN,
        "converter": create_list_block,
        "ordered": True,
        "use_html_block": True,
    },
}

MARKDOWN_CODE_RULE = {
    "name": "code",
    "fence": MARKDOWN_CODE_FENCE,
    "converter": create_code_block,
}

MARKDOWN_QUOTE_RULE = {
    "name": "quote",
    "pattern": MARKDOWN_QUOTE_PATTERN,
    "converter": create_quote_block,
}

MARKDOWN_SPACER_RULE = {
    "name": "spacer",
    "pattern": MARKDOWN_SPACER_PATTERN,
    "converter": create_spacer_block,
    "default_height": 40,
}

MARKDOWN_IMAGE_RULE = {
    "name": "image",
    "pattern": MARKDOWN_IMAGE_PATTERN,
    "converter": create_image_block,
}

MARKDOWN_EMBED_RULE = {
    "name": "embed",
    "pattern": MARKDOWN_EMBED_URL_PATTERN,
    "converter": create_embed_block,
}
