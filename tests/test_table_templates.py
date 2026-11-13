"""テーブル出力テンプレートと標準保存形のテストです。"""
from __future__ import annotations

import json
from pathlib import Path

from blocks.table import create_table_block_from_rows
from dictionaries import table_templates
from lint import lint_wp_html


def test_standard_table_matches_wordpress_fixed_layout_save_shape() -> None:
    """WordPress 7.1.3の既定fixed layoutとHTMLを対応させるテストです。"""
    save_file = create_table_block_from_rows(["項目"], [["内容"]])

    assert save_file == (
        "<!-- wp:table -->\n"
        '<figure class="wp-block-table"><table class="has-fixed-layout">'
        "<thead><tr><th>項目</th></tr></thead>"
        "<tbody><tr><td>内容</td></tr></tbody>"
        "</table></figure>\n"
        "<!-- /wp:table -->"
    )
    assert lint_wp_html(save_file) == []


def test_header_only_table_does_not_emit_empty_tbody() -> None:
    """コアsaveが作らない空tbodyを出力しないテストです。"""
    save_file = create_table_block_from_rows(["項目"], [])

    assert "<thead>" in save_file
    assert "<tbody>" not in save_file


def test_table_template_json_has_required_output_sections() -> None:
    """UTF-8辞書が通常実行で読み込め、必要項目を持つテストです。"""
    load_file = table_templates.load_table_templates()

    assert load_file["wordpress_core_version"] == "7.1.3"
    assert load_file["standard_table"]["table_open"] == (
        '<table class="has-fixed-layout">'
    )
    assert load_file["standard_table"]["table_open_auto_layout"] == "<table>"
    assert load_file["custom_html"]["block_open"] == "<!-- wp:html -->"


def test_table_output_uses_editable_json_template(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """外形変更がPython修正ではなくJSON差し替えで反映されるテストです。"""
    load_file = json.loads(
        table_templates.TABLE_TEMPLATE_PATH.read_text(encoding="utf-8")
    )
    load_file["standard_table"]["figure_open"] = (
        '<figure class="wp-block-table test-template">'
    )
    load_file_path = tmp_path / "table_block_templates.json"
    load_file_path.write_text(
        json.dumps(load_file, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    monkeypatch.setattr(table_templates, "TABLE_TEMPLATE_PATH", load_file_path)
    table_templates.load_table_templates.cache_clear()
    try:
        save_file = create_table_block_from_rows(["項目"], [["内容"]])
    finally:
        table_templates.load_table_templates.cache_clear()

    assert '<figure class="wp-block-table test-template">' in save_file


def test_pyinstaller_spec_packages_table_template_dictionary() -> None:
    """配布版にもテーブル辞書を同梱する設定を確認するテストです。"""
    spec_text = Path("wp-converter.spec").read_text(encoding="utf-8")

    assert "dictionaries/table_block_templates.json" in spec_text
