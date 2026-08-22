import re
from html import unescape

from blocks.inline import format_inline_text


ROW_PATTERN = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)
CELL_PATTERN = re.compile(r"<(td|th)\b[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
TAG_PATTERN = re.compile(r"<[^>]+>")


def create_table_block(table_html: str) -> str:
    """単純なHTML表をWordPress Gutenbergのtableブロックに変換します。"""
    rows = _extract_rows(table_html)

    if not rows:
        return f"<!-- wp:html -->\n{table_html.strip()}\n<!-- /wp:html -->"

    return _create_table_block_from_row_data(rows)


def create_table_block_from_rows(headers: list[str], rows: list[list[str]]) -> str:
    """Markdown表の行データをWordPress Gutenbergのtableブロックに変換します。"""
    table_rows = []

    if headers:
        table_rows.append([{"tag": "th", "text": header.strip()} for header in headers])

    for row in rows:
        table_rows.append([{"tag": "td", "text": cell.strip()} for cell in row])

    if not table_rows:
        return ""

    return _create_table_block_from_row_data(table_rows)


def _create_table_block_from_row_data(rows: list[list[dict[str, str]]]) -> str:
    header_rows = []
    body_rows = rows

    if rows and all(cell["tag"] == "th" for cell in rows[0]):
        header_rows = [rows[0]]
        body_rows = rows[1:]

    header_html = ""
    if header_rows:
        header_html = "<thead>\n" + "\n".join(_create_row_html(row) for row in header_rows) + "\n</thead>\n"

    body_html = "\n".join(_create_row_html(row) for row in body_rows)
    return (
        "<!-- wp:table -->\n"
        "<figure class=\"wp-block-table\"><table>\n"
        f"{header_html}<tbody>\n"
        f"{body_html}\n"
        "</tbody></table></figure>\n"
        "<!-- /wp:table -->"
    )


def _extract_rows(table_html: str) -> list[list[dict[str, str]]]:
    rows = []

    for row_match in ROW_PATTERN.finditer(table_html):
        cells = []
        for cell_match in CELL_PATTERN.finditer(row_match.group(1)):
            cell_text = TAG_PATTERN.sub("", cell_match.group(2))
            cells.append({
                "tag": cell_match.group(1).lower(),
                "text": unescape(cell_text).strip(),
            })

        if cells:
            rows.append(cells)

    return rows


def _create_row_html(row: list[dict[str, str]]) -> str:
    cells = "".join(
        f"<{cell['tag']}>{format_inline_text(cell['text'])}</{cell['tag']}>"
        for cell in row
    )
    return f"<tr>{cells}</tr>"
