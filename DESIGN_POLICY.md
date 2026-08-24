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
