"""Markdown独自レイアウト記法の辞書です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

LAYOUT_DICT: dict[str, str] = {
    "image_text_left": "画像左・文章右",
    "image_text_right": "文章左・画像右",
    "image_row_3_gap": "画像3枚・隙間あり",
    "image_row_3_no_gap": "画像3枚・隙間なし",
    "float_image_left": "画像左回り込み",
    "float_image_right": "画像右回り込み",
}

IMAGE_TEXT_LAYOUTS: set[str] = {"image_text_left", "image_text_right"}
IMAGE_ROW_LAYOUTS: set[str] = {
    "image_row",
    "image_row_2",
    "image_row_3",
    "image_row_3_gap",
    "image_row_3_no_gap",
}
FLOAT_IMAGE_LAYOUTS: set[str] = {"float_image_left", "float_image_right"}
