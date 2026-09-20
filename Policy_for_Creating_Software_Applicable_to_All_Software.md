# Policy_for_Creating_Software (Applicable_to_All Software)

## 目的

この文書は、事業所PCや個人PCで配布・運用するPython製ソフトウェアについて、できるだけ「どこでも置ける、ワンフォルダ運用」に近づけるための共通方針を定める。

対象は、Python実行環境、Pythonモジュール、AIモデル、学習済みデータ、キャッシュ、PyInstallerによるexe化、削除時の安全確認、配布用READMEを含む。

最重要方針は以下の通り。

1. 既存のPython環境、既存のAIモデル、既存の学習済みデータを壊さない。
2. 本ソフトが追加したものだけを記録し、削除対象にする。
3. 可能な限り、実行ファイル、venv、modules、models、cache、logs、README、cleanerを同一のMyAppフォルダ配下にまとめる。
4. 削除処理は必ずdry-runを先に行い、確認後に実行する。
5. GitHubリポジトリ用READMEとは別に、exe配布フォルダ用READMEを必ず用意する。

## 基本フォルダ構成

配布用フォルダは、原則として以下の構成を目標にする。

```text
MyApp/
  MyApp.exe
  module_cleaner.exe
  readme.txt
  readme_jp.txt
  LICENSE.txt

  app/
    settings/
    resources/

  runtime/
    python/
    venv/

  modules/
    site-packages/
    wheels/

  models/
    huggingface/
    torch/
    ultralytics/
    custom/

  cache/
    huggingface/
    torch/
    ultralytics/
    app_cache/

  data/
    input/
    output/
    temp/

  logs/
    app.log
    install.log
    cleaner.log

  install_records/
    pre_install_module.json
    after_install_module.json
    install_diff.json
    cleaner_report.json
```

この構成は絶対条件ではないが、新規ソフトでは可能な限りこの構成に寄せる。

## Pythonとvenvの方針

Python本体やvenvを使う場合は、可能な限りMyAppフォルダ配下に隔離する。

推奨配置は以下。

```text
MyApp/runtime/python/
MyApp/runtime/venv/
```

既存PCにPythonが入っている場合でも、原則として既存Pythonを勝手に変更しない。

特に禁止すること。

1. システムPythonへ勝手にpip installしない。
2. ユーザーの既存venvへ勝手にpip installしない。
3. PATHを恒久的に変更しない。
4. 既存Pythonのsite-packagesを削除しない。

やむを得ず既存Pythonを使う場合は、実行前に確認を表示し、ログに記録する。

## Pythonモジュールのインストール先

Pythonモジュールは、原則としてMyApp専用venv内にインストールする。

推奨。

```text
MyApp/runtime/venv/Lib/site-packages/
```

または、アプリ専用のモジュール保存先を用意する。

```text
MyApp/modules/site-packages/
```

pip install時は、可能な限り以下を満たす。

1. requirements.txtまたはrequirements.lock.txtを使用する。
2. pip freezeの結果をinstall_recordsへ保存する。
3. インストール前後の差分をJSONへ保存する。
4. pip cacheの保存先をMyApp/cache配下に寄せられる場合は寄せる。

例。

```powershell
set PIP_CACHE_DIR=%~dp0cache\pip
python -m pip install -r requirements.txt
```

## AIモデル・学習済みデータ・キャッシュの保存先

AIモデル、学習済みデータ、推論用キャッシュは、可能な限りMyApp配下に保存する。

環境変数で保存先を指定できるライブラリでは、MyApp配下を明示する。

例。

```powershell
set HF_HOME=%~dp0cache\huggingface
set TRANSFORMERS_CACHE=%~dp0cache\huggingface\transformers
set TORCH_HOME=%~dp0cache\torch
set ULTRALYTICS_SETTINGS=%~dp0cache\ultralytics\settings.json
```

保存先の基本方針。

| 種類 | 推奨保存先 |
|---|---|
| Hugging Faceモデル | `MyApp/models/huggingface/` または `MyApp/cache/huggingface/` |
| torch cache | `MyApp/cache/torch/` |
| Ultralytics / YOLO | `MyApp/models/ultralytics/` |
| 独自学習済みデータ | `MyApp/models/custom/` |
| 一時ファイル | `MyApp/data/temp/` |
| 出力ファイル | `MyApp/data/output/` |

既存のユーザーディレクトリにあるAIモデルやキャッシュは、原則として削除対象にしない。

## インストール前スナップショット

初回起動またはinstall_module.py実行時に、インストール前の状態を記録する。

作成ファイル。

```text
MyApp/install_records/pre_install_module.json
```

記録対象。

1. 検出されたPython本体のパスとバージョン
2. 検出されたvenv
3. pipパッケージ一覧
4. AIモデル保存先候補
5. 学習済みデータらしいファイル
6. 大容量ファイル
7. Hugging Face、torch、ultralyticsなどのキャッシュ場所
8. MyApp配下に既に存在していたファイル

pre_install_module.jsonに存在していたものは、原則として削除しない。

## インストール後スナップショット

モジュール、AIモデル、学習済みデータのインストール後に、インストール後の状態を記録する。

作成ファイル。

```text
MyApp/install_records/after_install_module.json
```

記録対象はpre_install_module.jsonと同じにする。

その後、pre_install_module.jsonとafter_install_module.jsonを比較し、差分を作成する。

作成ファイル。

```text
MyApp/install_records/install_diff.json
```

install_diff.jsonには、後から増えたファイル、フォルダ、pipパッケージ、モデル、キャッシュのみを記録する。

## JSONに記録する情報

JSONには、最低限以下を記録する。

```json
{
  "schema_version": "1.0",
  "app_name": "MyApp",
  "created_at": "YYYY-MM-DDTHH:MM:SS",
  "computer_name": "",
  "user_name": "",
  "python_versions": [],
  "venvs": [],
  "pip_packages": [],
  "model_dirs": [],
  "cache_dirs": [],
  "files": []
}
```

ファイル単位では以下を記録する。

```json
{
  "path": "C:/path/to/file",
  "size_bytes": 0,
  "mtime": "YYYY-MM-DDTHH:MM:SS",
  "kind": "model | module | cache | data | config | unknown",
  "source": "pip | huggingface | torch | ultralytics | app | unknown",
  "owned_by_this_app": false,
  "delete_candidate": false
}
```

可能であればsha256も記録する。ただし、大容量モデルでは処理時間が長くなるため、初期版では省略してよい。

## cleaner_for_delete.py / module_cleaner.pyの方針

削除用ツールは、原則としてmodule_cleaner.pyをソースにし、PyInstallerでmodule_cleaner.exeを作成する。

削除ツールは、いきなり削除してはいけない。

必須モード。

```powershell
module_cleaner.exe --scan
module_cleaner.exe --dry-run
module_cleaner.exe --clean
```

各モードの役割。

| モード | 役割 |
|---|---|
| `--scan` | 現在の状態を確認する |
| `--dry-run` | 削除候補だけを表示し、実際には削除しない |
| `--clean` | 確認後に削除する |

削除してよい候補。

1. pre_install_module.jsonに存在しない。
2. after_install_module.jsonまたはinstall_diff.jsonに存在する。
3. MyApp配下に存在する。
4. owned_by_this_appがtrueである。
5. 他のPython環境や他アプリの共有キャッシュではない。

削除してはいけない候補。

1. pre_install_module.jsonに存在していたもの。
2. ユーザーの既存Python本体。
3. ユーザーの既存venv。
4. ユーザーの既存site-packages。
5. ユーザーディレクトリ配下の共有AIモデル。
6. 作成日時や所有判定が不明なもの。
7. MyApp外にあり、他ソフトと共用されている可能性があるもの。

削除実行前には、必ず削除対象一覧を表示し、ユーザー確認を求める。

## 削除順序

削除時は、以下の順序を推奨する。

1. 起動中のMyApp.exeを終了する。
2. module_cleaner.exeを起動する。
3. `--scan`で現在状態を確認する。
4. `--dry-run`で削除候補を確認する。
5. ログと削除候補を保存する。
6. ユーザー確認後、`--clean`を実行する。
7. AIモデル、学習済みデータ、キャッシュを削除する。
8. venvまたは専用modulesを削除する。
9. 一時ファイル、ログ、設定ファイルを必要に応じて削除する。
10. 最後にMyAppフォルダを手動で削除する。

module_cleaner.exe自身は実行中に削除できないため、最後にユーザーがMyAppフォルダごと削除する。

## PyInstallerの方針

PyInstallerでは、本体exeとmodule_cleaner.exeを同時に作成できるようにする。

推奨する作成物。

```text
dist/MyApp/MyApp.exe
dist/MyApp/module_cleaner.exe
dist/MyApp/readme.txt
dist/MyApp/readme_jp.txt
dist/MyApp/LICENSE.txt
```

単純なビルドでは、以下のように個別に作成してもよい。

```powershell
pyinstaller --onefile main.py --name MyApp
pyinstaller --onefile module_cleaner.py --name module_cleaner
```

ただし、配布用には.specファイルでまとめることを推奨する。

specファイルでは、少なくとも以下を含める。

1. MyApp.exeの設定
2. module_cleaner.exeの設定
3. resourcesの同梱
4. readme.txtの同梱
5. readme_jp.txtの同梱
6. LICENSE.txtの同梱
7. 必要なモデルや設定ファイルの同梱
8. hiddenimportsの明示

## .specファイルの設計方針

.specファイルは、配布先フォルダをMyAppに統一する。

目標。

```text
dist/MyApp/
  MyApp.exe
  module_cleaner.exe
  readme.txt
  readme_jp.txt
  LICENSE.txt
  app/
  models/
  cache/
  install_records/
```

PyInstallerのonefileは配布が簡単だが、起動時に一時展開が発生する。

AIモデルや大容量データを扱う場合は、onefileよりonedirの方が安定することがある。

基本判断。

| 条件 | 推奨 |
|---|---|
| 小さいGUIツール | onefileでも可 |
| AIモデル同梱 | onedir推奨 |
| 外部データ多数 | onedir推奨 |
| 削除管理を重視 | onedir推奨 |

## READMEの方針

GitHub用READMEとは別に、exe配布フォルダには以下を用意する。

```text
readme.txt
readme_jp.txt
```

readme.txtは簡潔な英語または環境依存の少ない説明にする。

readme_jp.txtは日本語で、利用者向けにわかりやすく書く。

readme_jp.txtに必ず書く内容。

1. ソフト名
2. ソフトの目的
3. 起動方法
4. 使用する外部モジュール
5. 使用するAIモデル、学習済みデータ
6. 保存される可能性があるフォルダ
7. 削除時に使うソフト
8. 削除順序
9. 削除してよいもの、削除してはいけないもの
10. ライセンス
11. 免責事項

削除説明では、以下を明記する。

```text
削除する場合は、先にMyApp.exeを終了してください。
次にmodule_cleaner.exeを起動し、削除候補を確認してください。
問題がなければcleanを実行してください。
最後にMyAppフォルダを削除してください。
```

## ライセンス表記

配布フォルダには、ライセンス情報を必ず含める。

```text
LICENSE.txt
licenses/
```

外部モジュールを使用している場合は、可能な範囲でライセンス一覧を出力する。

推奨。

```powershell
pip-licenses --format=plain-vertical > licenses/python_modules_licenses.txt
```

pip-licensesを使わない場合でも、requirements.txtと主要ライブラリ名をreadme_jp.txtへ記載する。

AIモデルや学習済みデータを使用する場合は、そのモデルのライセンス、配布条件、再配布可否を確認する。

再配布不可のモデルは、exeフォルダに同梱しない。

## GitHubリポジトリとexe配布フォルダの違い

GitHubリポジトリは開発者向け、exe配布フォルダは利用者向けとして分ける。

GitHub側。

```text
README.md
README_jp.md
requirements.txt
src/
tests/
docs/
```

exe配布側。

```text
MyApp.exe
module_cleaner.exe
readme.txt
readme_jp.txt
LICENSE.txt
models/
cache/
install_records/
```

GitHub用READMEには開発方法、ビルド方法、テスト方法を書く。

exe配布用READMEには起動方法、削除方法、注意事項を書く。

## Codexへの実装指示方針

Codexがこの方針に従って作業する場合、以下を優先する。

1. 既存ファイル構成を確認する。
2. 既存のvenv、requirements、PyInstaller specを確認する。
3. MyApp配布フォルダ案を作成する。
4. install_module.pyまたはmodule_installer.pyを作成する。
5. pre_install_module.jsonを作成できるようにする。
6. after_install_module.jsonを作成できるようにする。
7. install_diff.jsonを作成できるようにする。
8. module_cleaner.pyをdry-run優先で作成する。
9. PyInstaller specで本体exeとcleaner exeを作成する。
10. readme.txt、readme_jp.txt、LICENSE.txtを配布フォルダへ含める。
11. 実際の削除処理は、安全確認ができるまで自動化しすぎない。

## 絶対に守るルール

1. pre_install_module.jsonに存在していたものは、原則として削除しない。
2. MyApp外のファイルを削除する場合は、必ずユーザー確認を要求する。
3. 削除前にdry-runを必ず実行できるようにする。
4. 削除ログを必ず残す。
5. 他のPython環境を壊さない。
6. 既存AIモデルや既存学習済みデータを壊さない。
7. ライセンス不明のAIモデルを同梱しない。
8. 事業所PCでは、管理者権限を前提にしない。
9. Windows環境を主対象とし、パス区切りや文字コードに注意する。
10. 初心者がreadme_jp.txtだけで削除手順を理解できるようにする。

## 将来拡張

将来的には、以下を検討する。

1. GUI版module_cleaner.exe
2. 削除候補のチェックボックス表示
3. 削除前バックアップ
4. install_recordsの比較ビュー
5. モデル容量の可視化
6. 使用中ファイルの検出
7. 他venvからの参照チェック
8. アンインストーラー風UI

ただし、初期版ではCLI版で十分とする。

## まとめ

本方針の目的は、Python製AIソフトを安全に配布し、利用後に安全に削除できるようにすることである。

理想は完全なワンフォルダ運用だが、AIモデルやPythonモジュールは外部キャッシュを使うことがある。

そのため、インストール前後の状態をJSONに記録し、本ソフトが追加したものだけを削除候補にする。

削除よりも、まず記録、比較、dry-runを優先する。

この方針により、事業所PCでも個人PCでも、既存環境を壊しにくい安全な配布・削除運用を目指す。
