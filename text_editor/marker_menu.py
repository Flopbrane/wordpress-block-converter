"""text_editorの右クリックメニューです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import tkinter as tk

from text_editor.markers import MARKERS, Marker


class MarkerMenu:
    """テキストエリアへマーカーを挿入する右クリックメニューです。"""

    def __init__(self, text_area: tk.Text) -> None:
        self.text_area = text_area
        self.menu = tk.Menu(text_area, tearoff=False)
        for marker in MARKERS:
            self.menu.add_command(
                label=marker.label,
                command=lambda selected_marker=marker: self.insert_marker(selected_marker),
            )

        text_area.bind("<Button-3>", self.show)

    def show(self, event: tk.Event) -> None:
        """右クリック位置にメニューを表示します。"""
        self.menu.tk_popup(event.x_root, event.y_root)
        self.menu.grab_release()

    def insert_marker(self, marker: Marker) -> None:
        """選択範囲、またはカーソル位置へマーカーを挿入します。"""
        selected_text = self._selected_text()
        if selected_text is not None:
            self.text_area.delete("sel.first", "sel.last")
            self.text_area.insert("insert", f"{marker.before}{selected_text}{marker.after}")
            return

        insert_text = f"{marker.before}{marker.placeholder}{marker.after}"
        cursor_offset = len(marker.before)
        self.text_area.insert("insert", insert_text)
        start_index = self.text_area.index(f"insert - {len(insert_text) - cursor_offset} chars")
        end_index = self.text_area.index(f"{start_index} + {len(marker.placeholder)} chars")
        if marker.placeholder:
            self.text_area.tag_add("sel", start_index, end_index)
            self.text_area.mark_set("insert", end_index)
        else:
            self.text_area.mark_set("insert", f"{start_index}")

    def _selected_text(self) -> str | None:
        try:
            return self.text_area.get("sel.first", "sel.last")
        except tk.TclError:
            return None
