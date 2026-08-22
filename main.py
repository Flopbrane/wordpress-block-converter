"""メインの駆動ファイルです"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################

import argparse
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

from converters.html_converter import convert_html_to_gutenberg
from converters.markdown_converter import convert_markdown_to_gutenberg
from converters.text_converter import convert_text_to_gutenberg
from dictionaries.html_dict import HTML_EXTENSIONS
from dictionaries.markdown_dict import MARKDOWN_EXTENSIONS
from dictionaries.text_dict import TEXT_EXTENSIONS

SUPPORTED_FILE_TYPES: list[tuple[str, str]] = [
    ("対応ファイル", "*.txt *.md *.markdown *.html *.htm"),
    ("テキスト", "*.txt"),
    ("Markdown", "*.md *.markdown"),
    ("HTML", "*.html *.htm"),
    ("すべてのファイル", "*.*"),
]


def convert_file(load_file_path: str | Path, save_file_path: str | Path) -> None:
    """ファイルの拡張子に応じて、WordPress Gutenberg向けHTMLへ変換します。"""
    load_file_path = Path(load_file_path)
    save_file_path = Path(save_file_path)

    if not load_file_path.exists():
        raise FileNotFoundError(f"読み込みファイルが見つかりません: {load_file_path}")

    load_file: str = load_file_path.read_text(encoding="utf-8-sig")
    converter: Callable[..., str] = _select_converter(load_file_path.suffix.lower())
    save_file: str = converter(load_file)

    save_file_path.parent.mkdir(parents=True, exist_ok=True)
    save_file_path.write_text(save_file, encoding="utf-8")


def _select_converter(file_extension: str) -> Callable[..., str]:
    if file_extension in TEXT_EXTENSIONS:
        return convert_text_to_gutenberg
    if file_extension in MARKDOWN_EXTENSIONS:
        return convert_markdown_to_gutenberg
    if file_extension in HTML_EXTENSIONS:
        return convert_html_to_gutenberg

    supported_extensions: list[str] = sorted(
        TEXT_EXTENSIONS |
        MARKDOWN_EXTENSIONS |
        HTML_EXTENSIONS
        )
    raise ValueError(
        "対応していないファイル形式です。"
        f"対応拡張子: {', '.join(supported_extensions)}"
    )


def main() -> None:
    """コマンドライン引数またはGUIからWordPress Gutenberg向けHTMLへ変換します。"""
    parser = argparse.ArgumentParser(
        description="平文、Markdown、HTMLをWordPress Gutenberg向けHTMLへ変換します。"
    )
    parser.add_argument("load_file_path", nargs="?", help="変換したいファイルのパス")
    parser.add_argument("save_file_path", nargs="?", help="変換後HTMLを保存するパス")
    parser.add_argument("--gui", action="store_true", help="ファイル選択画面で変換します")
    args: argparse.Namespace = parser.parse_args()

    if args.gui or not args.load_file_path or not args.save_file_path:
        run_gui()
        return

    convert_file(args.load_file_path, args.save_file_path)
    print(f"変換が完了しました: {args.save_file_path}")


def run_gui() -> None:
    """ファイル選択画面からWordPress Gutenberg向けHTMLへ変換します。"""
    root = tk.Tk()
    root.withdraw()

    load_file_path: str = filedialog.askopenfilename(
        title="変換したいファイルを選んでください",
        filetypes=SUPPORTED_FILE_TYPES,
    )
    if not load_file_path:
        messagebox.showinfo("キャンセル", "変換をキャンセルしました。")
        return

    default_save_file_path: Path = _create_default_save_file_path(load_file_path)
    save_file_path: str = filedialog.asksaveasfilename(
        title="変換後HTMLの保存先を選んでください",
        defaultextension=".html",
        initialfile=default_save_file_path.name,
        initialdir=str(default_save_file_path.parent),
        filetypes=[("HTML", "*.html"), ("すべてのファイル", "*.*")],
    )
    if not save_file_path:
        messagebox.showinfo("キャンセル", "保存先が選ばれなかったため、変換をキャンセルしました。")
        return

    try:
        convert_file(load_file_path, save_file_path)
    except (ValueError, TypeError, PermissionError) as error:
        messagebox.showerror("変換エラー", str(error))
        return

    messagebox.showinfo("変換完了", f"変換が完了しました。\n\n{save_file_path}")


def _create_default_save_file_path(load_file_path: str | Path) -> Path:
    load_file_path = Path(load_file_path)
    return load_file_path.with_name(f"{load_file_path.stem}_wordpress.html")


if __name__ == "__main__":
    main()
