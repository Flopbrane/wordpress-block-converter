"""Hi-Security Mode用のHTML安全化フィルターです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from html import escape, unescape
from html.parser import HTMLParser

from dictionaries.hi_security_dict import (
    ALLOWED_ATTRIBUTES_BY_TAG,
    ALLOWED_HREF_PREFIXES,
    ALLOWED_SRC_PREFIXES,
    ALLOWED_TAGS,
    BLOCKED_ATTRIBUTES,
    BLOCKED_TAGS,
    BLOCKED_URL_PREFIXES,
    CODE_BLOCK_PATTERN_TEXT,
    DROP_CONTENT_TAGS,
    EMBED_BLOCK_PATTERN_TEXT,
    PARAGRAPH_SEPARATOR_PATTERN_TEXT,
    SHORT_CODE_MAX_LINES,
)

EMBED_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    EMBED_BLOCK_PATTERN_TEXT,
    re.IGNORECASE | re.DOTALL,
)
CODE_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    CODE_BLOCK_PATTERN_TEXT,
    re.IGNORECASE | re.DOTALL,
)
PARAGRAPH_SEPARATOR_PATTERN: re.Pattern[str] = re.compile(
    PARAGRAPH_SEPARATOR_PATTERN_TEXT,
    re.IGNORECASE | re.DOTALL,
)
HEADING_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*wp:heading\b[^>]*-->\s*"
    r"<h([1-6])(\s[^>]*)?>(.*?)</h\1>\s*"
    r"<!--\s*/wp:heading\s*-->",
    re.IGNORECASE | re.DOTALL,
)
SAFE_BLOCK_START_COMMENT_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*wp:(paragraph|heading|code|table|separator)(?:\s+\{\"level\":[2-5]\})?\s*$"
)
SAFE_BLOCK_END_COMMENT_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*/wp:(paragraph|heading|code|table|separator)\s*$"
)

HEADING_LEVEL_MAP: dict[str, str] = {
    "h1": "h2",
    "h6": "h5",
}


def apply_hi_security_filter(save_file: str) -> str:
    """変換後HTMLを、制限の強いWordPress向けの安全HTMLに整えます。"""
    save_file = EMBED_BLOCK_PATTERN.sub(_convert_embed_block_to_link, save_file)
    save_file = HEADING_BLOCK_PATTERN.sub(_normalize_heading_block, save_file)
    save_file = PARAGRAPH_SEPARATOR_PATTERN.sub(_create_separator_block, save_file)
    save_file = CODE_BLOCK_PATTERN.sub(_convert_short_code_block_to_paragraph, save_file)
    parser = HiSecurityHTMLFilter()
    parser.feed(save_file)
    parser.close()
    return parser.get_html().strip()


def _convert_embed_block_to_link(embed_match: re.Match[str]) -> str:
    url: str = embed_match.group(1).strip()
    safe_url: str = escape(url, quote=True)
    return (
        "<!-- wp:paragraph -->\n"
        f'<p><a href="{safe_url}">{safe_url}</a></p>\n'
        "<!-- /wp:paragraph -->"
    )


def _normalize_heading_block(heading_match: re.Match[str]) -> str:
    heading_level = _normalize_heading_level(int(heading_match.group(1)))
    attrs = heading_match.group(2) or ""
    heading_text = heading_match.group(3)
    return (
        f'<!-- wp:heading {{"level":{heading_level}}} -->\n'
        f"<h{heading_level}{attrs}>{heading_text}</h{heading_level}>\n"
        "<!-- /wp:heading -->"
    )


def _normalize_heading_level(level: int) -> int:
    if level <= 2:
        return 2
    if level >= 5:
        return 5
    return level


def _create_separator_block(_separator_match: re.Match[str]) -> str:
    return (
        "<!-- wp:separator -->\n"
        '<hr class="wp-block-separator has-alpha-channel-opacity"/>\n'
        "<!-- /wp:separator -->"
    )


def _convert_short_code_block_to_paragraph(code_match: re.Match[str]) -> str:
    code_text: str = code_match.group(1).strip()
    if not _should_convert_code_to_paragraph(code_text):
        return code_match.group(0)

    code_lines = [
        f"<code>{escape(unescape(line.strip()), quote=False)}</code>"
        for line in code_text.splitlines()
        if line.strip()
    ]
    return (
        "<!-- wp:paragraph -->\n"
        f"<p>{'<br><br>'.join(code_lines)}</p>\n"
        "<!-- /wp:paragraph -->"
    )


def _should_convert_code_to_paragraph(code_text: str) -> bool:
    clean_lines: list[str] = [
        line.strip()
        for line in code_text.splitlines()
        if line.strip()
    ]
    if not clean_lines or len(clean_lines) > SHORT_CODE_MAX_LINES:
        return False

    return any(_looks_like_html_tag_example(line) for line in clean_lines)


def _looks_like_html_tag_example(line: str) -> bool:
    plain_line: str = unescape(line)
    return bool(re.search(r"</?[a-zA-Z][\w:-]*(?:\s[^>]*)?>", plain_line))


class HiSecurityHTMLFilter(HTMLParser):
    """許可タグと安全な属性だけを残すHTMLParserです。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._parts: list[str] = []
        self._drop_content_depth: int = 0
        self._open_tags: list[str] = []
        self._open_block_comments: list[str] = []

    def get_html(self) -> str:
        """安全化したHTMLを返します。"""
        return "".join(self._parts)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = _normalize_tag(tag)

        if self._drop_content_depth:
            self._drop_content_depth += int(clean_tag in DROP_CONTENT_TAGS)
            return

        if clean_tag in DROP_CONTENT_TAGS:
            self._drop_content_depth = 1
            return

        if clean_tag in BLOCKED_TAGS:
            return

        output_tag = _map_heading_tag(clean_tag)
        if output_tag not in ALLOWED_TAGS:
            return

        clean_attrs = _filter_attributes(output_tag, attrs)
        if output_tag == "a" and not _has_attribute(clean_attrs, "href"):
            return
        if output_tag == "img" and not _has_attribute(clean_attrs, "src"):
            return

        self._parts.append(_build_start_tag(output_tag, clean_attrs))

        if output_tag != "br":
            self._open_tags.append(output_tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        clean_tag = _normalize_tag(tag)

        if self._drop_content_depth or clean_tag in DROP_CONTENT_TAGS:
            return

        if clean_tag in BLOCKED_TAGS:
            return

        output_tag = _map_heading_tag(clean_tag)
        if output_tag not in ALLOWED_TAGS:
            return

        clean_attrs = _filter_attributes(output_tag, attrs)
        if output_tag == "img" and not _has_attribute(clean_attrs, "src"):
            return

        if output_tag in {"br", "hr", "img"}:
            self._parts.append(_build_start_tag(output_tag, clean_attrs))

    def handle_endtag(self, tag: str) -> None:
        clean_tag = _normalize_tag(tag)

        if self._drop_content_depth:
            if clean_tag in DROP_CONTENT_TAGS:
                self._drop_content_depth -= 1
            return

        if clean_tag in BLOCKED_TAGS:
            return

        output_tag = _map_heading_tag(clean_tag)
        if output_tag in ALLOWED_TAGS and output_tag in self._open_tags:
            self._parts.append(f"</{output_tag}>")
            self._open_tags.remove(output_tag)

    def handle_data(self, data: str) -> None:
        if not self._drop_content_depth:
            self._parts.append(escape(data))

    def handle_entityref(self, name: str) -> None:
        if not self._drop_content_depth:
            self._parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._drop_content_depth:
            self._parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if self._drop_content_depth:
            return

        start_match = SAFE_BLOCK_START_COMMENT_PATTERN.match(data)
        if start_match:
            block_name = start_match.group(1)
            self._open_block_comments.append(block_name)
            self._parts.append(f"<!--{data}-->")
            return

        end_match = SAFE_BLOCK_END_COMMENT_PATTERN.match(data)
        if not end_match:
            return

        block_name = end_match.group(1)
        if block_name in self._open_block_comments:
            self._parts.append(f"<!--{data}-->")
            self._open_block_comments.remove(block_name)


def _normalize_tag(tag: str) -> str:
    return tag.lower().strip()


def _map_heading_tag(tag: str) -> str:
    return HEADING_LEVEL_MAP.get(tag, tag)


def _filter_attributes(
    tag: str,
    attrs: list[tuple[str, str | None]],
) -> list[tuple[str, str]]:
    allowed_attributes = ALLOWED_ATTRIBUTES_BY_TAG.get(tag, set())
    clean_attrs: list[tuple[str, str]] = []

    for name, value in attrs:
        clean_name = name.lower().strip()
        clean_value = (value or "").strip()

        if clean_name in BLOCKED_ATTRIBUTES:
            continue

        if clean_name not in allowed_attributes:
            continue

        if clean_name == "href" and not _is_allowed_url(clean_value, ALLOWED_HREF_PREFIXES):
            continue

        if clean_name == "src" and not _is_allowed_url(clean_value, ALLOWED_SRC_PREFIXES):
            continue

        if clean_name == "target" and clean_value != "_blank":
            continue

        clean_attrs.append((clean_name, clean_value))

    if tag == "a":
        clean_attrs = _ensure_noopener(clean_attrs)

    return clean_attrs


def _has_attribute(attrs: list[tuple[str, str]], name: str) -> bool:
    return any(attr_name == name for attr_name, _ in attrs)


def _is_allowed_url(url: str, allowed_prefixes: tuple[str, ...]) -> bool:
    lower_url = url.lower()
    if lower_url.startswith(BLOCKED_URL_PREFIXES):
        return False

    return lower_url.startswith(allowed_prefixes)


def _ensure_noopener(attrs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    has_blank_target = any(
        name == "target" and value == "_blank"
        for name, value in attrs
    )
    if not has_blank_target:
        return attrs

    for index, (name, value) in enumerate(attrs):
        if name != "rel":
            continue

        rel_values = value.split()
        if "noopener" not in rel_values:
            rel_values.append("noopener")
        attrs[index] = (name, " ".join(rel_values))
        return attrs

    attrs.append(("rel", "noopener"))
    return attrs


def _build_start_tag(tag: str, attrs: list[tuple[str, str]]) -> str:
    if not attrs:
        return f"<{tag}>"

    attr_text = " ".join(
        f'{name}="{escape(value, quote=True)}"'
        for name, value in attrs
    )
    return f"<{tag} {attr_text}>"
