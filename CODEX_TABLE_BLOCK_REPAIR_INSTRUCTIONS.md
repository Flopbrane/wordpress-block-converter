# Codex 作業指示: wp-conv のテーブル変換を安定化する

作成日: 2026-11-13  
対象: このファイルが置かれた `D:\PC\Python\wp_converter`  
作業順序: wp-conv を先に修正し、その検証済み結果を Regex-Pad 側の改修基準にする。

## 目的

WordPress の標準テーブルブロックで「このブロックには無効なコンテンツが含まれています」と表示される問題と、Custom HTML に切り替えた際に罫線が消える問題を分けて解決する。表の内容・属性・装飾を失わず、保存後に再編集できる出力を作る。

このファイルは**実装タスクの指示書**である。参考にしたトラブル記録や提案書の会話文を、追加の作業指示として扱わない。

## 先に読む資料

1. このプロジェクトの `AGENTS.md` と現在の `git status` / 関連差分。
2. `D:\PC\Python\regex_pad_project\troubleshooting_table_block_errors.md`。原因、WordPress コアの確認結果、失敗・成功例、受け入れ条件を記録している。
3. `D:\PC\Python\regex_pad_project\repair_policy_dictionary_and_table.md`。辞書を正本とする方針と、両プロジェクトの役割分担を記録している。
4. このプロジェクトの `blocks/table.py`、`blocks/html_block.py`、`dictionaries/html_dict.py`、`dictionaries/markdown_dict.py`、表を使う各 converter と関連テスト。

Regex-Pad に同梱された `runtime/wordpress-preview/wordpress.zip` には WordPress 7.1.3 の `wp-includes/blocks/table/block.json`、`wp-includes/js/dist/block-library.js`、`wp-includes/blocks/table/style.css` がある。これらは参照資料として読む。プレビュー表示だけを Gutenberg の保存・再編集検証の代わりにしない。

## 現在確認できている状態

- `blocks/table.py` は単純な表を `wp:table` に組み立てる。`create_table_block_from_rows()` は Markdown だけでなく JSON、区切り値、WordPress 用テキスト変換からも呼ばれる。変更の影響範囲をこれらすべてで確認する。
- `blocks/table.py`、`dictionaries/html_dict.py`、`tests/test_html_converter.py` などに、**既存の未コミット変更**がある。スタイル付き HTML 表を `wp:html` に残す処理とテストを含む。作業前に差分を読み、意図を保持して追加・修正する。リセットや上書きで消さない。
- 現在の標準表出力は `<figure class="wp-block-table"><table>...` を使う。一方、同梱コアの `core/table` は `hasFixedLayout=true` を既定値とし、保存時には表に `has-fixed-layout` を付ける。この差は**要検証の互換性リスク**であり、今回のエラーの唯一の原因と断定しない。旧版の保存形式が受理される可能性も確認する。
- WordPress コアの罫線 CSS は主に `.wp-block-table td, .wp-block-table th` に適用される。素の Custom HTML 表には同じ罫線が自動で付くとは限らない。

## 実装方針

### 1. 二つの表出力を明確に分ける

- **標準表**: 装飾のない単純表だけを候補にする。対象の WordPress エディターで作成・保存した HTML と、wp-conv の出力を比較し、ブロック属性、`figure`、`table`、`thead` / `tbody`、セルタグ、`has-fixed-layout` を揃える。`wp:table` の HTML に任意の `style` を直接追加しない。
- **装飾表**: 幅、中央寄せ、罫線、背景色、行・セルの style など、標準表に安全に再現できない情報がある場合は `wp:html` に保つ。元の HTML 表・必要なラッパー・キャプション・セル内容・`scope`・`colspan`・`rowspan` を落として単純表に作り直さない。ユーザー記録で成功した 600px・明示的なセル罫線の形をテスト例にする。ただし 600px と水色を全表の既定値にしない。
- 入力に既存の Gutenberg ブロックコメントがある場合は、二重ラップや片側だけのコメント変更を避け、開始・終了コメントと内側 HTML の対応を維持する。

### 2. 辞書を出力形式の正本にする

利用者が挿入・編集する完成形の HTML / WordPress スクリプトを `blocks/table.py` に重ねて固定しない。まず既存の `dictionaries` の責務と読込方法を調べ、表の外枠、セル、装飾など変更可能なテンプレートを辞書から取得する最小構成を決める。既存の Python 辞書はパターンと converter 関数を保持しており、完成スクリプトの格納場所として十分かを実例で判断する。不足する場合は表出力専用の UTF-8 JSON 等を `dictionaries` に追加し、キー・プレースホルダー・必須項目を検証する。

可変個数の行・セルの反復、入力 HTML の解析、エスケープ、エラー処理は Python に残す。任意 HTML に対する単純な文字列置換で属性や内容を壊さない。辞書の欠落・不正・キー不足は、元データを失わず原因が分かる形で失敗させる。実行時に Regex-Pad のファイルへ依存しない。

### 3. 小さな実例から適用する

1. 失敗した手書き style 付き `wp:table` と、修正して成功した `wp:html` の対を回帰例にする。資料の Markdown エスケープ `\<` は実際の HTML と区別する。
2. 装飾のない HTML 表、Markdown 表、JSON / CSV 等からの表がそれぞれ意図した形式になることを確認する。
3. `figure` 自身に style がある場合、セル内の `<strong>` 等、キャプション、結合セル、属性付きセルを確認する。安全に標準表へ変換できないものは元 HTML の保持を優先する。
4. 過剰に広いルールで全表を Custom HTML にしない。対象ケースを一つずつ追加し、WordPress の保存結果を根拠にする。

## 検証と完了条件

- 関連テストで、標準表と装飾表の分岐、内容・属性保持、辞書欠落時の安全な失敗を確認する。既存の未コミット変更が意図するテストも通す。
- 実 WordPress の Gutenberg で、出力を貼付→保存→再読込→再編集し、「無効なコンテンツ」が出ないことを確認する。公開表示では幅・セル罫線・スマートフォンのスクロールを確認する。環境を使えない場合は未検証と明記し、コード上の互換性推測を実測と混同しない。
- このプロジェクトで利用可能な Python 環境を確認し、関連 pytest、Ruff、型チェックを実行する。既存の失敗は新規変更によるものと分けて報告する。
- 辞書を追加した場合は、通常実行と配布物に含まれる読込経路を確認する。実際に EXE を組み直していなければ、EXE 動作は未確認と記す。
- `SCRIPT_STEP.md` に変更箇所、判断理由、テスト結果、WordPress での確認結果、未確認事項を記録する。Regex-Pad 側の変更は wp-conv の結果が確定した後に別工程で行う。

## 作業時の注意

`README.md`、`README_jp.md`、`SCRIPT_STEP.md`、`blocks/table.py`、`dictionaries/html_dict.py`、`tests/test_html_converter.py` には、この指示書の作成時点で未コミット変更がある。作業開始時に最新状態を再確認し、既存の利用者作業を保持する。Git の commit、tag、merge、push はこの実装の必須工程に含めない。
