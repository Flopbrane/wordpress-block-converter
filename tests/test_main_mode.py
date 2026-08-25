"""main.pyの変換モードのテストです。"""
#########################
# Author: F.Kurokawa
# Description:
#
#########################
from __future__ import annotations

from pathlib import Path

from main import convert_file


def test_convert_file_applies_hi_security_mode(tmp_path: Path) -> None:
    """hi-securityのときだけ安全化フィルターを通すテストです。"""
    load_file_path = tmp_path / "sample.md"
    save_file_path = tmp_path / "sample_safe_wordpress.html"
    load_file_path.write_text(
        "# タイトル\n\nhttps://www.youtube.com/watch?v=abc",
        encoding="utf-8",
    )

    convert_file(load_file_path, save_file_path, mode="hi-security")

    save_file = save_file_path.read_text(encoding="utf-8")
    assert "<!-- wp:embed" not in save_file
    assert "<h2>タイトル</h2>" in save_file
    assert '<a href="https://www.youtube.com/watch?v=abc">' in save_file
