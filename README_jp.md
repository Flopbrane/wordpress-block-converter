# WordPress Block Converter

平文、Markdown、簡単なHTMLを、WordPressのGutenbergブロック用HTMLへ変換するPythonツールです。  

WordPressの記事下書きを作るときに、手作業でブロックコメントを書く負担を減らすことを目的にしています。  

このツールは、WordPressのビジュアルエディター上での自動整形を避け、  

安定したブロックHTMLを作成してコードエディターへ貼り付けるための補助ツールです。  

## できること

- 平文 `.txt` を段落ブロックへ変換
- Markdownの見出し、本文、リスト、引用、コード、表、区切り線、画像、ショートコードを変換
- HTMLの見出し、段落、リスト、引用、コード、表、画像、リンク、ショートコードを変換
- CSV/SSV/TSV/PSVなどの区切り値ファイルを表ブロックへ変換
- JSONの構造データから見出し、段落、リスト、表、FAQを変換
- YouTube、YouTube Shorts、TikTok、VimeoなどのURLを埋め込みブロックへ変換
- 画像・動画・音声・PDFなどの直接URLを、それぞれ適したブロックへ変換
- リンク、太字、斜体などの基本的な本文装飾を保持
- 平文の段落間に24pxの余白ブロックを挿入
- GUIでload_fileとsave_fileを選択
- コマンドラインからも実行可能
- Python標準ライブラリのみで動作

## 対応しているload_file

| 種類 | 拡張子 |
|---|---|
| 平文 | `.txt` |
| Markdown | `.md`, `.markdown` |
| HTML | `.html`, `.htm` |
| 区切り値ファイル | `.csv`, `.ssv`, `.tsv`, `.psv`, `.pipesv` |
| JSON | `.json` |

## バージョン対応

| バージョン | 対応内容 | 状態 |
|---|---|---|
| Ver.1.0 | 平文、Markdown、HTMLの基本変換 | 対応済み |
| Ver.1.1 | 埋め込みURL、画像、動画、音声、ファイルURL、Hi-Security Mode | 対応済み |
| Ver.1.2 | CSV / SSV / TSV / PSVをtableブロックへ変換 | 対応済み |
| Ver.1.3 | JSONから見出し、段落、リスト、表、FAQを生成 | 対応済み |
| Ver.1.4 | Markdown独自レイアウト記法。画像横並び、画像＋文章、CTA、FAQ、カード型レイアウト | 着手中 |

## 対応しているWordPressブロック

| 内容 | WordPressブロック |
|---|---|
| 段落 | `core/paragraph` |
| 見出し | `core/heading` |
| リスト | 基本は `core/html` |
| コード | `core/code` |
| 引用 | `core/quote` |
| 余白 | `core/spacer` |
| 区切り線 | `core/separator` |
| 表 | `core/table` |
| カスタムHTML | `core/html` |
| 画像 | `core/image` |
| 動画ファイル | `core/video` |
| 音声ファイル | `core/audio` |
| ダウンロードファイル | `core/file` |
| ショートコード | `core/shortcode` |
| 外部サービスURL | `core/embed` |

## 変換ルールの概要

### 平文

- 空行で段落を分けます。
- 段落内の改行は `<br><br>` に変換します。
- 段落と段落の間には24pxのspacerブロックを入れます。

### Markdown

対応している主な書き方です。

- 見出し: `#` から `######`
- 段落
- 箇条書き: `-`, `*`, `+`
- 番号付きリスト: `1.` または `1)`
- コードブロック: 三連バッククォート
- 引用: `> 引用文`
- 表: `| 列 | 列 |`
- 画像: `![代替テキスト](https://example.com/image.jpg)`
- リンク: `[表示名](https://example.com/)`
- 太字・斜体: `**太字**`, `*斜体*`
- 区切り線: `---`, `***`, `___`
- 余白指定: `[spacer]` または `[spacer:60]`
- WordPressショートコード: `[shortcode ...]`
- 単独行のURL

#### Markdown独自レイアウト記法

Ver.1.4では、`:::名前` から `:::` までを1つのレイアウト指定として扱います。

対応予定、または対応中の主な記法です。

- `:::image_text_left`: 画像左、文章右
- `:::image_text_right`: 画像右、文章左
- `:::image_row_3`: 画像横並び
- `:::cta`: CTA見出し、本文、ボタン
- `:::faq`: FAQ
- `:::cards`: カード型レイアウト

例:

```markdown
:::image_text_left
image: https://example.com/service.jpg
alt: サービス紹介画像
title: 私たちのサービス
text: ここに説明文を入れます。
width: 40
:::
```

### HTML

対応している主なHTMLです。

- `<p>`, `<h1>` から `<h6>`
- `<ul>`, `<ol>`, `<li>`
- `<blockquote>`
- `<pre>`, `<code>`
- `<table>`, `<tr>`, `<th>`, `<td>`
- `<img>`
- `<a>`
- `<strong>`, `<b>`, `<em>`, `<i>`
- `<hr>`

`<b>` は `<strong>` に、`<i>` は `<em>` に寄せて出力します。

### 区切り値ファイル

CSV、TSV、SSV、PSVをWordPressのtableブロックへ変換します。

- `.csv`: カンマ区切り
- `.tsv`: タブ区切り
- `.ssv`: スペース区切り、またはセミコロン区切り
- `.psv`, `.pipesv`: パイプ区切り

区切り文字はファイル内容からも推定します。1行目は見出し行として扱います。

### JSON

JSONの構造データから、WordPressの基本ブロックを生成します。

- `title`, `heading`: 見出し
- `text`, `body`, `description`: 段落
- `sections`, `blocks`, `content`: セクション
- `items`, `list`: リスト
- `table`, `rows`: 表
- `faq`, `faqs`: FAQ

1つのJSONから、会社紹介ページ、サービス紹介ページ、FAQ、商品一覧のような下書きを作れます。

### URLの分別

単独行のURLは、種類によって変換先を分けます。

| URLの種類 | 変換先 |
|---|---|
| YouTube / YouTube Shorts / TikTok / Vimeo / Instagram / X / Twitter / Dailymotion / Twitch / TED / Spotify / SoundCloud | `core/embed` |
| `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.avif` | `core/image` |
| `.mp4`, `.webm`, `.mov`, `.m4v` | `core/video` |
| `.mp3`, `.wav`, `.ogg`, `.m4a` | `core/audio` |
| `.pdf`, `.zip`, Officeファイル | `core/file` |
| 本文中のその他URL | 通常のHTMLリンク |

## 必要環境

- Python 3.10 以降

外部パッケージのインストールは不要です。

## 使い方

### GUIで使う場合

```powershell
python .\main.py --gui
```

画面が開いたら、次の順番で選択します。

1. 変換したいload_file
2. 保存先のsave_file

引数なしで実行した場合も、自動的にGUIが開きます。

```powershell
python .\main.py
```

### コマンドラインで使う場合

```powershell
python .\main.py .\sample.md .\sample_wordpress.html
```

`load_file_path` と `save_file_path` を指定して変換します。

## 変換例

入力Markdown:

```markdown
# 動画テスト

これは本文です。

https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

出力HTML:

```html
<!-- wp:heading {"level":1} -->
<h1>動画テスト</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>これは本文です。</p>
<!-- /wp:paragraph -->

<!-- wp:embed {"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio">
<div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=dQw4w9WgXcQ
</div>
</figure>
<!-- /wp:embed -->
```

## フォルダ構成

```text
wp_converter/
├─ main.py
├─ storage.py
├─ file_checker.py
├─ gui_maker.py
├─ converters/
│  ├─ document_converter.py
│  ├─ hi_security_filter.py
│  ├─ html_converter.py
│  ├─ json_converter.py
│  ├─ markdown_layout_converter.py
│  ├─ markdown_converter.py
│  ├─ separated_values_converter.py
│  ├─ text_converter.py
├─ blocks/
│  ├─ code.py
│  ├─ embed.py
│  ├─ heading.py
│  ├─ html_block.py
│  ├─ image.py
│  ├─ inline.py
│  ├─ list_block.py
│  ├─ layout.py
│  ├─ media.py
│  ├─ paragraph.py
│  ├─ quote.py
│  ├─ separator.py
│  ├─ shortcode.py
│  ├─ spacer.py
│  └─ table.py
└─ dictionaries/
   ├─ hi_security_dict.py
   ├─ html_dict.py
   ├─ json_dict.py
   ├─ markdown_dict.py
   ├─ separated_values_dict.py
   └─ text_dict.py
```

## 各フォルダの役割

| 場所 | 役割 |
|---|---|
| `main.py` | 引数処理、変換全体の流れ |
| `storage.py` | load_fileの読み込み、save_fileの保存 |
| `file_checker.py` | 対応拡張子の確認、converter選択 |
| `gui_maker.py` | GUI表示、ファイル選択画面 |
| `converters/` | 入力形式ごとの変換処理 |
| `blocks/` | WordPressブロックHTMLを作る部品 |
| `dictionaries/` | 変換ルール、正規表現、対応拡張子 |

## 開発方針

最初から大きな変換エンジンにせず、初心者でも追いやすいように小さな関数で分けています。

現在の目標は、完璧なMarkdownパーサーやHTMLパーサーを作ることではなく、WordPressへ貼り付けやすい安定したHTMLを作ることです。

## 注意点

複雑なHTML、WordPressテーマ独自の装飾、プラグイン専用ブロックには完全対応していません。

変換後は、WordPressの編集画面やプレビュー画面で表示確認することをおすすめします。

## ライセンス

まだライセンスは設定していません。
