"""MarkdownをWordPress Gutenberg向けHTMLへ変換します。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal, cast

from blocks.paragraph import create_paragraph_block
from converters.markdown_layout_converter import convert_markdown_layout_to_gutenberg
from dictionaries.html_dict import DIRECT_URL_RULES, EMBED_PROVIDER_RULES
from dictionaries.markdown_dict import (
    MARKDOWN_CODE_RULE,
    MARKDOWN_EMBED_RULE,
    MARKDOWN_HEADING_RULE,
    MARKDOWN_IMAGE_RULE,
    MARKDOWN_LIST_RULES,
    MARKDOWN_QUOTE_RULE,
    MARKDOWN_SEPARATOR_RULE,
    MARKDOWN_SHORTCODE_RULE,
    MARKDOWN_SPACER_RULE,
    MARKDOWN_TABLE_RULE,
)

MarkdownBlockType = Literal[
    "paragraph",
    "heading",
    "code",
    "list",
    "quote",
    "table",
    "spacer",
    "separator",
    "shortcode",
    "image",
    "embed",
    "direct_url",
    "layout",
]


@dataclass(frozen=True)
class MarkdownBlock:
    """Markdownを行単位で解析した中間ブロックです。"""

    block_type: MarkdownBlockType
    lines: list[str]
    text: str = ""
    level: int = 0
    ordered: bool = False
    layout_name: str = ""


def convert_markdown_to_gutenberg(load_file: str) -> str:
    """MarkdownをWordPress Gutenberg向けHTMLに変換します。"""
    return render_markdown_blocks_to_wordpress(parse_markdown_blocks(load_file))


def parse_markdown_blocks(load_file: str) -> list[MarkdownBlock]:
    """MarkdownをWordPress変換前のブロック構造へ分解します。"""
    blocks: list[MarkdownBlock] = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_ordered = False
    quote_lines: list[str] = []
    table_lines: list[str] = []
    code_lines: list[str] = []
    layout_lines: list[str] = []
    layout_name = ""
    in_code_block = False
    in_layout_block = False
    code_fence = str(MARKDOWN_CODE_RULE["fence"])

    for line in load_file.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith(":::") and not in_code_block:
            if in_layout_block:
                blocks.append(MarkdownBlock("layout", layout_lines[:], layout_name=layout_name))
                layout_lines = []
                layout_name = ""
                in_layout_block = False
            else:
                _flush_pending_blocks(
                    blocks,
                    paragraph_lines,
                    list_items,
                    list_ordered,
                    quote_lines,
                    table_lines,
                )
                list_ordered = False
                layout_name = stripped_line.removeprefix(":::").strip()
                in_layout_block = bool(layout_name)
            continue

        if in_layout_block:
            layout_lines.append(line)
            continue

        if stripped_line.startswith(code_fence):
            if in_code_block:
                blocks.append(MarkdownBlock("code", code_lines[:]))
                code_lines = []
                in_code_block = False
            else:
                _flush_pending_blocks(
                    blocks,
                    paragraph_lines,
                    list_items,
                    list_ordered,
                    quote_lines,
                    table_lines,
                )
                list_ordered = False
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        single_code_block = _match_single_code_block(stripped_line)
        if single_code_block is not None:
            _flush_pending_blocks(
                blocks,
                paragraph_lines,
                list_items,
                list_ordered,
                quote_lines,
                table_lines,
            )
            list_ordered = False
            blocks.append(MarkdownBlock("code", [single_code_block]))
            continue

        if not stripped_line:
            _flush_pending_blocks(
                blocks,
                paragraph_lines,
                list_items,
                list_ordered,
                quote_lines,
                table_lines,
            )
            list_ordered = False
            continue

        if _is_table_row(stripped_line):
            _flush_paragraph_blocks(blocks, paragraph_lines)
            _flush_list_blocks(blocks, list_items, list_ordered)
            list_ordered = False
            _flush_quote_blocks(blocks, quote_lines)
            table_lines.append(stripped_line)
            continue

        block = _create_standalone_block(stripped_line)
        if block is not None:
            _flush_pending_blocks(
                blocks,
                paragraph_lines,
                list_items,
                list_ordered,
                quote_lines,
                table_lines,
            )
            list_ordered = False
            blocks.append(block)
            continue

        quote_text = _match_quote(line)
        if quote_text is not None:
            _flush_paragraph_blocks(blocks, paragraph_lines)
            _flush_list_blocks(blocks, list_items, list_ordered)
            list_ordered = False
            _flush_table_blocks(blocks, table_lines, paragraph_lines)
            _flush_paragraph_blocks(blocks, paragraph_lines)
            quote_lines.append(quote_text)
            continue

        list_match = _match_list_item(line)
        if list_match is not None:
            item_text, current_ordered = list_match
            _flush_paragraph_blocks(blocks, paragraph_lines)
            _flush_quote_blocks(blocks, quote_lines)
            _flush_table_blocks(blocks, table_lines, paragraph_lines)
            _flush_paragraph_blocks(blocks, paragraph_lines)
            if list_items and list_ordered != current_ordered:
                _flush_list_blocks(blocks, list_items, list_ordered)

            list_ordered = current_ordered
            list_items.append(item_text)
            continue

        _flush_list_blocks(blocks, list_items, list_ordered)
        list_ordered = False
        _flush_quote_blocks(blocks, quote_lines)
        _flush_table_blocks(blocks, table_lines, paragraph_lines)
        paragraph_lines.append(stripped_line)

    if in_code_block:
        blocks.append(MarkdownBlock("code", code_lines[:]))

    if in_layout_block:
        blocks.append(MarkdownBlock("layout", layout_lines[:], layout_name=layout_name))

    _flush_pending_blocks(
        blocks,
        paragraph_lines,
        list_items,
        list_ordered,
        quote_lines,
        table_lines,
    )
    return blocks


def render_markdown_blocks_to_wordpress(markdown_blocks: list[MarkdownBlock]) -> str:
    """Markdown中間ブロックをWordPress Gutenberg HTMLへ描画します。"""
    rendered_blocks = [_render_markdown_block(block) for block in markdown_blocks]
    save_file = "\n\n".join(block for block in rendered_blocks if block)
    return _normalize_rendered_markdown_html(save_file)


def _normalize_rendered_markdown_html(save_file: str) -> str:
    """変換後HTMLの隣接paragraphを、指定の完全一致置換で整えます。"""
    save_file = save_file.replace(
        "<!-- /wp:paragraph -->\n\n<!-- wp:paragraph -->",
        "",
    )
    save_file = save_file.replace("</p>\n\n<p>", "<br><br>\n")
    return save_file.replace("</p>\n<p>", "<br><br>\n")


# pylint: disable-next=too-many-return-statements
def _render_markdown_block(block: MarkdownBlock) -> str:
    if block.block_type == "paragraph":
        return create_paragraph_block(
            _build_paragraph_text(block.lines),
            line_break_html="<br><br>",
            convert_inline_code=True,
        )
    if block.block_type == "heading":
        heading_converter = cast(Callable[..., str], MARKDOWN_HEADING_RULE["converter"])
        return heading_converter(block.text, block.level, convert_inline_code=True)
    if block.block_type == "code":
        code_converter = cast(Callable[[str], str], MARKDOWN_CODE_RULE["converter"])
        return code_converter("\n".join(block.lines))
    if block.block_type == "list":
        return _render_list_block(block.lines, block.ordered)
    if block.block_type == "quote":
        quote_converter = cast(Callable[..., str], MARKDOWN_QUOTE_RULE["converter"])
        return quote_converter(" ".join(block.lines), convert_inline_code=True)
    if block.block_type == "table":
        return _render_table_block(block.lines)
    if block.block_type == "spacer":
        spacer_converter = cast(Callable[[int], str], MARKDOWN_SPACER_RULE["converter"])
        return spacer_converter(int(block.text))
    if block.block_type == "separator":
        separator_converter = cast(Callable[[], str], MARKDOWN_SEPARATOR_RULE["converter"])
        return separator_converter()
    if block.block_type == "shortcode":
        shortcode_converter = cast(Callable[[str], str], MARKDOWN_SHORTCODE_RULE["converter"])
        return shortcode_converter(block.text)
    if block.block_type == "image":
        image_converter = cast(Callable[[str, str], str], MARKDOWN_IMAGE_RULE["converter"])
        return image_converter(block.lines[0], block.text)
    if block.block_type == "embed":
        return _render_embed_block(block.text)
    if block.block_type == "direct_url":
        return _create_direct_url_block(block.text) or ""
    if block.block_type == "layout":
        return convert_markdown_layout_to_gutenberg(block.layout_name, block.lines)
    return ""


def _render_embed_block(url: str) -> str:
    provider_info = _find_embed_provider(url)
    if provider_info is None:
        return ""

    embed_converter = cast(Callable[..., str], MARKDOWN_EMBED_RULE["converter"])
    return embed_converter(
        url,
        provider_info["providerNameSlug"],
        embed_type=provider_info["type"],
        responsive=provider_info["responsive"],
        aspect=provider_info["aspect"],
    )


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
def _flush_pending_blocks(
    blocks: list[MarkdownBlock],
    paragraph_lines: list[str],
    list_items: list[str],
    list_ordered: bool,
    quote_lines: list[str],
    table_lines: list[str],
) -> None:
    _flush_table_blocks(blocks, table_lines, paragraph_lines)
    _flush_paragraph_blocks(blocks, paragraph_lines)
    _flush_list_blocks(blocks, list_items, list_ordered)
    _flush_quote_blocks(blocks, quote_lines)


def _flush_paragraph_blocks(blocks: list[MarkdownBlock], paragraph_lines: list[str]) -> None:
    if paragraph_lines:
        blocks.append(MarkdownBlock("paragraph", paragraph_lines[:]))
        paragraph_lines.clear()


def _flush_list_blocks(
    blocks: list[MarkdownBlock],
    list_items: list[str],
    ordered: bool,
) -> None:
    if list_items:
        blocks.append(MarkdownBlock("list", list_items[:], ordered=ordered))
        list_items.clear()


def _flush_quote_blocks(blocks: list[MarkdownBlock], quote_lines: list[str]) -> None:
    if quote_lines:
        blocks.append(MarkdownBlock("quote", quote_lines[:]))
        quote_lines.clear()


def _flush_table_blocks(
    blocks: list[MarkdownBlock],
    table_lines: list[str],
    paragraph_lines: list[str],
) -> None:
    if not table_lines:
        return

    separator_pattern = cast(re.Pattern[str], MARKDOWN_TABLE_RULE["separator_pattern"])
    if len(table_lines) < 2 or not separator_pattern.match(table_lines[1]):
        paragraph_lines.extend(table_lines)
        table_lines.clear()
        return

    blocks.append(MarkdownBlock("table", table_lines[:]))
    table_lines.clear()


def _create_standalone_block(stripped_line: str) -> MarkdownBlock | None:
    for block_factory in (
        _create_heading_block,
        _create_spacer_block,
        _create_separator_block,
        _create_shortcode_block,
        _create_image_block,
        _create_embed_block,
        _create_direct_url_markdown_block,
    ):
        block = block_factory(stripped_line)
        if block is not None:
            return block
    return None


def _create_heading_block(stripped_line: str) -> MarkdownBlock | None:
    heading_pattern = cast(re.Pattern[str], MARKDOWN_HEADING_RULE["pattern"])
    heading_match = heading_pattern.match(stripped_line)
    if heading_match is None:
        return None

    return MarkdownBlock(
        "heading",
        [],
        text=heading_match.group(2),
        level=len(heading_match.group(1)),
    )


def _create_spacer_block(stripped_line: str) -> MarkdownBlock | None:
    spacer_pattern = cast(re.Pattern[str], MARKDOWN_SPACER_RULE["pattern"])
    spacer_match = spacer_pattern.match(stripped_line)
    if spacer_match is None:
        return None

    default_height = cast(int, MARKDOWN_SPACER_RULE["default_height"])
    return MarkdownBlock("spacer", [], text=str(int(spacer_match.group(1) or default_height)))


def _create_separator_block(stripped_line: str) -> MarkdownBlock | None:
    if _matches_rule(stripped_line, MARKDOWN_SEPARATOR_RULE):
        return MarkdownBlock("separator", [], text=stripped_line)
    return None


def _create_shortcode_block(stripped_line: str) -> MarkdownBlock | None:
    if _matches_rule(stripped_line, MARKDOWN_SHORTCODE_RULE):
        return MarkdownBlock("shortcode", [], text=stripped_line)
    return None


def _create_image_block(stripped_line: str) -> MarkdownBlock | None:
    image_pattern = cast(re.Pattern[str], MARKDOWN_IMAGE_RULE["pattern"])
    image_match = image_pattern.match(stripped_line)
    if image_match is None:
        return None

    return MarkdownBlock("image", [image_match.group(2)], text=image_match.group(1))


def _create_embed_block(stripped_line: str) -> MarkdownBlock | None:
    embed_pattern = cast(re.Pattern[str], MARKDOWN_EMBED_RULE["pattern"])
    if _find_embed_provider(stripped_line) and embed_pattern.match(stripped_line):
        return MarkdownBlock("embed", [], text=stripped_line)
    return None


def _create_direct_url_markdown_block(stripped_line: str) -> MarkdownBlock | None:
    embed_pattern = cast(re.Pattern[str], MARKDOWN_EMBED_RULE["pattern"])
    if _create_direct_url_block(stripped_line) and embed_pattern.match(stripped_line):
        return MarkdownBlock("direct_url", [], text=stripped_line)
    return None


def _matches_rule(stripped_line: str, rule: Mapping[str, object]) -> bool:
    pattern = cast(re.Pattern[str], rule["pattern"])
    return bool(pattern.match(stripped_line))


def _match_single_code_block(stripped_line: str) -> str | None:
    single_code_pattern = cast(re.Pattern[str], MARKDOWN_CODE_RULE["single_line_pattern"])
    single_code_match = single_code_pattern.match(stripped_line)
    if single_code_match is None:
        return None

    return single_code_match.group(1)


def _match_quote(line: str) -> str | None:
    quote_pattern = cast(re.Pattern[str], MARKDOWN_QUOTE_RULE["pattern"])
    quote_match = quote_pattern.match(line)
    if quote_match is None:
        return None

    return quote_match.group(1).strip()


def _match_list_item(line: str) -> tuple[str, bool] | None:
    unordered_rule = MARKDOWN_LIST_RULES["unordered"]
    ordered_rule = MARKDOWN_LIST_RULES["ordered"]
    unordered_pattern = cast(re.Pattern[str], unordered_rule["pattern"])
    ordered_pattern = cast(re.Pattern[str], ordered_rule["pattern"])
    unordered_match = unordered_pattern.match(line)
    ordered_match = ordered_pattern.match(line)

    if ordered_match is not None:
        return ordered_match.group(1), True
    if unordered_match is not None:
        return unordered_match.group(1), False
    return None


def _is_table_row(stripped_line: str) -> bool:
    table_row_pattern = cast(re.Pattern[str], MARKDOWN_TABLE_RULE["row_pattern"])
    return bool(table_row_pattern.match(stripped_line))


def _render_list_block(list_items: list[str], ordered: bool) -> str:
    list_rule: dict[str, str | re.Pattern[str] | Callable[..., object] | bool] = (
        MARKDOWN_LIST_RULES["ordered"] if ordered else MARKDOWN_LIST_RULES["unordered"]
    )
    list_converter = cast(Callable[..., str], list_rule["converter"])
    return list_converter(
        list_items,
        ordered=cast(bool, list_rule["ordered"]),
        use_html_block=cast(bool, list_rule["use_html_block"]),
        convert_inline_code=True,
    )


def _render_table_block(table_lines: list[str]) -> str:
    headers = _split_table_row(table_lines[0])
    rows = [_split_table_row(row) for row in table_lines[2:]]
    table_converter = cast(Callable[..., str], MARKDOWN_TABLE_RULE["converter"])
    return table_converter(headers, rows, convert_inline_code=True)


def _build_paragraph_text(paragraph_lines: list[str]) -> str:
    paragraph_groups: list[list[str]] = [[]]

    for line in paragraph_lines:
        if line:
            paragraph_groups[-1].append(line)
        elif paragraph_groups[-1]:
            paragraph_groups.append([])

    joined_groups = [
        "\n".join(paragraph_group)
        for paragraph_group in paragraph_groups
        if paragraph_group
    ]
    return "\n\n".join(joined_groups)


def _split_table_row(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip().strip("|").split("|")]


def _find_embed_provider(url: str) -> dict[str, str | bool | None] | None:
    lower_url = url.lower()

    for compare_text, provider_info in EMBED_PROVIDER_RULES.items():
        if compare_text in lower_url:
            return provider_info

    return None


def _create_direct_url_block(url: str) -> str | None:
    lower_url = url.lower().split("?", 1)[0].split("#", 1)[0]

    for rule in DIRECT_URL_RULES.values():
        extensions = cast(list[str], rule["extensions"])
        if any(lower_url.endswith(file_extension) for file_extension in extensions):
            direct_url_converter = cast(Callable[[str], str], rule["converter"])
            return direct_url_converter(url)

    return None
