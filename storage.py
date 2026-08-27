"""ファイルの読み込みと保存を担当するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from pathlib import Path


def read_load_file(load_file_path: str | Path) -> str:
    """load_file_pathから変換元ファイルを読み込みます。"""
    load_file_path = Path(load_file_path)

    if not load_file_path.exists():
        raise FileNotFoundError(f"読み込みファイルが見つかりません: {load_file_path}")

    return load_file_path.read_text(encoding="utf-8-sig")


def write_save_file(save_file_path: str | Path, save_file: str) -> None:
    """save_file_pathへ変換後ファイルを保存します。"""
    save_file_path = Path(save_file_path)
    save_file_path.parent.mkdir(parents=True, exist_ok=True)
    save_file_path.write_text(save_file, encoding="utf-8")
