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
    Marker("段落", "<!-- wp:paragraph -->\n", "\n<!-- /wp:paragraph -->", "本文"),
    Marker("HTML", "<!-- wp:html -->\n", "\n<!-- /wp:html -->", "<div>HTML</div>"),
    Marker("見出し", "【", "】", "見出し本文"),
    Marker("小見出し", "《", "》", "小見出し本文"),
    Marker("通常コード", "[コード]\n", "\n[/コード]", "コード内容"),
    Marker("強調コード", "[強調コード]\n", "\n[/強調コード]", "強調したい文字列や短いコード"),
    Marker("引用", "> ", "", "引用文"),
    Marker("リスト", "[リスト]\n", "\n[/リスト]", "項目1\n項目2\n項目3"),
    Marker("番号リスト", "[番号リスト]\n", "\n[/番号リスト]", "項目1\n項目2\n項目3"),
    Marker("箇条書き", "・", "", "項目"),
    Marker("番号付き行", "1. ", "", "項目"),
    Marker("表", "[表]\n", "\n[/表]", "項目|説明\nA|説明文\nB|説明文"),
    Marker("リンク", "[リンク:", "|https://example.com/]", "表示文字"),
    Marker("画像", "[画像:https://example.com/image.jpg|", "]", "代替テキスト"),
    Marker("区切り線", "---", "", ""),
    Marker("余白", "[余白:25]", "", ""),
)
