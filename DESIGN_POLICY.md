# Design Policy

## 目的

`wp_converter` は、平文、Markdown、HTMLをWordPressで扱いやすいHTMLへ変換するためのツールです。

主な利用者は、WordPressやHTMLに慣れていない初心者を想定します。
そのため、変換結果は「高機能」よりも「安全」「予測しやすい」「貼り付けやすい」ことを優先します。

## 基本方針

- 既存の変換処理はできるだけ共用します。
- モードごとの差分は、辞書ファイルや安全フィルターに集めます。
- 大型変更よりも、小さく確認しながら拡張できる構成を優先します。
- WordPress側のテーマ装飾やプラグイン装飾は、無理に再現しません。
- コンバーター側では、WordPressに消されにくいHTMLを作ることを重視します。

## 変換モード

### Normal

通常のWordPress環境向けの変換モードです。

想定用途:

- 自分でレンタルサーバーを借りて運用するWordPress
- 比較的自由度の高いWordPress
- GutenbergブロックHTMLを積極的に使いたい場合

方針:

- WordPress Gutenbergブロックを基本にします。
- 動画URLは、可能であれば `wp:embed` として扱います。
- 画像、リンク、表、コード、リストなどを通常通り変換します。
- 今までの既存機能は、原則としてNormalを基準に維持します。

### Hi-Security

制限の強いWordPressや、企業案件向けの安全寄り変換モードです。

想定用途:

- 企業、事業所、団体などのWordPress
- 権限やHTML制限が強いWordPress
- クラウドワークス等で納品する記事HTML
- 保存時にHTMLが削除されやすい環境

方針:

- 危険なタグや属性を出力しません。
- 保存時に削除されにくいHTMLを優先します。
- 見た目の装飾はWordPressテーマ側に任せます。
- 外部動画は埋め込みではなく、通常リンクまたはURL文字列として扱います。
- 外部リンクは全削除せず、安全なリンクだけ残します。

## GUI方針

tkinterのGUIでは、変換前に小さいウインドでモードを選べるようにします。

表示案:

```text
変換モードを選んでください

(*) Normal
( ) Hi-Security
```

画面表示名:

- Normal
- 企業向け安全モード

内部名:

- `normal`
- `hi-security`

初心者が使うことを想定し、専門用語を増やしすぎないようにします。

## 実装方針

基本の流れ:

```text
ファイル読み込み
↓
通常変換
↓
hi-security の場合だけ安全フィルターを通す
↓
保存
```

できるだけ避けたい実装:

- Normal用とHi-Security用でコンバーター全体を二重化する
- 同じ変換ロジックを複数ファイルにコピーする
- モード判定を各所に散らしすぎる

推奨する実装:

- `main.py` で `mode` を受け取る
- CLIでは `--mode normal` / `--mode hi-security` を使う
- GUIではラジオボタンでモードを選ぶ
- `security_dict.py` に安全ルールを集める
- Hi-Security時だけ安全化処理を通す

## Hi-Securityで許可するHTMLの目安

以下は、制限の強いWordPressでも比較的残りやすい安全寄りのタグです。

```html
<p>
<h2>
<h3>
<ul>
<ol>
<li>
<strong>
<em>
<a href="">
<img src="" alt="">
<table>
<tr>
<th>
<td>
<pre>
<code>
```

## Hi-Securityで避けるHTMLの目安

以下は、保存時に削除されたり、セキュリティ上問題になりやすいため、Hi-Securityでは出力しない方針にします。

```html
<script>
<iframe>
<style>
<object>
<embed>
<form>
<input>
```

避ける属性やURL:

```text
onclick
onload
onerror
onmouseover
javascript:
data:
vbscript:
```

## 外部リンクの方針

Hi-Securityでも、外部リンクは全削除しません。

企業案件やECサイトでは、以下のようなリンクが必要になるためです。

- 公式サイト
- 予約ページ
- 決済ページ
- 問い合わせページ
- 地図
- SNS

許可するリンクの目安:

```text
https://
mailto:
tel:
/
#
```

禁止または無効化するリンクの目安:

```text
javascript:
data:
vbscript:
```

### リンク検証メモ

事業所WordPressでは、リンクが残るかどうかはまだ検証中です。

現時点では、次の方針で扱います。

- `href` が正しく付いたリンクだけを残します。
- `harf` などの誤字属性はリンク先として扱いません。
- `https://`、`mailto:`、`tel:`、`/`、`#` は残す候補にします。
- `http://` は、企業案件では安全性が弱いため、Hi-Securityではリンク化せず文字列として残します。
- `target="_blank"` を残す場合は、`rel="noopener"` を付けます。
- `title`、`id`、`class` は必要最小限の安全寄り属性として残す候補にします。

## 動画URLの方針

Normal:

- YouTube、TikTok、Vimeoなどは `wp:embed` として扱います。

Hi-Security:

- `wp:embed` や `iframe` は使いません。
- 動画URLは通常リンク、またはURL文字列として残します。

例:

```html
<a href="https://www.youtube.com/watch?v=XXXXXXXXXXX">https://www.youtube.com/watch?v=XXXXXXXXXXX</a>
```

## 画像の方針

Normal:

- WordPressの画像ブロック、または安全なHTMLとして出力します。

Hi-Security:

- `<img src="" alt="">` を基本にします。
- 危険な属性は付けません。
- `onerror` などのイベント属性は削除します。

## コード表示の方針

コードは、WordPressテーマ側で装飾される可能性があります。

Normal、Hi-Securityともに、基本は以下の形を優先します。

```html
<pre><code>コード本文</code></pre>
```

Gutenbergブロックコメントを使う場合も、Hi-Securityでは余計な属性を増やしすぎないようにします。

### 事業所WordPressでのコード表示メモ

事業所WordPressのCSSを確認したところ、`code` と `pre code` で見た目が分かれていました。

確認できた傾向:

- 段落内の `<code>` は赤系の文字になりやすいです。
- `<pre><code>...</code></pre>` の中の `code` は、`pre` 側の文字色を引き継ぎ、黒系の表示になりやすいです。
- そのため、短いHTMLタグ例は paragraph内の `<code>` として出す方が、初心者向け記事では見やすい可能性があります。
- 長いコード例や複数行のコードは、引き続き `<pre><code>` を維持します。

Hi-Securityでの推奨:

```text
短いHTMLタグ例:
paragraph内の <code>

長いコード例:
wp:code + <pre class="wp-block-code"><code>
```

例:

```html
<p><code>&lt;h2&gt;</code> は見出しを表します。</p>

<pre><code>def hello() -> None:
    print("Hello, WordPress")</code></pre>
```

長いコード例は、WordPressコードエディターへ貼り付ける用途を考え、Hi-Securityでも次のブロックコメントを残します。

```html
<!-- wp:code -->
<pre class="wp-block-code"><code>コード本文</code></pre>
<!-- /wp:code -->
```

## 事業所WordPressのCSS観察メモ

2026-08-25時点で、事業所WordPressから保存したCSSを確認した結果、次の傾向がありました。

- `code` 単体には赤系の文字色が指定されていました。
- `pre code` には `pre` 側の文字色を継承する指定がありました。
- `h3:before` によって、見出しの文頭へ装飾が付く可能性があります。
- `iframe` を前提にした動画表示用CSSは存在しますが、Hi-Securityでは `iframe` は使わず、通常リンクを優先します。

このため、Hi-Security Modeでは「WordPressテーマの装飾に自然に乗る、素朴なHTML」を優先します。

## 今後の拡張基準

新しい機能を追加するときは、次の順番で判断します。

1. Normalで必要か
2. Hi-Securityでも安全に残せるか
3. Hi-Securityではリンク化、文字列化、削除のどれが自然か
4. GUIで初心者が迷わない表示にできるか
5. READMEに簡単に説明できるか

## Ver.1系の目標

Ver.1系では、次の範囲を中心にします。

- `.txt`
- `.md`
- `.markdown`
- `.html`
- `.htm`
- link
- image
- table
- embed
- spacer
- code

JSON、XML、YAML、TOML、DOCX、XLSX、PDFなどは、Ver.2以降の検討対象とします。

## 設計メモ

`wp_converter` は、単なるHTML変換ツールではなく、WordPress記事の下書きや納品用HTMLを整える補助ツールとして育てます。

特にHi-Securityは、「全部消すモード」ではありません。
危険なものだけ避け、仕事で必要なリンクや本文構造は残すモードとして扱います。

## Hi-Security Mode 実装方針

Hi-Security Mode は、通常変換処理を別系統に分けず、通常変換後のHTMLに安全化フィルターを通す方式を基本とします。

基本の流れ:

```text
load_file 読み込み
↓
拡張子に応じて通常変換
↓
mode が hi-security の場合だけ安全化フィルターを適用
↓
save_file に保存
```

## CLIでは --mode を使用します

python .\main.py .\sample.md .\sample_wordpress.html --mode normal
python .\main.py .\sample.md .\sample_safe_wordpress.html --mode hi-security

省略時は normal とします。

## GUIでは、変換前に以下の選択肢を表示します。

変換モード:
(*) Normal
( ) 企業向け安全モード

内部名:
| 表示名             | 内部名        |
| ------------------ | ------------- |
| Normal             | `normal`      |
| 企業向け安全モード | `hi-security` |

## 共用方針

Normal用とHi-Security用で、converter全体を二重化しません。

共用するもの:

- text_converter.py
- markdown_converter.py
- html_converter.py
- blocks/ 配下の基本ブロック生成処理
- 既存の辞書ファイル

Hi-Security専用に分けるもの:

- 安全化ルール
- 禁止タグ一覧
- 許可タグ一覧
- 禁止属性一覧
- URLスキーム判定
- embed を通常リンクへ戻す処理
- 安全化フィルターの適用処理

追加ファイル案
dictionaries/hi_security_dict.py
converters/hi_security_filter.py

hi_security_dict.py には、判定用の定数を集めます。

### 例:

```python
ALLOWED_TAGS = {
    "p", "h2", "h3", "h4",
    "ul", "ol", "li",
    "strong", "em",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "pre", "code", "br",
}

BLOCKED_TAGS = {
    "script", "iframe", "style", "object", "embed",
    "form", "input", "button", "textarea", "select",
}

BLOCKED_ATTRIBUTES = {
    "onclick", "onload", "onerror", "onmouseover", "style",
}

ALLOWED_URL_PREFIXES = (
    "https://",
    "mailto:",
    "tel:",
    "/",
    "#",
)

BLOCKED_URL_PREFIXES = (
    "javascript:",
    "data:",
    "vbscript:",
)
```

## Hi-Securityでの変換方針

| 入力           | Normal           | Hi-Security                   |
| -------------- | ---------------- | ----------------------------- |
| YouTube URL    | `wp:embed`       | 通常リンク                    |
| TikTok URL     | `wp:embed`       | 通常リンク                    |
| Vimeo URL      | `wp:embed`       | 通常リンク                    |
| `<iframe>`     | 必要に応じて保持 | 削除またはリンク化            |
| `<script>`     | 削除             | 削除                          |
| `<style>`      | 場合により保持   | 削除                          |
| `onclick` など | 削除             | 削除                          |
| `javascript:`  | 削除             | 削除                          |
| 短いタグ例     | 通常処理         | paragraph内の `<code>` を優先 |
| 長いコード     | `wp:code`        | `<pre><code>` を維持          |

## 見出しルール

WordPressでは記事タイトルが h1 相当になるため、Hi-Security Modeでは本文内の見出しを h2 から始めることを推奨します。

| Markdown | Normal | Hi-Security                   |
| -------- | ------ | ----------------------------- |
| `#`      | `h1`   | 記事タイトル候補、または `h2` |
| `##`     | `h2`   | `h2`                          |
| `###`    | `h3`   | `h3`                          |
| `####`   | `h4`   | `h4`                          |

先生としては、まず実装はこの形が良いです。

```text
main.py
  --mode を受け取る

既存converter
  今まで通り変換

hi_security_filter.py
  最後に安全化

hi_security_dict.py
  ルールだけ持つ

この構成なら、Normal版を壊しにくいです。
しかも事業所WPで分かった実戦データを、hi_security_dict.py に少しずつ足して育てられます。
```

## Hi-Security Mode Policy

Hi-Security mode is designed for restricted WordPress environments.

The converter should prefer stable Gutenberg-compatible HTML that survives saving in the block editor.

Priority:
1. Preserve readable article structure.
2. Avoid unsafe or easily stripped HTML.
3. Keep normal mode unchanged.
4. Share existing converter and block functions where possible.

Allowed direction:
- headings: h2, h3, h4, h5
- paragraph text
- inline code
- safe links
- images with src and alt
- tables
- pre/code blocks

Avoid:
- script
- iframe
- style
- object
- embed
- forms
- event attributes
- javascript: URLs

External videos should become normal links in Hi-Security mode.

## Hi-Security Heading Comment Policy

Hi-Security Modeでは、見出しタグとWordPressブロックコメントのlevelをそろえます。

推奨する出力:

```html
<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">見出し</h2>
<!-- /wp:heading -->

<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">小見出し</h3>
<!-- /wp:heading -->
```

方針:

- `h2`、`h3`、`h4`、`h5` を本文見出しとして使います。
- Hi-Securityでは `h2` にも `{"level":2}` を明記します。
- Markdownの `#` は、本文内では `h2` 相当に寄せます。
- `h6` は、企業向け安全モードでは `h5` へ寄せます。

## Hi-Security Block Comment Policy

Hi-Security Modeでは、保存後の生存率とWordPressコードエディターでの扱いやすさを両立するため、安全寄りのブロックコメントだけを残します。

残すブロックコメント:

- `wp:paragraph`
- `wp:heading`
- `wp:code`
- `wp:table`
- `wp:separator`

原則として避けるブロックコメント:

- `wp:html`
- `wp:embed`

表は、可能な範囲で次の形を維持します。

```html
<!-- wp:table -->
<figure class="wp-block-table"><table>...</table></figure>
<!-- /wp:table -->
```

段落内に `---`、`***`、`___` だけが入っている場合は、区切り線として扱います。

```html
<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->
```
