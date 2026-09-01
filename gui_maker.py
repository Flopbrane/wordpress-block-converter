"""GUI表示を担当するモジュールです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import os
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox

from dictionaries.hi_security_dict import HIGH_SECURITY_MODE, MIDDLE_MODE, NORMAL_MODE
from file_checker import SUPPORTED_FILE_TYPES


def run_gui(convert_file: Callable[[str | Path, str | Path, str], None]) -> None:
    """ファイル選択画面からWordPress Gutenberg向けHTMLへ変換します。"""
    root = tk.Tk()
    root.withdraw()

    mode: str = _select_mode_with_gui(root)
    if not mode:
        messagebox.showinfo("キャンセル", "変換をキャンセルしました。")
        return

    load_file_path: str = filedialog.askopenfilename(
        title="変換したいファイルを選んでください",
        filetypes=SUPPORTED_FILE_TYPES,
    )
    if not load_file_path:
        messagebox.showinfo("キャンセル", "変換をキャンセルしました。")
        return

    default_save_file_path: Path = create_default_save_file_path(load_file_path)
    save_file_path: str = filedialog.asksaveasfilename(
        title="変換後HTMLの保存先を選んでください",
        defaultextension=".wp_html",
        initialfile=default_save_file_path.name,
        initialdir=str(default_save_file_path.parent),
        filetypes=[("WordPress HTML", "*.wp_html"), ("HTML", "*.html"), ("すべてのファイル", "*.*")],
    )
    if not save_file_path:
        messagebox.showinfo("キャンセル", "保存先が選ばれなかったため、変換をキャンセルしました。")
        return

    try:
        convert_file(load_file_path, save_file_path, mode)
    except (ValueError, TypeError, PermissionError) as error:
        messagebox.showerror("変換エラー", str(error))
        return

    show_conversion_complete_dialog(root, Path(save_file_path))


def create_default_save_file_path(load_file_path: str | Path) -> Path:
    """変換後HTMLの標準保存先を作ります。"""
    load_file_path = Path(load_file_path)
    return load_file_path.with_name(f"{load_file_path.stem}_wordpress.wp_html")


def show_conversion_complete_dialog(root: tk.Tk, save_file_path: str | Path) -> None:
    """変換完了後、OKまたは保存フォルダを開く操作を選べる画面を表示します。"""
    save_file_path = Path(save_file_path)
    dialog = tk.Toplevel(root)
    dialog.title("変換完了")
    dialog.resizable(False, False)
    dialog.grab_set()

    tk.Label(
        dialog,
        text=f"変換が完了しました。\n\n{save_file_path}",
        justify="left",
        anchor="w",
    ).pack(padx=20, pady=(16, 12), fill="x")

    button_frame = tk.Frame(dialog)
    button_frame.pack(padx=20, pady=(0, 16), anchor="e")

    def open_save_folder() -> None:
        try:
            os.startfile(save_file_path.parent)
        except OSError as error:
            messagebox.showerror("フォルダを開けません", str(error), parent=dialog)

    tk.Button(
        button_frame,
        text="保存したフォルダを開く",
        command=open_save_folder,
    ).pack(side="left", padx=(0, 8))
    tk.Button(button_frame, text="OK", command=dialog.destroy).pack(side="left")

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    root.wait_window(dialog)


def _select_mode_with_gui(root: tk.Tk) -> str:
    """GUIで変換モードを選びます。"""
    selected_mode = tk.StringVar(value=NORMAL_MODE)
    result: dict[str, str] = {"mode": ""}

    mode_window = tk.Toplevel(root)
    mode_window.title("変換モード")
    mode_window.resizable(False, False)
    mode_window.grab_set()

    tk.Label(mode_window, text="変換モードを選んでください").pack(
        padx=20,
        pady=(16, 8),
        anchor="w",
    )
    tk.Radiobutton(
        mode_window,
        text="Normal",
        variable=selected_mode,
        value=NORMAL_MODE,
    ).pack(padx=24, anchor="w")
    tk.Radiobutton(
        mode_window,
        text="Middle / 事業所WP向け",
        variable=selected_mode,
        value=MIDDLE_MODE,
    ).pack(padx=24, anchor="w")
    tk.Radiobutton(
        mode_window,
        text="High-Security",
        variable=selected_mode,
        value=HIGH_SECURITY_MODE,
    ).pack(padx=24, anchor="w")

    def decide_mode() -> None:
        result["mode"] = selected_mode.get()
        mode_window.destroy()

    tk.Button(mode_window, text="OK", command=decide_mode).pack(pady=(8, 16))
    mode_window.protocol("WM_DELETE_WINDOW", mode_window.destroy)
    root.wait_window(mode_window)
    return result["mode"]
