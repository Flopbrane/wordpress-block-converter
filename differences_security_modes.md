# Differences Between Middle and Hi-security Modes

この文書は、`Middle/事業所向け` モードと `Hi-security` モードで、そのまま出力されないHTML・WordPressブロック・属性の扱いをまとめたものです。

## モード名

| 指定名 | 内部扱い | 用途 |
|---|---|---|
| `middle` | `middle` | 事業所WordPress向け。Gutenberg標準ブロックへ寄せ、危険HTMLを落とします。 |
| `office` | `middle` | `middle` の互換別名です。 |
| `high-security` | `high-security` | より制限の強い環境向け。危険HTML・危険属性・危険URLを落とします。 |
| `hi-security` | `high-security` | `high-security` の互換別名です。 |

現時点では、`middle` と `high-security` は同じ安全化フィルターを通します。  
違いは主にモード名の意味付けで、どちらも下記のHTMLや属性をそのまま残しません。

## 削除されるタグ

以下のタグは、`middle` / `high-security` のどちらでも出力されません。

| 入力例 | 出力での扱い | 理由 |
|---|---|---|
| `<script>...</script>` | タグと中身を削除 | JavaScript実行を避けるため |
| `<iframe ...>...</iframe>` | タグと中身を削除 | 外部埋め込みや実行HTMLを避けるため |
| `<style>...</style>` | タグと中身を削除 | インラインCSS依存を避けるため |
| `<object>...</object>` | タグと中身を削除 | 外部実行・埋め込みを避けるため |
| `<embed ...>` | タグと中身を削除 | 外部実行・埋め込みを避けるため |
| `<textarea>...</textarea>` | タグと中身を削除 | フォーム部品を避けるため |
| `<select>...</select>` | タグと中身を削除 | フォーム部品を避けるため |
| `<form>...</form>` | タグを削除 | フォーム送信を避けるため |
| `<input>` | タグを削除 | フォーム部品を避けるため |
| `<button>` | タグを削除 | ボタン動作を避けるため |

## 削除される属性

以下の属性は、許可タグについていても削除されます。

| 入力例 | 出力での扱い | 理由 |
|---|---|---|
| `style="color:red"` | `style` を削除 | CSS依存を避けるため |
| `onclick="..."` | `onclick` を削除 | JavaScript実行を避けるため |
| `onload="..."` | `onload` を削除 | JavaScript実行を避けるため |
| `onerror="..."` | `onerror` を削除 | JavaScript実行を避けるため |
| `onmouseover="..."` | `onmouseover` を削除 | JavaScript実行を避けるため |

## 削除または無効化されるURL

危険なURLや、制限対象のURLはリンク・画像URLとして残しません。

| 入力例 | 出力での扱い |
|---|---|
| `<a href="javascript:alert(1)">text</a>` | `<a>` は削除され、表示文字だけ残ります。 |
| `<a href="data:text/html,...">text</a>` | `<a>` は削除され、表示文字だけ残ります。 |
| `<a href="vbscript:...">text</a>` | `<a>` は削除され、表示文字だけ残ります。 |
| `<a href="http://example.com">text</a>` | `<a>` は削除され、表示文字だけ残ります。 |
| `<img src="data:image/png;base64,...">` | `<img>` は出力されません。 |
| `<img src="http://example.com/image.jpg">` | `<img>` は出力されません。 |

`href` で残せるURLは、現在は `https://`、`mailto:`、`tel:`、`/`、`#` です。  
`src` で残せるURLは、現在は `https://` と `/` です。

## 変換されるWordPressブロック

以下はそのまま残さず、安全寄りの形へ変換します。

| 入力 | 出力 |
|---|---|
| `wp:embed` のYouTube等埋め込み | 通常の段落内リンクへ変換 |
| `wp:heading` の `h1` | `h2` へ変換 |
| `wp:heading` の `h6` | `h5` へ変換 |
| `wp:paragraph` 内の `---`、`***`、`___` | `wp:separator` へ変換 |
| 前後が空白の `\\` | `<br><br>` へ変換 |
| 6行以内の短いHTML例コードブロック | 段落内の `<code>...</code>` 表示へ変換 |

短いHTML例コードブロックの例:

```html
<!-- wp:code -->
<pre class="wp-block-code"><code>&lt;p&gt;本文&lt;/p&gt;</code></pre>
<!-- /wp:code -->
```

出力例:

```html
<!-- wp:paragraph -->
<p><code>&lt;p&gt;本文&lt;/p&gt;</code></p>
<!-- /wp:paragraph -->
```

## 保持されるWordPressブロック

以下のWordPressブロックコメントは、`middle` / `high-security` でも保持します。

| ブロック | 保持する例 |
|---|---|
| paragraph | `<!-- wp:paragraph -->` / `<!-- /wp:paragraph -->` |
| heading | `<!-- wp:heading {"level":2} -->` / `<!-- /wp:heading -->` |
| code | `<!-- wp:code -->` / `<!-- /wp:code -->` |
| table | `<!-- wp:table -->` / `<!-- /wp:table -->` |
| separator | `<!-- wp:separator -->` / `<!-- /wp:separator -->` |
| list | `<!-- wp:list -->` / `<!-- /wp:list -->` |
| ordered list | `<!-- wp:list {"ordered":true} -->` / `<!-- /wp:list -->` |
| list item | `<!-- wp:list-item -->` / `<!-- /wp:list-item -->` |

## 保持されるHTMLタグ

以下のタグは、許可された属性だけを残して出力します。

| 系統 | タグ |
|---|---|
| 本文 | `p`, `strong`, `em`, `br`, `hr` |
| 見出し | `h2`, `h3`, `h4`, `h5` |
| リスト | `ul`, `ol`, `li` |
| メディア | `a`, `img` |
| 表 | `figure`, `table`, `thead`, `tbody`, `tr`, `th`, `td` |
| コード | `pre`, `code` |

`ul` / `ol` / `li` は、HTML変換後に以下のようなWordPress listブロックとして残す方針です。

```html
<!-- wp:list -->
<ul class="wp-block-list">
<!-- wp:list-item -->
<li>項目</li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->
```

## 残さないWordPressブロックコメント

安全化フィルターで許可していないWordPressブロックコメントは削除されます。  
中のHTMLが許可タグであれば、HTML部分だけ残ることがあります。

| 入力例 | 出力での扱い |
|---|---|
| `<!-- wp:html -->` | ブロックコメントは削除。許可HTMLだけ残る。 |
| `<!-- wp:shortcode -->` | ブロックコメントは削除。 |
| `<!-- wp:video -->` | ブロックコメントは削除。許可されない動画タグは残りません。 |
| `<!-- wp:audio -->` | ブロックコメントは削除。許可されない音声タグは残りません。 |
| `<!-- wp:file -->` | ブロックコメントは削除。許可されたリンクだけ残る場合があります。 |
| `<!-- wp:gallery -->` | ブロックコメントは削除。許可された画像だけ残る場合があります。 |
| `<!-- wp:media-text -->` | ブロックコメントは削除。許可HTMLだけ残る。 |
| `<!-- wp:columns -->` / `<!-- wp:column -->` | ブロックコメントは削除。許可HTMLだけ残る。 |
| `<!-- wp:buttons -->` / `<!-- wp:button -->` | ブロックコメントは削除。許可HTMLだけ残る。 |
| `<!-- wp:spacer -->` | ブロックコメントは削除。HTML部分が許可されなければ残りません。 |

## 注意

このファイルは、現在の実装に基づくメモです。  
将来、`middle` と `high-security` で安全化ルールを分ける場合は、この表も更新してください。
