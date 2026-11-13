"""text_editorのMarkdown編集経路を確認するテストです。"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path

from text_editor.editor_frame import (
    TextEditorFrame,
    convert_editor_text_to_gutenberg,
    create_default_markdown_save_file_path,
    is_markdown_editor_path,
)
from text_editor.markers import MARKDOWN_MARKERS, format_marker_text


def _markdown_marker(label: str):
    return next(marker for marker in MARKDOWN_MARKERS if marker.label == label)


def test_txt_and_markdown_use_markdown_editor_mode() -> None:
    assert is_markdown_editor_path("article.txt")
    assert is_markdown_editor_path("article.md")
    assert is_markdown_editor_path("article.markdown")
    assert is_markdown_editor_path(None)


def test_prewp_txt_keeps_legacy_editor_mode() -> None:
    assert not is_markdown_editor_path("article.prewp_txt")
    assert not is_markdown_editor_path("article.wp_txt")
    assert not is_markdown_editor_path("article.wptxt")


def test_default_markdown_path_preserves_txt_and_changes_extension() -> None:
    load_file_path = Path("draft/article.txt")

    save_file_path = create_default_markdown_save_file_path(load_file_path)

    assert save_file_path == Path("draft/article.md")


def test_markdown_heading_marker_prefixes_each_selected_line() -> None:
    marker = _markdown_marker("見出し2")

    marked_text = format_marker_text(marker, "最初\n次")

    assert marked_text == "## 最初\n## 次"


def test_markdown_list_marker_prefixes_each_selected_line() -> None:
    marker = _markdown_marker("箇条書き")

    marked_text = format_marker_text(marker, "りんご\nみかん")

    assert marked_text == "- りんご\n- みかん"


def test_markdown_list_marker_keeps_blank_line_empty() -> None:
    marker = _markdown_marker("箇条書き")

    marked_text = format_marker_text(marker, "りんご\n\nみかん")

    assert marked_text == "- りんご\n\n- みかん"


def test_markdown_ordered_list_numbers_selected_lines() -> None:
    marker = _markdown_marker("番号付きリスト")

    marked_text = format_marker_text(marker, "準備\n実行\n確認")

    assert marked_text == "1. 準備\n2. 実行\n3. 確認"


def test_markdown_bold_wraps_selected_text() -> None:
    marker = _markdown_marker("太字")

    assert format_marker_text(marker, "重要") == "**重要**"


def test_markdown_table_uses_standard_pipe_template() -> None:
    marker = _markdown_marker("表")

    marked_text = format_marker_text(marker)

    assert marked_text.startswith("| 項目 | 説明 |\n|---|---|")
    assert "[Table]" not in marked_text


def test_txt_editor_preview_uses_markdown_converter() -> None:
    save_file = convert_editor_text_to_gutenberg("## 見出し\n\n本文", "article.txt")

    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">見出し</h2>' in save_file
    assert "<!-- wp:paragraph -->" in save_file


def test_prewp_editor_preview_keeps_legacy_converter() -> None:
    save_file = convert_editor_text_to_gutenberg(
        "[Heading:見出し]\n\n本文",
        "article.prewp_txt",
    )

    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert '<h2 class="wp-block-heading">見出し</h2>' in save_file
    assert "[Heading:" not in save_file


def test_markdown_export_saves_source_before_wp_html(tmp_path, monkeypatch) -> None:
    load_file_path = tmp_path / "draft.txt"
    markdown_save_file_path = tmp_path / "draft.md"
    wordpress_save_file_path = tmp_path / "draft_wordpress.wp_html"
    load_file_path.write_text("元の本文", encoding="utf-8")
    dialog_titles: list[str] = []
    selected_paths = iter((str(markdown_save_file_path), str(wordpress_save_file_path)))

    def fake_save_dialog(**options) -> str:
        dialog_titles.append(str(options["title"]))
        return next(selected_paths)

    monkeypatch.setattr("text_editor.editor_frame.filedialog.asksaveasfilename", fake_save_dialog)
    monkeypatch.setattr("text_editor.editor_frame.messagebox.showinfo", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("text_editor.editor_frame.messagebox.showwarning", lambda *_args, **_kwargs: None)

    root = tk.Tk()
    root.withdraw()
    try:
        editor = TextEditorFrame(root, load_file_path)
        editor.text_area.delete("1.0", "end")
        editor.text_area.insert("1.0", "## 保存後に変換\n\n本文")

        assert editor.convert_to_wordpress_html()
        editor.destroy()

        cancelled_dialog_titles: list[str] = []

        def cancel_markdown_save(**options) -> str:
            cancelled_dialog_titles.append(str(options["title"]))
            return ""

        monkeypatch.setattr(
            "text_editor.editor_frame.filedialog.asksaveasfilename",
            cancel_markdown_save,
        )
        cancelled_editor = TextEditorFrame(root, load_file_path)
        assert not cancelled_editor.convert_to_wordpress_html()
        cancelled_editor.destroy()
    finally:
        root.destroy()

    assert dialog_titles == ["Markdownとして保存", "WordPress HTMLの保存先を選んでください"]
    assert markdown_save_file_path.read_text(encoding="utf-8") == "## 保存後に変換\n\n本文"
    save_file = wordpress_save_file_path.read_text(encoding="utf-8")
    assert '<!-- wp:heading {"level":2} -->' in save_file
    assert "<!-- wp:paragraph -->" in save_file
    assert cancelled_dialog_titles == ["Markdownとして保存"]
