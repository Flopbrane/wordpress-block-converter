"""Hi-Security Mode用の安全化ルールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

NORMAL_MODE = "normal"
HI_SECURITY_MODE = "hi-security"
CONVERSION_MODES: tuple[str, str] = (NORMAL_MODE, HI_SECURITY_MODE)

TEXT_TAGS: tuple[str, ...] = ("p", "h2", "h3", "h4", "h5", "strong", "em", "br", "hr")
LIST_TAGS: tuple[str, ...] = ("ul", "ol", "li")
MEDIA_TAGS: tuple[str, ...] = ("a", "img")
TABLE_TAGS: tuple[str, ...] = ("figure", "table", "thead", "tbody", "tr", "th", "td")
CODE_TAGS: tuple[str, ...] = ("pre", "code")

ALLOWED_TAGS: set[str] = {
    *TEXT_TAGS,
    *LIST_TAGS,
    *MEDIA_TAGS,
    *TABLE_TAGS,
    *CODE_TAGS,
}

BLOCKED_TAGS: set[str] = {
    "script",
    "iframe",
    "style",
    "object",
    "embed",
    "form",
    "input",
    "button",
    "textarea",
    "select",
}

DROP_CONTENT_TAGS: set[str] = {
    "script",
    "iframe",
    "style",
    "object",
    "embed",
    "textarea",
    "select",
}

BLOCKED_ATTRIBUTES: set[str] = {
    "onclick",
    "onload",
    "onerror",
    "onmouseover",
    # Hi-Security ModeではCSSに頼らず、Gutenberg標準ブロックを優先します。
    "style",
}

ALLOWED_ATTRIBUTES_BY_TAG: dict[str, set[str]] = {
    "a": {"href", "target", "rel", "title", "id", "class"},
    "img": {"src", "alt", "title", "id", "class"},
    "h2": {"id", "class"},
    "h3": {"id", "class"},
    "h4": {"id", "class"},
    "h5": {"id", "class"},
    "p": {"id", "class"},
    "hr": {"id", "class"},
    "table": {"id", "class"},
    "figure": {"id", "class"},
    "thead": {"id", "class"},
    "tbody": {"id", "class"},
    "tr": {"id", "class"},
    "th": {"id", "class"},
    "td": {"id", "class"},
    "pre": {"id", "class"},
    "code": {"id", "class"},
}

ALLOWED_HREF_PREFIXES: tuple[str, ...] = (
    "https://",
    "mailto:",
    "tel:",
    "/",
    "#",
)

ALLOWED_SRC_PREFIXES: tuple[str, ...] = (
    "https://",
    "/",
)

BLOCKED_URL_PREFIXES: tuple[str, ...] = (
    "javascript:",
    "data:",
    "vbscript:",
    "http://",
)

EMBED_BLOCK_PATTERN_TEXT = (
    r"<!--\s*wp:embed\b[^>]*-->\s*"
    r"<figure\b[^>]*>\s*"
    r"<div\b[^>]*>\s*"
    r"(https?://[^\s<]+)\s*"
    r"</div>\s*"
    r"</figure>\s*"
    r"<!--\s*/wp:embed\s*-->"
)

SHORT_CODE_MAX_LINES = 6

CODE_BLOCK_PATTERN_TEXT = (
    r"(?:<!--\s*wp:code\b[^>]*-->\s*)?"
    r"<pre\b[^>]*>\s*"
    r"<code\b[^>]*>(.*?)</code>\s*"
    r"</pre>\s*"
    r"(?:<!--\s*/wp:code\s*-->)?"
)

PARAGRAPH_SEPARATOR_PATTERN_TEXT = (
    r"(?:<!--\s*wp:paragraph\s*-->\s*)?"
    r"<p\b[^>]*>\s*(?:-{3,}|\*{3,}|_{3,})\s*</p>\s*"
    r"(?:<!--\s*/wp:paragraph\s*-->)?"
)
