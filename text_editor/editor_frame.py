"""平文入力補助エディタの画面本体です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from converters.wp_txt_converter import convert_wp_txt_to_gutenberg
from text_editor.linter import LintIssue, format_lint_issues, has_errors, lint_prewp_txt
from text_editor.marker_menu import MarkerMenu


class TextEditorFrame(tk.Frame):
    """prewp_txtを作るための簡易エディタです。"""

    def __init__(self, master: tk.Misc, load_file_path: str | Path | None = None) -> None:
        super().__init__(master)
        self.current_file_path: Path | None = Path(load_file_path) if load_file_path else None
        self.pack(fill="both", expand=True)
        self._create_widgets()
        self._create_menu()
        if self.current_file_path:
            self.open_file(self.current_file_path)

    def _create_widgets(self) -> None:
        self.text_area = tk.Text(self, wrap="word", undo=True)
        scrollbar = tk.Scrollbar(self, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=scrollbar.set)
        self.text_area.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        MarkerMenu(self.text_area)

    def _create_menu(self) -> None:
        root: tk.Tk | tk.Toplevel = self.winfo_toplevel()
        menu_bar = tk.Menu(root)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="開く", command=self.ask_open_file)
        file_menu.add_command(label="保存", command=self.save)
        file_menu.add_command(label="名前を付けて保存", command=self.save_as)
        file_menu.add_command(label=".prewp_txtとして保存", command=self.save_as_prewp_txt)
        file_menu.add_command(label="WordPress HTMLへ変換して保存", command=self.convert_to_wordpress_html)
        file_menu.add_separator()
        file_menu.add_command(label="閉じる", command=root.destroy)
        menu_bar.add_cascade(label="ファイル", menu=file_menu)
        root.configure(menu=menu_bar)

    def ask_open_file(self) -> None:
        """開くファイルを選択します。"""
        load_file_path: str = filedialog.askopenfilename(
            title="開くファイルを選んでください",
            filetypes=[
                ("テキスト", "*.txt *.prewp_txt *.wp_txt *.wptxt"),
                ("すべてのファイル", "*.*"),
            ],
        )
        if load_file_path:
            self.open_file(load_file_path)

    def open_file(self, load_file_path: str | Path) -> None:
        """ファイルを読み込んでエディタに表示します。"""
        self.current_file_path = Path(load_file_path)
        load_file: str = self.current_file_path.read_text(encoding="utf-8-sig")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", load_file)
        self.winfo_toplevel().title(f"text_editor - {self.current_file_path}")

    def save(self) -> bool:
        """現在のファイルへ保存します。"""
        if self.current_file_path is None:
            return self.save_as_prewp_txt()
        return self._save_to_path(self.current_file_path)

    def save_as(self) -> bool:
        """名前を付けて保存します。"""
        save_file_path: str = filedialog.asksaveasfilename(
            title="保存先を選んでください",
            defaultextension=".prewp_txt",
            filetypes=[
                ("prewp_txt", "*.prewp_txt"),
                ("WP-TXT", "*.wp_txt *.wptxt"),
                ("テキスト", "*.txt"),
                ("すべてのファイル", "*.*"),
            ],
        )
        if not save_file_path:
            return False
        return self._save_to_path(Path(save_file_path))

    def save_as_prewp_txt(self) -> bool:
        """拡張子を.prewp_txtにして保存します。"""
        initial_file = "article.prewp_txt"
        initial_dir = None
        if self.current_file_path:
            initial_file: str = f"{self.current_file_path.stem}.prewp_txt"
            initial_dir = str(self.current_file_path.parent)

        save_file_path = filedialog.asksaveasfilename(
            title=".prewp_txtとして保存",
            defaultextension=".prewp_txt",
            initialfile=initial_file,
            initialdir=initial_dir,
            filetypes=[("prewp_txt", "*.prewp_txt"), ("すべてのファイル", "*.*")],
        )
        if not save_file_path:
            return False
        return self._save_to_path(Path(save_file_path).with_suffix(".prewp_txt"))

    def _save_to_path(self, save_file_path: Path) -> bool:
        save_file: str = self.text_area.get("1.0", "end-1c")
        issues: list[LintIssue] = lint_prewp_txt(save_file)
        if issues:
            issue_text = format_lint_issues(issues)
            if has_errors(issues):
                should_save = messagebox.askyesno(
                    "lintエラーがあります",
                    f"{issue_text}\n\nこのまま保存しますか？",
                    parent=self.winfo_toplevel(),
                )
                if not should_save:
                    return False
            else:
                messagebox.showwarning(
                    "lint警告",
                    issue_text,
                    parent=self.winfo_toplevel(),
                )

        save_file_path.parent.mkdir(parents=True, exist_ok=True)
        save_file_path.write_text(save_file, encoding="utf-8")
        self.current_file_path = save_file_path
        self.winfo_toplevel().title(f"text_editor - {save_file_path}")
        messagebox.showinfo("保存完了", f"保存しました。\n\n{save_file_path}", parent=self)
        return True

    def convert_to_wordpress_html(self) -> bool:
        """エディタ上の文字列を保存せず、そのままWordPress HTMLへ変換します。"""
        load_file: str = self.text_area.get("1.0", "end-1c")
        issues: list[LintIssue] = lint_prewp_txt(load_file)
        if issues:
            issue_text: str = format_lint_issues(issues)
            if has_errors(issues):
                should_convert = messagebox.askyesno(
                    "lintエラーがあります",
                    f"{issue_text}\n\nこのまま変換しますか？",
                    parent=self.winfo_toplevel(),
                )
                if not should_convert:
                    return False
            else:
                messagebox.showwarning("lint警告", issue_text, parent=self.winfo_toplevel())

        default_save_file_path: Path = self._create_default_wordpress_save_file_path()
        save_file_path: str = filedialog.asksaveasfilename(
            title="WordPress HTMLの保存先を選んでください",
            defaultextension=".wp_html",
            initialfile=default_save_file_path.name,
            initialdir=str(default_save_file_path.parent),
            filetypes=[
                ("WordPress HTML", "*.wp_html"),
                ("HTML", "*.html"),
                ("すべてのファイル", "*.*"),
            ],
        )
        if not save_file_path:
            return False

        try:
            save_file: str = convert_wp_txt_to_gutenberg(load_file)
        except (ValueError, TypeError) as error:
            messagebox.showerror("変換エラー", str(error), parent=self.winfo_toplevel())
            return False

        Path(save_file_path).write_text(save_file, encoding="utf-8")
        messagebox.showinfo("変換完了", f"変換しました。\n\n{save_file_path}", parent=self)
        return True

    def _create_default_wordpress_save_file_path(self) -> Path:
        if self.current_file_path:
            save_file_name: str = f"{self.current_file_path.stem}_wordpress.wp_html"
            return self.current_file_path.with_name(save_file_name)
        return Path.cwd() / "article_wordpress.wp_html"
