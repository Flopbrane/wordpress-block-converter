wp-converter 配布フォルダ用 README
=================================

ソフト名:
wp-converter

目的:
平文、Markdown、HTMLをWordPress Gutenberg向けHTMLへ変換するためのツールです。

起動方法:
このフォルダ内の wp-converter.exe を実行してください。

ワンフォルダ運用方針:
この配布フォルダでは、可能な限り必要なファイルを wp-converter フォルダ内にまとめます。
Pythonモジュールは module_installer.py により runtime/venv へ入れる方針です。
キャッシュ、一時ファイル、ログ、インストール記録は以下へ保存します。

- cache/
- data/
- logs/
- install_records/
- runtime/venv/

使用する可能性がある外部モジュール:
requirements系ファイルに記載されたPythonモジュールを使用します。
このソフト単体ではAIモデルや学習済みデータの同梱を前提にしていません。

削除時に使うソフト:
module_cleaner.exe

削除順序:
1. wp-converter.exe を終了してください。
2. module_cleaner.exe --scan を実行し、現在状態を確認してください。
3. module_cleaner.exe --dry-run を実行し、削除候補を確認してください。
4. 問題がなければ module_cleaner.exe --clean を実行してください。
5. 最後に wp-converter フォルダを手動で削除してください。

削除してよいもの:
- install_records/install_diff.json に記録された、このアプリが追加したファイル
- wp-converter フォルダ内の cache、runtime、logs、data など

削除してはいけないもの:
- このフォルダ外にあるPython本体
- このフォルダ外にある既存venv
- ユーザーが別用途で使っているsite-packages
- 共有キャッシュや既存AIモデル
- 記録上、このアプリが作成したと確認できないファイル

ライセンス:
LICENSE.txt を確認してください。
外部モジュールのライセンスは、requirements系ファイルおよび各配布元の条件を確認してください。

免責事項:
このソフトの使用、削除、変換結果によって発生した損害について、作者は責任を負いません。
重要なファイルは事前にバックアップしてください。
