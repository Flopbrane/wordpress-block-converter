# pylint: disable=C0301
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
from typing import cast

from converters.wp_txt_converter import convert_wp_txt_to_gutenberg
from lint import LintIssue as WpHtmlLintIssue
from lint import lint_css, lint_wp_html
from text_editor.linter import LintIssue, format_lint_issues, has_errors, lint_prewp_txt
from text_editor.marker_menu import MarkerMenu

AnyLintIssue = LintIssue | WpHtmlLintIssue


class TextEditorFrame(tk.Frame):
    """prewp_txtを作るための簡易エディタです。"""

    def __init__(self, master: tk.Misc, load_file_path: str | Path | None = None) -> None:
        super().__init__(master)
        self.current_file_path: Path | None = Path(load_file_path) if load_file_path else None
        self._lint_tooltip: tk.Toplevel | None = None
        self._lint_tooltip_after_id: str | None = None
        self.pack(fill="both", expand=True)
        self._create_widgets()
        self._create_menu()
        if self.current_file_path:
            self.open_file(self.current_file_path)

    def _create_widgets(self) -> None:
        self.text_area = tk.Text(self, wrap="word", undo=True)
        self.text_area.tag_configure("lint_error_line", background="#ffe5e5")
        self.text_area.tag_configure("lint_warning_line", background="#fff6cc")
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
        tool_menu = tk.Menu(menu_bar, tearoff=False)
        tool_menu.add_command(label="lintチェック", command=self.run_lint_check)
        menu_bar.add_cascade(label="ツール", menu=tool_menu)
        root.configure(menu=menu_bar)

    def ask_open_file(self) -> None:
        """開くファイルを選択します。"""
        load_file_path: str = filedialog.askopenfilename(
            title="開くファイルを選んでください",
            filetypes=[
                ("編集対象", "*.txt *.prewp_txt *.wp_txt *.wptxt *.wp_html *.html *.htm *.css"),
                ("テキスト", "*.txt *.prewp_txt *.wp_txt *.wptxt"),
                ("WordPress HTML", "*.wp_html *.html *.htm"),
                ("CSS", "*.css"),
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
        self._clear_lint_marks()
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
                ("WordPress HTML", "*.wp_html *.html *.htm"),
                ("CSS", "*.css"),
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
        issues: list[AnyLintIssue] = self._run_lint(save_file)
        if issues:
            issue_text = self._format_lint_issues(issues)
            if self._has_errors(issues):
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
        issues: list[AnyLintIssue] = self._run_lint(load_file)
        if issues:
            issue_text: str = self._format_lint_issues(issues)
            if self._has_errors(issues):
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

    def run_lint_check(self) -> None:
        """現在の内容をlintし、問題行をハイライトします。"""
        load_file: str = self.text_area.get("1.0", "end-1c")
        issues = self._run_lint(load_file)
        if not issues:
            messagebox.showinfo(
                "lint結果",
                "lint結果: 問題は見つかりませんでした。",
                parent=self.winfo_toplevel(),
            )
            return

        messagebox.showwarning(
            "lint結果",
            self._format_lint_issues(issues),
            parent=self.winfo_toplevel(),
        )

    def _run_lint(self, load_file: str) -> list[AnyLintIssue]:
        if self._should_use_css_lint():
            issues = cast(list[AnyLintIssue], lint_css(load_file))
        elif self._should_use_wp_html_lint(load_file):
            issues = cast(list[AnyLintIssue], lint_wp_html(load_file, mode="high-security"))
        else:
            issues = cast(list[AnyLintIssue], lint_prewp_txt(load_file))
        self._mark_lint_issues(issues)
        return issues

    def _should_use_css_lint(self) -> bool:
        return bool(self.current_file_path and self.current_file_path.suffix.lower() == ".css")

    def _should_use_wp_html_lint(self, load_file: str) -> bool:
        if self.current_file_path and self.current_file_path.suffix.lower() in {
            ".html",
            ".htm",
            ".wp_html",
        }:
            return True
        return "<!-- wp:" in load_file

    def _mark_lint_issues(self, issues: list[AnyLintIssue]) -> None:
        self._clear_lint_marks()
        for index, issue in enumerate(issues):
            line_number = self._issue_line_number(issue)
            line_start = f"{line_number}.0"
            line_end = f"{line_number}.end + 1 chars"
            base_tag = "lint_error_line" if self._issue_level(issue) == "error" else "lint_warning_line"
            issue_tag = f"lint_issue_{index}"
            tooltip_text = self._format_single_lint_issue(issue)
            self.text_area.tag_add(base_tag, line_start, line_end)
            self.text_area.tag_add(issue_tag, line_start, line_end)
            self.text_area.tag_bind(
                issue_tag,
                "<Enter>",
                lambda event, text=tooltip_text: self._schedule_lint_tooltip(event, text),
            )
            self.text_area.tag_bind(issue_tag, "<Leave>", self._hide_lint_tooltip)

    def _clear_lint_marks(self) -> None:
        self._hide_lint_tooltip()
        for tag_name in self.text_area.tag_names():
            if tag_name.startswith("lint_issue_") or tag_name in {
                "lint_error_line",
                "lint_warning_line",
            }:
                self.text_area.tag_delete(tag_name)
        self.text_area.tag_configure("lint_error_line", background="#ffe5e5")
        self.text_area.tag_configure("lint_warning_line", background="#fff6cc")

    def _schedule_lint_tooltip(self, event: tk.Event, text: str) -> None:
        self._hide_lint_tooltip()
        self._lint_tooltip_after_id = self.after(
            250,
            lambda: self._show_lint_tooltip(event.x_root, event.y_root, text),
        )

    def _show_lint_tooltip(self, x_root: int, y_root: int, text: str) -> None:
        self._lint_tooltip_after_id = None
        tooltip = tk.Toplevel(self)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x_root + 12}+{y_root + 16}")
        label = tk.Label(
            tooltip,
            text=text,
            justify="left",
            background="#fffbe6",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=5,
            wraplength=520,
        )
        label.pack()
        self._lint_tooltip = tooltip

    def _hide_lint_tooltip(self, _event: tk.Event | None = None) -> None:
        if self._lint_tooltip_after_id is not None:
            self.after_cancel(self._lint_tooltip_after_id)
            self._lint_tooltip_after_id = None
        if self._lint_tooltip is not None:
            self._lint_tooltip.destroy()
            self._lint_tooltip = None

    def _format_lint_issues(self, issues: list[AnyLintIssue]) -> str:
        if not issues:
            return "lint結果: 問題は見つかりませんでした。"
        if all(isinstance(issue, LintIssue) for issue in issues):
            return format_lint_issues([issue for issue in issues if isinstance(issue, LintIssue)])
        return "\n\n".join(self._format_single_lint_issue(issue) for issue in issues)

    def _format_single_lint_issue(self, issue: AnyLintIssue) -> str:
        label = "エラー" if self._issue_level(issue) == "error" else "警告"
        return (
            f"[{label}] {self._issue_line_number(issue)}行目: {issue.message}\n"
            f"  {issue.hint}"
        )

    def _has_errors(self, issues: list[AnyLintIssue]) -> bool:
        prewp_issues = [issue for issue in issues if isinstance(issue, LintIssue)]
        if prewp_issues:
            return has_errors(prewp_issues)
        return False

    def _issue_line_number(self, issue: AnyLintIssue) -> int:
        if isinstance(issue, WpHtmlLintIssue):
            return issue.line_number
        return issue.line

    def _issue_level(self, issue: AnyLintIssue) -> str:
        if isinstance(issue, WpHtmlLintIssue):
            return "warning"
        return issue.level

    def _create_default_wordpress_save_file_path(self) -> Path:
        if self.current_file_path:
            save_file_name: str = f"{self.current_file_path.stem}_wordpress.wp_html"
            return self.current_file_path.with_name(save_file_name)
        return Path.cwd() / "article_wordpress.wp_html"
