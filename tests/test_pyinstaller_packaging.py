"""PyInstallerの辞書収録設定を確認するテストです。"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_spec_bundles_all_runtime_json_files() -> None:
    spec_text = (PROJECT_ROOT / "wp-converter.spec").read_text(encoding="utf-8")

    for relative_path in (
        "dictionaries/table_block_templates.json",
        "dictionaries/lint_reference.json",
        "correct_data.json",
    ):
        assert relative_path in spec_text
    assert "contents_directory='_internal'" in spec_text


def test_build_script_verifies_bundled_json_and_executable() -> None:
    build_script = (PROJECT_ROOT / "build.ps1").read_text(encoding="utf-8")

    for required_text in (
        "table_block_templates.json",
        "lint_reference.json",
        "correct_data.json",
        "ConvertFrom-Json",
        "Get-FileHash",
        "wp-converter.exe",
        "WP_CONVERTER_PYTHON",
        "venv_wp_conv312",
    ):
        assert required_text in build_script


def test_runtime_json_files_are_valid() -> None:
    import json

    for relative_path in (
        Path("dictionaries/table_block_templates.json"),
        Path("dictionaries/lint_reference.json"),
        Path("correct_data.json"),
    ):
        load_file_path = PROJECT_ROOT / relative_path
        json.loads(load_file_path.read_text(encoding="utf-8-sig"))


def test_development_requirements_include_pyinstaller() -> None:
    requirements = (PROJECT_ROOT / "requestments_dev.txt").read_text(encoding="utf-8")

    assert "pyinstaller==6.22.2" in requirements.casefold()
