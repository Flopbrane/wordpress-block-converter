"""将来の文書ファイル変換用コンバータです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from pathlib import Path

DOCUMENT_EXTENSIONS: set[str] = {".rtf", ".doc", ".docx", ".pdf"}


def convert_rtf_to_gutenberg(load_file: str) -> str:
    """将来、RTFをWordPress Gutenberg向けHTMLへ変換するための受け皿です。"""
    raise NotImplementedError("RTF変換は今後追加予定です。")


def convert_doc_to_gutenberg(load_file_path: str | Path) -> str:
    """将来、doc/docxをWordPress Gutenberg向けHTMLへ変換するための受け皿です。"""
    raise NotImplementedError("Word文書変換は今後追加予定です。")


def convert_pdf_to_gutenberg(load_file_path: str | Path) -> str:
    """将来、PDFをWordPress Gutenberg向けHTMLへ変換するための受け皿です。"""
    raise NotImplementedError("PDF変換は今後追加予定です。")
