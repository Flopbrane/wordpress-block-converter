"""平文入力補助エディタの起動処理です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import tkinter as tk
from pathlib import Path

from text_editor.editor_frame import TextEditorFrame


def run_text_editor(load_file_path: str | Path | None = None) -> None:
    """text_editorを起動します。"""
    root = tk.Tk()
    root.title("text_editor")
    root.geometry("900x650")
    TextEditorFrame(root, load_file_path)
    root.mainloop()


if __name__ == "__main__":
    run_text_editor()
