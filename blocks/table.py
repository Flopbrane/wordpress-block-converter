"""HTML表をWordPress Gutenberg向けHTMLに変換するモジュールです。"""
from __future__ import annotations

import json
import re
from html import escape

from blocks.inline import format_inline_text
from dictionaries.table_templates import load_table_templates

ROW_PATTERN: re.Pattern[str] = re.compile(
    r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL
)
CELL_PATTERN: re.Pattern[str] = re.compile(
    r"<(td|th)\b([^>]*)>(.*?)</\1>", re.IGNORECASE | re.DOTALL
)
SECTION_PATTERN_TEMPLATE = r"<{tag}\b[^>]*>(.*?)</{tag}>"
TABLE_CONTENT_PATTERN: re.Pattern[str] = re.compile(
    r"<table\b[^>]*>(.*?)</table>", re.IGNORECASE | re.DOTALL
)
FIGCAPTION_PATTERN: re.Pattern[str] = re.compile(
    r"<figcaption\b[^>]*>(.*?)</figcaption>", re.IGNORECASE | re.DOTALL
)
START_TAG_PATTERN: re.Pattern[str] = re.compile(
    r"<([a-zA-Z][a-zA-Z0-9:-]*)\b([^>]*)>", re.IGNORECASE | re.DOTALL
)
ATTRIBUTE_PATTERN: re.Pattern[str] = re.compile(
    r'([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(["\'])(.*?)\2',
    re.DOTALL,
)
WORDPRESS_TABLE_COMMENT_PATTERN: re.Pattern[str] = re.compile(
    r"<!--\s*/?\s*wp:table(?:\s+\{.*?\})?\s*-->",
    re.IGNORECASE | re.DOTALL,
)
WORDPRESS_TABLE_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    r"\s*<!--\s*wp:table(?:\s+(\{.*?\}))?\s*-->.*?"
    r"<!--\s*/wp:table\s*-->\s*",
    re.IGNORECASE | re.DOTALL,
)

STRUCTURAL_TAGS = {
    "figure",
    "table",
    "thead",
    "tbody",
    "tfoot",
    "tr",
    "th",
    "td",
    "figcaption",
}
SAFE_INLINE_TAGS = {"a", "b", "br", "code", "em", "i", "span", "strong", "sub", "sup"}
CELL_ATTRIBUTE_ORDER = ("class", "data-align", "scope", "colspan", "rowspan")


def create_table_block(table_html: str) -> str:
    """HTML表を標準tableブロックまたは内容保持用Custom HTMLへ変換します。"""
    existing_layout, existing_attributes_supported = _existing_table_layout(table_html)
    clean_table_html = _strip_wordpress_table_comments(table_html).strip()
    if (
        not existing_attributes_supported
        and re.search(r"\bstyle\s*=", clean_table_html, re.IGNORECASE) is None
    ):
        return table_html.strip()
    if _requires_custom_html(clean_table_html):
        return _create_custom_table_block(clean_table_html)

    sections, caption = _extract_html_table_data(clean_table_html)
    if not any(sections.values()):
        return _create_custom_table_block(clean_table_html)

    return _create_table_block_from_sections(
        sections,
        preserve_html=True,
        caption=caption,
        fixed_layout=existing_layout,
    )


def create_table_block_from_rows(
    headers: list[str],
    rows: list[list[str]],
    convert_inline_code: bool = False,
) -> str:
    """Markdown・JSON・区切り値の行データを標準tableブロックへ変換します。"""
    sections: dict[str, list[list[dict[str, str]]]] = {
        "head": [],
        "body": [],
        "foot": [],
    }
    if headers:
        sections["head"].append(
            [{"tag": "th", "content": header.strip(), "attributes": ""} for header in headers]
        )
    sections["body"].extend(
        [
            {"tag": "td", "content": cell.strip(), "attributes": ""}
            for cell in row
        ]
        for row in rows
    )

    if not any(sections.values()):
        return ""

    return _create_table_block_from_sections(
        sections,
        convert_inline_code=convert_inline_code,
    )


def _create_table_block_from_sections(
    sections: dict[str, list[list[dict[str, str]]]],
    *,
    convert_inline_code: bool = False,
    preserve_html: bool = False,
    caption: str = "",
    fixed_layout: bool = True,
) -> str:
    templates = load_table_templates()["standard_table"]
    table_open_key = "table_open" if fixed_layout else "table_open_auto_layout"
    block_open_key = "block_open" if fixed_layout else "block_open_auto_layout"
    table_parts = [templates[table_open_key]]

    for section_name in ("head", "body", "foot"):
        rows = sections[section_name]
        if not rows:
            continue
        table_parts.append(templates["section_open"][section_name])
        table_parts.extend(
            _create_row_html(
                row,
                convert_inline_code=convert_inline_code,
                preserve_html=preserve_html,
            )
            for row in rows
        )
        table_parts.append(templates["section_close"][section_name])

    table_parts.append(templates["table_close"])
    if caption:
        table_parts.append(templates["caption"].format(content=caption.strip()))

    inner_html = "".join(table_parts)
    return "\n".join(
        (
            templates[block_open_key],
            f"{templates['figure_open']}{inner_html}{templates['figure_close']}",
            templates["block_close"],
        )
    )


def _create_custom_table_block(table_html: str) -> str:
    templates = load_table_templates()["custom_html"]
    return "\n".join(
        (templates["block_open"], table_html.strip(), templates["block_close"])
    )


def _extract_html_table_data(
    table_html: str,
) -> tuple[dict[str, list[list[dict[str, str]]]], str]:
    sections: dict[str, list[list[dict[str, str]]]] = {
        "head": [],
        "body": [],
        "foot": [],
    }
    table_match = TABLE_CONTENT_PATTERN.search(table_html)
    if table_match is None:
        return sections, ""

    table_content = table_match.group(1)
    found_explicit_section = False
    for section_name, html_tag in (("head", "thead"), ("body", "tbody"), ("foot", "tfoot")):
        section_pattern = re.compile(
            SECTION_PATTERN_TEMPLATE.format(tag=html_tag),
            re.IGNORECASE | re.DOTALL,
        )
        for section_match in section_pattern.finditer(table_content):
            found_explicit_section = True
            sections[section_name].extend(_extract_rows(section_match.group(1)))

    if not found_explicit_section:
        rows = _extract_rows(table_content)
        if rows and all(cell["tag"] == "th" for cell in rows[0]):
            sections["head"] = [rows[0]]
            sections["body"] = rows[1:]
        else:
            sections["body"] = rows

    caption_match = FIGCAPTION_PATTERN.search(table_html)
    caption = caption_match.group(1).strip() if caption_match else ""
    return sections, caption


def _extract_rows(table_content: str) -> list[list[dict[str, str]]]:
    rows: list[list[dict[str, str]]] = []
    for row_match in ROW_PATTERN.finditer(table_content):
        cells: list[dict[str, str]] = []
        for cell_match in CELL_PATTERN.finditer(row_match.group(1)):
            tag = cell_match.group(1).lower()
            cells.append(
                {
                    "tag": tag,
                    "content": cell_match.group(3).strip(),
                    "attributes": _normalize_cell_attributes(tag, cell_match.group(2)),
                }
            )
        if cells:
            rows.append(cells)
    return rows


def _create_row_html(
    row: list[dict[str, str]],
    *,
    convert_inline_code: bool = False,
    preserve_html: bool = False,
) -> str:
    templates = load_table_templates()["standard_table"]
    cells: list[str] = []
    for cell in row:
        content = (
            cell["content"]
            if preserve_html
            else format_inline_text(
                cell["content"],
                convert_inline_code=convert_inline_code,
            )
        )
        cells.append(
            templates["cell"].format(
                tag=cell["tag"],
                attributes=cell["attributes"],
                content=content,
            )
        )
    return templates["row"].format(cells="".join(cells))


def _requires_custom_html(table_html: str) -> bool:
    if re.search(r"\bstyle\s*=", table_html, re.IGNORECASE):
        return True
    if re.search(r"<caption\b", table_html, re.IGNORECASE):
        return True
    if not _table_structure_is_supported(table_html):
        return True

    for tag_match in START_TAG_PATTERN.finditer(table_html):
        tag = tag_match.group(1).lower()
        raw_attributes = tag_match.group(2)
        attributes = _extract_attributes(raw_attributes)
        if _has_unparsed_attributes(raw_attributes, attributes):
            return True
        if tag not in STRUCTURAL_TAGS and tag not in SAFE_INLINE_TAGS:
            return True
        if tag == "figure" and not _is_allowed_class_only(attributes, "wp-block-table"):
            return True
        if tag == "table" and not _is_allowed_class_only(attributes, "has-fixed-layout"):
            return True
        if tag in {"thead", "tbody", "tfoot", "tr"} and attributes:
            return True
        if tag in {"td", "th"} and not _cell_attributes_are_supported(tag, attributes):
            return True
        if tag == "figcaption" and not _is_allowed_class_only(
            attributes, "wp-element-caption"
        ):
            return True
        if tag in SAFE_INLINE_TAGS and not _inline_attributes_are_supported(tag, attributes):
            return True
    return False


def _table_structure_is_supported(table_html: str) -> bool:
    table_matches = list(TABLE_CONTENT_PATTERN.finditer(table_html))
    if len(table_matches) != 1:
        return False

    table_content = table_matches[0].group(1)
    section_patterns = [
        re.compile(
            SECTION_PATTERN_TEMPLATE.format(tag=tag),
            re.IGNORECASE | re.DOTALL,
        )
        for tag in ("thead", "tbody", "tfoot")
    ]
    section_matches = [
        match
        for section_pattern in section_patterns
        for match in section_pattern.finditer(table_content)
    ]
    if any(len(section_pattern.findall(table_content)) > 1 for section_pattern in section_patterns):
        return False

    if section_matches:
        remaining_table_content = table_content
        for section_pattern in section_patterns:
            remaining_table_content = section_pattern.sub("", remaining_table_content)
        if remaining_table_content.strip():
            return False
        if any(not _rows_cover_content(match.group(1)) for match in section_matches):
            return False
    elif not _rows_cover_content(table_content):
        return False

    remaining_outer_html = TABLE_CONTENT_PATTERN.sub("", table_html, count=1)
    remaining_outer_html = FIGCAPTION_PATTERN.sub("", remaining_outer_html, count=1)
    remaining_outer_html = re.sub(
        r"</?figure\b[^>]*>",
        "",
        remaining_outer_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return not remaining_outer_html.strip()


def _rows_cover_content(section_html: str) -> bool:
    row_matches = list(ROW_PATTERN.finditer(section_html))
    if not row_matches or ROW_PATTERN.sub("", section_html).strip():
        return False
    return all(
        bool(CELL_PATTERN.search(row_match.group(1)))
        and not CELL_PATTERN.sub("", row_match.group(1)).strip()
        for row_match in row_matches
    )


def _extract_attributes(raw_attributes: str) -> dict[str, str]:
    return {
        match.group(1).lower(): match.group(3)
        for match in ATTRIBUTE_PATTERN.finditer(raw_attributes)
    }


def _has_unparsed_attributes(
    raw_attributes: str,
    attributes: dict[str, str],
) -> bool:
    consumed = ATTRIBUTE_PATTERN.sub("", raw_attributes)
    return bool(consumed.strip(" \t\r\n/")) or len(attributes) != len(
        ATTRIBUTE_PATTERN.findall(raw_attributes)
    )


def _is_allowed_class_only(attributes: dict[str, str], allowed_class: str) -> bool:
    if not attributes:
        return True
    return attributes == {"class": allowed_class}


def _cell_attributes_are_supported(tag: str, attributes: dict[str, str]) -> bool:
    allowed = {"colspan", "rowspan", "data-align", "class"}
    if tag == "th":
        allowed.add("scope")
    if set(attributes).difference(allowed):
        return False

    for span_name in ("colspan", "rowspan"):
        if span_name in attributes:
            value = attributes[span_name]
            if not value.isdigit() or int(value) < 2:
                return False
    if "scope" in attributes and attributes["scope"] not in {"col", "row"}:
        return False

    align = attributes.get("data-align")
    class_name = attributes.get("class")
    if align is None and class_name is None:
        return True
    if align not in {"left", "center", "right"}:
        return False
    return class_name == f"has-text-align-{align}"


def _inline_attributes_are_supported(tag: str, attributes: dict[str, str]) -> bool:
    if not attributes:
        return True
    if tag == "a":
        return set(attributes).issubset({"href", "target", "rel", "title"})
    return False


def _normalize_cell_attributes(tag: str, raw_attributes: str) -> str:
    attributes = _extract_attributes(raw_attributes)
    if not _cell_attributes_are_supported(tag, attributes):
        return ""
    return "".join(
        f' {name}="{escape(attributes[name], quote=True)}"'
        for name in CELL_ATTRIBUTE_ORDER
        if name in attributes
    )


def _strip_wordpress_table_comments(table_html: str) -> str:
    return WORDPRESS_TABLE_COMMENT_PATTERN.sub("", table_html)


def _existing_table_layout(table_html: str) -> tuple[bool, bool]:
    block_match = WORDPRESS_TABLE_BLOCK_PATTERN.fullmatch(table_html)
    if block_match is None:
        return True, True

    attributes_text = block_match.group(1)
    if attributes_text is None:
        return True, True
    try:
        attributes = json.loads(attributes_text)
    except json.JSONDecodeError:
        return True, False
    if not isinstance(attributes, dict) or set(attributes).difference({"hasFixedLayout"}):
        return True, False

    has_fixed_layout = attributes.get("hasFixedLayout", True)
    if not isinstance(has_fixed_layout, bool):
        return True, False
    return has_fixed_layout, True
