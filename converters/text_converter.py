from blocks.paragraph import create_paragraph_block
from dictionaries.text_dict import TEXT_LINE_BREAK_HTML, TEXT_PARAGRAPH_SEPARATOR


def convert_text_to_gutenberg(load_file: str) -> str:
    """平文をWordPress Gutenberg向けHTMLに変換します。"""
    paragraphs = [paragraph.strip() for paragraph in load_file.split(TEXT_PARAGRAPH_SEPARATOR)]
    blocks = [
        create_paragraph_block(paragraph, line_break_html=TEXT_LINE_BREAK_HTML)
        for paragraph in paragraphs
        if paragraph.strip()
    ]

    return "\n\n".join(blocks)
