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


MARKERS: tuple[Marker, ...] = (
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
