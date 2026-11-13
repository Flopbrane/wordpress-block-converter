# pylint: disable=C0301
"""text_editorの右クリックメニューです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

import tkinter as tk

from text_editor.markers import MARKERS, Marker, format_marker_text


class MarkerMenu:
    """テキストエリアへマーカーを挿入する右クリックメニューです。"""

    def __init__(self, text_area: tk.Text, markers: tuple[Marker, ...] = MARKERS) -> None:
        self.text_area: tk.Text = text_area
        self.menu = tk.Menu(text_area, tearoff=False)
        self.set_markers(markers)

        text_area.bind("<Button-3>", self.show)

    def set_markers(self, markers: tuple[Marker, ...]) -> None:
        """現在の編集形式に合う挿入メニューへ切り替えます。"""
        self.menu.delete(0, "end")
        for marker in markers:
            self.menu.add_command(
                label=marker.label,
                command=lambda selected_marker=marker: self.insert_marker(selected_marker),
            )

    def show(self, event: tk.Event) -> None:
        """右クリック位置にメニューを表示します。"""
        self.menu.tk_popup(event.x_root, event.y_root)
        self.menu.grab_release()

    def insert_marker(self, marker: Marker) -> None:
        """選択範囲、またはカーソル位置へマーカーを挿入します。"""
        selected_text: str | None = self._selected_text()
        insert_index = self.text_area.index("insert")
        if selected_text is not None:
            insert_index = self.text_area.index("sel.first")
            self.text_area.delete("sel.first", "sel.last")
            insert_text = format_marker_text(marker, selected_text)
            self.text_area.insert(insert_index, insert_text)
            self.text_area.mark_set("insert", f"{insert_index} + {len(insert_text)} chars")
            return

        insert_text = format_marker_text(marker)
        self.text_area.insert(insert_index, insert_text)
        if marker.placeholder:
            placeholder_offset = insert_text.find(marker.placeholder)
            start_index = self.text_area.index(f"{insert_index} + {placeholder_offset} chars")
            end_index = self.text_area.index(f"{start_index} + {len(marker.placeholder)} chars")
            self.text_area.tag_add("sel", start_index, end_index)
            self.text_area.mark_set("insert", end_index)
        else:
            self.text_area.mark_set("insert", f"{insert_index} + {len(insert_text)} chars")

    def _selected_text(self) -> str | None:
        try:
            return self.text_area.get("sel.first", "sel.last")
        except tk.TclError:
            return None
