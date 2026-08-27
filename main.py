"""メインの駆動ファイルです"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################

import argparse
from pathlib import Path

from converters.hi_security_filter import apply_hi_security_filter
from dictionaries.hi_security_dict import (
    CONVERSION_MODES,
    HI_SECURITY_MODE,
    NORMAL_MODE,
)
from file_checker import select_converter
from gui_maker import run_gui
from storage import read_load_file, write_save_file


def convert_file(
    load_file_path: str | Path,
    save_file_path: str | Path,
    mode: str = NORMAL_MODE,
) -> None:
    """ファイルの拡張子に応じて、WordPress Gutenberg向けHTMLへ変換します。"""
    load_file_path = Path(load_file_path)
    save_file_path = Path(save_file_path)

    if mode not in CONVERSION_MODES:
        raise ValueError(f"対応していない変換モードです: {mode}")

    load_file: str = read_load_file(load_file_path)
    converter = select_converter(load_file_path)
    save_file: str = converter(load_file)
    if mode == HI_SECURITY_MODE:
        save_file = apply_hi_security_filter(save_file)

    write_save_file(save_file_path, save_file)


def main() -> None:
    """コマンドライン引数またはGUIからWordPress Gutenberg向けHTMLへ変換します。"""
    parser = argparse.ArgumentParser(
        description="平文、Markdown、HTMLをWordPress Gutenberg向けHTMLへ変換します。"
    )
    parser.add_argument("load_file_path", nargs="?", help="変換したいファイルのパス")
    parser.add_argument("save_file_path", nargs="?", help="変換後HTMLを保存するパス")
    parser.add_argument(
        "--mode",
        choices=CONVERSION_MODES,
        default=NORMAL_MODE,
        help="変換モードを選びます",
    )
    parser.add_argument("--gui", action="store_true", help="ファイル選択画面で変換します")
    args: argparse.Namespace = parser.parse_args()

    if args.gui or not args.load_file_path or not args.save_file_path:
        run_gui(convert_file)
        return

    convert_file(args.load_file_path, args.save_file_path, mode=args.mode)
    print(f"変換が完了しました: {args.save_file_path}")


if __name__ == "__main__":
    main()
