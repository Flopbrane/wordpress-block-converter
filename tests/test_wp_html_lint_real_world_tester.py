"""実文章ベースでWP_HTML lintの各項目を動かすテスターです。

実行例:
    python -m pytest tests/test_wp_html_lint_real_world_tester.py
"""
from __future__ import annotations

import pytest

from lint import lint_css, lint_wp_html


REAL_WORLD_BAD_PARAGRAPH = """<!-- wp:paragraph -->
<p>("sample-theme/" のように、<strong>最後に「/」が付いているものはフォルダ</strong>です。<br>
フォルダは、ファイルを入れておく箱のようなものです。<br><br>

一方で、<strong>style.css や functions.php のように、</strong><br>
</p>
<!-- /wp:paragraph -->"""


REAL_WORLD_COMPACT_PARAGRAPH = """<!-- wp:paragraph -->
<p>("sample-theme/" のように、<strong>最後に「/」が付いているものはフォルダ</strong>です。<br>
フォルダは、ファイルを入れておく箱のようなものです。<br><br>一方で、<strong>style.css や functions.php のように、</strong><br></p>
<!-- /wp:paragraph -->"""


REAL_WORLD_SPLIT_PARAGRAPHS = """<!-- wp:paragraph -->
<p>("sample-theme/" のように、<strong>最後に「/」が付いているものはフォルダ</strong>です。<br>
フォルダは、ファイルを入れておく箱のようなものです。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>一方で、<strong>style.css や functions.php のように、最後に「.css」「.php」などが付いているものは単一ファイル</strong>です。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong>拡張子</strong>とは、<strong>ファイル名の最後に付く目印</strong>です。<br>
たとえば <code>.css</code> はCSSファイル、<code>.php</code> はPHPファイル、<code>.jpg</code> や <code>.png</code> は画像ファイルを表します。</p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p>PCを操作するうえで、拡張子という言葉は頻繁に使用されますので、<strong>この際に、覚えておいた方が、後々、便利</strong>です。</p>
<!-- /wp:paragraph -->"""


@pytest.mark.parametrize(
    ("case_name", "load_file", "expected_message"),
    [
        (
            "paragraph内部の空行",
            REAL_WORLD_BAD_PARAGRAPH,
            "paragraph ブロック内の <p> に空行があります",
        ),
        (
            "コアブロックの閉じ忘れ",
            "<!-- wp:paragraph -->\n<p>本文です。</p>\n",
            "wp:paragraph ブロックが閉じられていません",
        ),
        (
            "コアブロック名typo",
            "<!-- wp:paragaph -->\n<p>本文です。</p>\n<!-- /wp:paragaph -->",
            "wp:paragaph ブロックコメントは既知のコアブロック名ではありません",
        ),
        (
            "コアブロック内HTMLタグ閉じ忘れ",
            "<!-- wp:paragraph -->\n<p><strong>本文です</p>\n<!-- /wp:paragraph -->",
            "<strong> が閉じられていません",
        ),
        (
            "HTMLタグtypo",
            "<!-- wp:paragraph -->\n<p><strnog>本文です</strnog></p>\n<!-- /wp:paragraph -->",
            "<strnog> は既知のHTMLタグではありません",
        ),
        (
            "危険HTMLタグ",
            "<!-- wp:html -->\n<script>alert(1)</script>\n<!-- /wp:html -->",
            "<script> はmiddle / high-security modeでは危険扱いです",
        ),
        (
            "リンク属性不足",
            "<!-- wp:paragraph -->\n<p><a target=\"_blank\">公式サイト</a></p>\n<!-- /wp:paragraph -->",
            "<a> タグに href がありません",
        ),
        (
            "画像属性不足",
            "<!-- wp:image -->\n<figure class=\"wp-block-image\"><img src=\"https://example.com/a.jpg\"></figure>\n<!-- /wp:image -->",
            "<img> タグに alt がありません",
        ),
        (
            "非normal不安定コアブロック",
            "<!-- wp:embed -->\n<figure class=\"wp-block-embed\"><div>https://example.com</div></figure>\n<!-- /wp:embed -->",
            "core/embed は事業所WPや高セキュリティ環境で表示されないことがあります",
        ),
        (
            "非表示class",
            "<!-- wp:paragraph -->\n<p class=\"hidden-post\">本文です。</p>\n<!-- /wp:paragraph -->",
            "hidden-post",
        ),
        (
            "表示制限style",
            "<!-- wp:paragraph -->\n<p style=\"pointer-events:none\">本文です。</p>\n<!-- /wp:paragraph -->",
            "style に表示・操作を制限する指定があります",
        ),
    ],
)
def test_real_world_wp_html_lint_cases(
    case_name: str,
    load_file: str,
    expected_message: str,
) -> None:
    """実文章に近いWP_HTMLで、各lint項目が実際に発火することを確認します。"""
    issues = lint_wp_html(load_file, mode="high-security")

    assert any(expected_message in issue.message for issue in issues), case_name


@pytest.mark.parametrize(
    ("case_name", "load_file"),
    [
        ("空行を詰めたparagraph", REAL_WORLD_COMPACT_PARAGRAPH),
        ("段落ブロック分割", REAL_WORLD_SPLIT_PARAGRAPHS),
    ],
)
def test_real_world_safe_paragraph_patterns_pass(
    case_name: str,
    load_file: str,
) -> None:
    """実文章の安全版で、paragraph内部空行エラーが出ないことを確認します。"""
    issues = lint_wp_html(load_file, mode="normal")

    assert not any("paragraph ブロック内の <p> に空行があります" in issue.message for issue in issues), case_name
    assert issues == []


def test_real_world_css_lint_case() -> None:
    """CSSファイルモードの実働項目も同じテスターで確認します。"""
    load_file = (
        ".hidden-post { display: none; }\n"
        ".button-link { pointer-events: none; }\n"
        ".article-body { overflow: hidden; }\n"
    )

    issues = lint_css(load_file)

    assert any("display:none" in issue.message for issue in issues)
    assert any("pointer-events:none" in issue.message for issue in issues)
    assert any("overflow:hidden" in issue.message for issue in issues)
