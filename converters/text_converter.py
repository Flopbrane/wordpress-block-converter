from blocks.paragraph import create_paragraph_block
from blocks.spacer import create_spacer_block
from dictionaries.text_dict import (
    TEXT_LINE_BREAK_HTML,
    TEXT_PARAGRAPH_SEPARATOR_PATTERN,
    TEXT_PARAGRAPH_SPACER_HEIGHT,
)


def convert_text_to_gutenberg(load_file: str) -> str:
    """平文をWordPress Gutenberg向けHTMLに変換します。"""
    normalized_load_file = load_file.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [
        paragraph.strip()
        for paragraph in TEXT_PARAGRAPH_SEPARATOR_PATTERN.split(normalized_load_file)
    ]
    blocks = []
    clean_paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip()]

    for paragraph_index, paragraph in enumerate(clean_paragraphs):
        if paragraph_index > 0:
            blocks.append(create_spacer_block(TEXT_PARAGRAPH_SPACER_HEIGHT))

        blocks.append(create_paragraph_block(paragraph, line_break_html=TEXT_LINE_BREAK_HTML))

    return "\n\n".join(blocks)
