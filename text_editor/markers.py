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
    Marker("改行を<br>に変換", "<!-- wp:paragraph -->\n", "\n<!-- /wp:paragraph -->", "1行目\n2行目"),
    Marker("HTML実行ブロック", "[HTML]\n", "\n[/HTML]", "<div>HTML</div>"),
    Marker("HTML", "<!-- wp:html -->\n", "\n<!-- /wp:html -->", "<div>HTML</div>"),
    Marker("太字", "[太字]", "[/太字]", "太字にする文字"),
    Marker("注意枠", "[注意]\n", "\n[/注意]", "注意文"),
    Marker("補足枠", "[補足]\n", "\n[/補足]", "補足文"),
    Marker("囲い込み", "[囲い込み]\n", "\n[/囲い込み]", "囲い込みたい本文"),
    Marker("見出し", "【", "】", "見出し本文"),
    Marker("小見出し", "《", "》", "小見出し本文"),
    Marker("通常コード", "[コード]\n", "\n[/コード]", "コード内容"),
    Marker("強調コード", "[強調コード]\n", "\n[/強調コード]", "強調したい文字列や短いコード"),
    Marker("引用", "> ", "", "引用文"),
    Marker("リスト", "[リスト]\n", "\n[/リスト]", "項目1\n項目2\n項目3"),
    Marker("番号リスト", "[番号リスト]\n", "\n[/番号リスト]", "項目1\n項目2\n項目3"),
    Marker("手順リスト", "[手順]\n", "\n[/手順]", "手順1\n手順2\n手順3"),
    Marker(
        "画像横並び",
        "[画像横並び:24px]\n",
        "\n[/画像横並び]",
        "[画像:https://example.com/image1.jpg|画像1]\n"
        "[画像:https://example.com/image2.jpg|画像2]\n"
        "[画像:https://example.com/image3.jpg|画像3]",
    ),
    Marker("箇条書き", "・", "", "項目"),
    Marker("番号付き行", "1. ", "", "項目"),
    Marker("表", "[表]\n", "\n[/表]", "項目|説明\nA|説明文\nB|説明文"),
    Marker("リンク", "[リンク:", "|https://example.com/]", "表示文字"),
    Marker("画像", "[画像:https://example.com/image.jpg|", "]", "代替テキスト"),
    Marker("音声", "[音声:https://example.com/audio.mp3]", "", ""),
    Marker("動画", "[動画:https://example.com/video.mp4]", "", ""),
    Marker("ファイル", "[ファイル:https://example.com/file.pdf]", "", ""),
    Marker("区切り線", "---", "", ""),
    Marker("余白", "[余白:25]", "", ""),
)
