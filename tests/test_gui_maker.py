"""GUI補助関数のテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from pathlib import Path

from gui_maker import create_default_save_file_path


def test_create_default_save_file_path_uses_wp_html_extension() -> None:
    """標準保存先の拡張子が.wp_htmlになるテストです。"""
    load_file_path = Path("sample.md")

    save_file_path = create_default_save_file_path(load_file_path)

    assert save_file_path.name == "sample_wordpress.wp_html"
