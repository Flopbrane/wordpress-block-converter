from blocks.paragraph import create_paragraph_block
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
from dictionaries.html_dict import DIRECT_URL_RULES, EMBED_PROVIDER_RULES


def convert_markdown_to_gutenberg(load_file: str) -> str:
    """MarkdownをWordPress Gutenberg向けHTMLに変換します。"""
    blocks = []
    paragraph_lines = []
    list_items = []
    list_ordered = False
    quote_lines = []
    table_lines = []
    code_lines = []
    in_code_block = False

    for line in load_file.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith(MARKDOWN_CODE_RULE["fence"]):
            if in_code_block:
                blocks.append(MARKDOWN_CODE_RULE["converter"]("\n".join(code_lines)))
                code_lines = []
                in_code_block = False
            else:
                _flush_paragraph(blocks, paragraph_lines)
                paragraph_lines = []
                _flush_list(blocks, list_items, list_ordered)
                list_items = []
                _flush_quote(blocks, quote_lines)
                quote_lines = []
                _flush_table(blocks, table_lines, paragraph_lines)
                table_lines = []
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if not stripped_line:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            continue

        if MARKDOWN_TABLE_RULE["row_pattern"].match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            table_lines.append(stripped_line)
            continue

        heading_match = MARKDOWN_HEADING_RULE["pattern"].match(stripped_line)
        if heading_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            level = len(heading_match.group(1))
            blocks.append(MARKDOWN_HEADING_RULE["converter"](heading_match.group(2), level))
            continue

        spacer_match = MARKDOWN_SPACER_RULE["pattern"].match(stripped_line)
        if spacer_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            height = int(spacer_match.group(1) or MARKDOWN_SPACER_RULE["default_height"])
            blocks.append(MARKDOWN_SPACER_RULE["converter"](height))
            continue

        if MARKDOWN_SEPARATOR_RULE["pattern"].match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            blocks.append(MARKDOWN_SEPARATOR_RULE["converter"]())
            continue

        if MARKDOWN_SHORTCODE_RULE["pattern"].match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            blocks.append(MARKDOWN_SHORTCODE_RULE["converter"](stripped_line))
            continue

        image_match = MARKDOWN_IMAGE_RULE["pattern"].match(stripped_line)
        if image_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            blocks.append(MARKDOWN_IMAGE_RULE["converter"](image_match.group(2), image_match.group(1)))
            continue

        provider_info = _find_embed_provider(stripped_line)
        if provider_info and MARKDOWN_EMBED_RULE["pattern"].match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            blocks.append(
                MARKDOWN_EMBED_RULE["converter"](
                    stripped_line,
                    provider_info["providerNameSlug"],
                    embed_type=provider_info["type"],
                    responsive=provider_info["responsive"],
                    aspect=provider_info["aspect"],
                )
            )
            continue

        direct_url_block = _create_direct_url_block(stripped_line)
        if direct_url_block and MARKDOWN_EMBED_RULE["pattern"].match(stripped_line):
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            blocks.append(direct_url_block)
            continue

        quote_match = MARKDOWN_QUOTE_RULE["pattern"].match(line)
        if quote_match:
            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_list(blocks, list_items, list_ordered)
            list_items = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            quote_lines.append(quote_match.group(1).strip())
            continue

        unordered_rule = MARKDOWN_LIST_RULES["unordered"]
        ordered_rule = MARKDOWN_LIST_RULES["ordered"]
        unordered_match = unordered_rule["pattern"].match(line)
        ordered_match = ordered_rule["pattern"].match(line)
        if unordered_match or ordered_match:
            current_ordered = ordered_match is not None
            item_text = ordered_match.group(1) if ordered_match else unordered_match.group(1)

            _flush_paragraph(blocks, paragraph_lines)
            paragraph_lines = []
            _flush_quote(blocks, quote_lines)
            quote_lines = []
            _flush_table(blocks, table_lines, paragraph_lines)
            table_lines = []
            if list_items and list_ordered != current_ordered:
                _flush_list(blocks, list_items, list_ordered)
                list_items = []

            list_ordered = current_ordered
            list_items.append(item_text)
            continue

        _flush_list(blocks, list_items, list_ordered)
        list_items = []
        _flush_quote(blocks, quote_lines)
        quote_lines = []
        _flush_table(blocks, table_lines, paragraph_lines)
        table_lines = []
        paragraph_lines.append(stripped_line)

    if in_code_block:
        blocks.append(MARKDOWN_CODE_RULE["converter"]("\n".join(code_lines)))

    _flush_table(blocks, table_lines, paragraph_lines)
    _flush_paragraph(blocks, paragraph_lines)
    _flush_list(blocks, list_items, list_ordered)
    _flush_quote(blocks, quote_lines)

    return "\n\n".join(blocks)


def _flush_paragraph(blocks: list[str], paragraph_lines: list[str]) -> None:
    if paragraph_lines:
        blocks.append(create_paragraph_block(" ".join(paragraph_lines)))


def _flush_list(blocks: list[str], list_items: list[str], ordered: bool) -> None:
    if list_items:
        list_rule = MARKDOWN_LIST_RULES["ordered"] if ordered else MARKDOWN_LIST_RULES["unordered"]
        blocks.append(
            list_rule["converter"](
                list_items,
                ordered=list_rule["ordered"],
                use_html_block=list_rule["use_html_block"],
            )
        )


def _flush_quote(blocks: list[str], quote_lines: list[str]) -> None:
    if quote_lines:
        blocks.append(MARKDOWN_QUOTE_RULE["converter"](" ".join(quote_lines)))


def _flush_table(blocks: list[str], table_lines: list[str], paragraph_lines: list[str]) -> None:
    if not table_lines:
        return

    if len(table_lines) < 2 or not MARKDOWN_TABLE_RULE["separator_pattern"].match(table_lines[1]):
        paragraph_lines.extend(table_lines)
        table_lines.clear()
        return

    headers = _split_table_row(table_lines[0])
    rows = [_split_table_row(row) for row in table_lines[2:]]
    blocks.append(MARKDOWN_TABLE_RULE["converter"](headers, rows))
    table_lines.clear()


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
        if any(lower_url.endswith(file_extension) for file_extension in rule["extensions"]):
            return rule["converter"](url)

    return None
