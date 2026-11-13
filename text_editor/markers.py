"""text_editorで挿入するマーカー定義です。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Marker:
    """右クリックメニューから挿入するマーカーです。"""

    label: str
    before: str
    after: str = ""
    placeholder: str = ""
    action: str = "wrap"


PREWP_MARKERS: tuple[Marker, ...] = (
    Marker("Paragraph", "<!-- wp:paragraph -->\n", "\n<!-- /wp:paragraph -->", "Body text"),
    Marker("Line breaks", "<!-- wp:paragraph -->\n", "\n<!-- /wp:paragraph -->", "Line 1\nLine 2"),
    Marker("HTML block", "[HTML]\n", "\n[/HTML]", "<div>HTML</div>"),
    Marker("HTML", "<!-- wp:html -->\n", "\n<!-- /wp:html -->", "<div>HTML</div>"),
    Marker("Bold", "[Bold]", "[/Bold]", "Bold text"),
    Marker("Notice box", "[Notice]\n", "\n[/Notice]", "Notice text"),
    Marker("Supplement box", "[Supplement]\n", "\n[/Supplement]", "Supplement text"),
    Marker("Box", "[Box]\n", "\n[/Box]", "Box text"),
    Marker("Heading", "[Heading:", "]", "Heading text"),
    Marker("Subheading", "[Subheading:", "]", "Subheading text"),
    Marker("Code", "[Code]\n", "\n[/Code]", "Code text"),
    Marker("Emphasis code", "[EmphasisCode]\n", "\n[/EmphasisCode]", "Short code or parameter"),
    Marker("Quote", "> ", "", "Quote text"),
    Marker("List", "[List]\n", "\n[/List]", "Item 1\nItem 2\nItem 3"),
    Marker("Ordered list", "[OrderedList]\n", "\n[/OrderedList]", "Item 1\nItem 2\nItem 3"),
    Marker("Steps", "[Steps]\n", "\n[/Steps]", "Step 1\nStep 2\nStep 3"),
    Marker(
        "Image row",
        "[ImageRow:24px]\n",
        "\n[/ImageRow]",
        "[Image:https://example.com/image1.jpg|Image 1]\n"
        "[Image:https://example.com/image2.jpg|Image 2]\n"
        "[Image:https://example.com/image3.jpg|Image 3]",
    ),
    Marker("Bullet line", "- ", "", "Item"),
    Marker("Numbered line", "1. ", "", "Item"),
    Marker("Table", "[Table]\n", "\n[/Table]", "Item|Description\nA|Description A\nB|Description B"),
    Marker("Link", "[Link:", "|https://example.com/]", "Label"),
    Marker("Image", "[Image:https://example.com/image.jpg|", "]", "Alt text"),
    Marker("Audio", "[Audio:https://example.com/audio.mp3]", "", ""),
    Marker("Video", "[Video:https://example.com/video.mp4]", "", ""),
    Marker("File", "[File:https://example.com/file.pdf]", "", ""),
    Marker("Separator", "---", "", ""),
    Marker("Spacer", "[Spacer:25]", "", ""),
)

# 既存コードとの互換名です。新しい.txt編集ではMARKDOWN_MARKERSを使います。
MARKERS: tuple[Marker, ...] = PREWP_MARKERS

MARKDOWN_MARKERS: tuple[Marker, ...] = (
    Marker("見出し1", "# ", placeholder="見出し", action="line_prefix"),
    Marker("見出し2", "## ", placeholder="見出し", action="line_prefix"),
    Marker("見出し3", "### ", placeholder="見出し", action="line_prefix"),
    Marker("箇条書き", "- ", placeholder="項目", action="line_prefix"),
    Marker("番号付きリスト", "", placeholder="項目", action="ordered_list"),
    Marker("引用", "> ", placeholder="引用文", action="line_prefix"),
    Marker("太字", "**", "**", "重要"),
    Marker("インラインコード", "`", "`", "code"),
    Marker("コードブロック", "```\n", "\n```", "code"),
    Marker("リンク", "[", "](https://example.com/)", "表示名"),
    Marker("画像", "![", "](https://example.com/image.jpg)", "代替テキスト"),
    Marker(
        "表",
        "",
        "",
        "| 項目 | 説明 |\n|---|---|\n| A | 説明A |\n| B | 説明B |",
    ),
    Marker("区切り線", "---"),
)


def format_marker_text(marker: Marker, selected_text: str | None = None) -> str:
    """選択文字列またはひな型へ、指定した記法を適用します。"""
    target_text = marker.placeholder if selected_text is None else selected_text
    if marker.action == "line_prefix":
        return _prefix_each_line(target_text, marker.before)
    if marker.action == "ordered_list":
        return _number_each_line(target_text)
    return f"{marker.before}{target_text}{marker.after}"


def _prefix_each_line(text: str, prefix: str) -> str:
    lines = text.splitlines() or [""]
    return "\n".join(f"{prefix}{line}" if line else line for line in lines)


def _number_each_line(text: str) -> str:
    lines = text.splitlines() or [""]
    item_number = 0
    numbered_lines: list[str] = []
    for line in lines:
        if not line.strip():
            numbered_lines.append(line)
            continue
        item_number += 1
        numbered_lines.append(f"{item_number}. {line}")
    return "\n".join(numbered_lines)
