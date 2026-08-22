# WordPress Block Converter

平文、Markdown、簡単なHTMLを、WordPressのGutenbergブロック用HTMLへ変換するPythonツールです。

WordPressの記事下書きを作るときに、手作業でブロックコメントを書く負担を減らすことを目的にしています。

## できること

- 平文 `.txt` を段落ブロックへ変換
- Markdownの見出しと本文を変換
- HTMLの見出し、段落、リストを変換
- YouTubeのURLを埋め込みブロックへ変換
- TikTokのURLを埋め込みブロックへ変換
- GUIでload_fileとsave_fileを選択
- コマンドラインからも実行可能
- Python標準ライブラリのみで動作

## 対応しているload_file

| 種類 | 拡張子 |
|---|---|
| 平文 | `.txt` |
| Markdown | `.md`, `.markdown` |
| HTML | `.html`, `.htm` |

## 対応しているWordPressブロック

| 内容 | WordPressブロック |
|---|---|
| 段落 | `core/paragraph` |
| 見出し | `core/heading` |
| HTMLリスト・表 | `core/html` |
| コード | `core/code` |
| 引用 | `core/quote` |
| 余白 | `core/spacer` |
| YouTube / TikTok埋め込み | `core/embed` |

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
├─ converters/
│  ├─ markdown_converter.py
│  ├─ text_converter.py
│  └─ html_converter.py
├─ blocks/
│  ├─ code.py
│  ├─ embed.py
│  ├─ heading.py
│  ├─ html_block.py
│  ├─ list_block.py
│  ├─ paragraph.py
│  ├─ quote.py
│  └─ spacer.py
└─ dictionaries/
   ├─ markdown_dict.py
   ├─ text_dict.py
   └─ html_dict.py
```

## 各フォルダの役割

| 場所 | 役割 |
|---|---|
| `main.py` | file選択、引数処理、保存処理 |
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
