# SCRIPT_STEP.md

## Python environment

D:\Dev\venvs\venv_wp_conv312\Scripts\python.exe

## Development Steps

This file records implementation notes and recommended next steps for `wp_converter`.

## Completed

1. Conversion modes
   - `normal`, `middle`, and `high-security` modes are available.
   - Compatibility aliases remain available: `office` maps to `middle`, and `hi-security` maps to `high-security`.
   - Non-normal modes are used for office WordPress and high-restriction environments.

2. WP HTML lint mode support
   - `lint.py` accepts `--mode`.
   - `normal` keeps structural checks.
   - `middle` / `office` / `high-security` / `hi-security` also warn about restricted-environment display risks.

3. Non-normal WordPress core block warnings
   - Warns about blocks that may be hidden, disabled, or unstable in restricted WordPress environments.
   - Covered examples include `core/embed`, `core/html`, `core/shortcode`, `core/video`, `core/audio`, `core/file`, `core/gallery`, `core/media-text`, `core/columns`, `core/column`, `core/buttons`, `core/button`, and `core/spacer`.

4. CSS-derived display restriction warnings in WP HTML
   - Warns about unstable classes found during the CSS audit.
   - Covered examples include `hidden-post`, `samearea-otheroffice`, `blog-officelist`, `modal`, `swiper`, `visually-hidden`, `screen-reader`, and `sr-only`.
   - Warns about inline display/interaction restrictions such as `display:none`, `visibility:hidden`, `opacity:0`, `pointer-events:none`, `user-select:none`, and `overflow:hidden`.

5. CSS file lint mode
   - `lint.py` supports `--input-type auto|wp-html|css`.
   - `.css` files are detected automatically as CSS lint targets.
   - CSS lint checks display removal, interaction blocking, unstable layout rules, external dependencies, and brace mismatch.
   - Covered examples include `display:none`, `visibility:hidden`, `content-visibility:hidden`, `opacity:0`, `pointer-events:none`, `user-select:none`, `overflow:hidden`, `clip`, `clip-path`, `position:fixed`, large `z-index`, `@import`, and external `url(https://...)`.

6. HTML / WP HTML common strict lint
   - Plain HTML and WordPress block HTML share strict HTML tag checks.
   - Detects unclosed HTML tags and nesting mistakes.
   - Detects tag typos such as `<strnog>`, `<spna>`, and similar misspellings.
   - Detects unknown WordPress core block names such as `wp:paragaph`.
   - Accepts `wp:core/paragraph` style core-prefixed block comments.

7. Gutenberg paragraph stability lint
   - Detects blank lines inside `<p>...</p>` in `wp:paragraph`.
   - This guards against Gutenberg treating a paragraph block as too complex and moving it to a Custom HTML block.
   - Recommended fixes are to remove human-facing blank lines inside `<p>`, compact with `<br><br>`, or split content into multiple `wp:paragraph` blocks.

8. Text editor lint integration
   - `text_editor` has `Tools > lintチェック`.
   - Lint issues are highlighted with Tk text tags.
   - Hovering a highlighted line shows a warning and fix hint.
   - `.css` files use CSS lint.
   - `.wp_html`, `.html`, `.htm`, or content containing `<!-- wp:` use WordPress HTML lint.

9. Real-world lint tester
   - Added `tests/test_wp_html_lint_real_world_tester.py`.
   - Uses the actual paragraph sample where blank lines inside `<p>` caused Gutenberg instability.
   - Confirms the bad sample fails.
   - Confirms the compact paragraph and split-paragraph versions pass.
   - Also exercises core block closing, core block name typo, HTML tag typo, unclosed HTML tags, dangerous HTML, link/image attributes, non-normal unstable blocks, display restriction classes/styles, and CSS lint.

10. Documentation
    - Updated `README.md` and `README_jp.md`.
    - Documented WP HTML / CSS lint usage.
    - Documented the real-world lint tester command.
    - Documented the Gutenberg paragraph blank-line warning.

11. Warning: styled div articles in office WordPress
    - Temporary rule: when HTML input contains a `div` with decoration/layout styles such as `border`, `padding`, `margin`, `background`, `background-color`, `max-width`, `min-width`, `width`, `border-radius`, `display`, `grid-*`, or `flex-*`, keep the whole parent `div` and its children as one `wp:html` block.
    - Do not split the inner `p`, `ul`, `ol`, or nested `div` into separate Gutenberg blocks in this case.
    - Existing `wp:html` input must not be wrapped in another `wp:html` block.
    - Reason: office WordPress may restrict styled frame articles, and preserving the original HTML is safer than converting it to `wp:group` or partial native blocks.
    - This is a temporary safety rule. Add real saved test patterns after checking the office WordPress editor.

12. Warning lint for styled div articles and CSS brace problems
    - In `middle` / `office` / `high-security` / `hi-security` lint modes, styled `div` frame articles now warn that they are `wp:html` protection targets and need saved-output confirmation in office WordPress.
    - The converter regression tests include styled frame articles, nested `div`, and existing `wp:html` input to avoid accidental block splitting or double wrapping.
    - Protected styled `div` output removes inner Gutenberg comments such as `wp:paragraph` and `wp:list`; the `wp:html` block must contain ordinary HTML only.
    - WP-TXT frame markers such as `[囲い込み]`, `[注意]`, and `[補足]` keep paragraphs and list-like lines as text with `<br>` / `<br><br>` inside one `wp:html` block.
    - CSS lint reports display/interaction restrictions and now distinguishes missing `}`, extra `}`, and unclosed `/* ... */` comments with line numbers.
    - WP HTML syntax breakage such as missing block end comments, missing `/`, mismatched blocks, malformed comments, and unclosed HTML tags is treated as `error`; display restrictions and office WordPress instability are treated as `warning`.

13. Warning: decorated HTML tables in office WordPress
    - Temporary rule: plain HTML tables without inline styling can be converted to `wp:table`.
    - If HTML input has `style=` on `table`, `thead`, `tbody`, `tr`, `th`, or `td`, keep the whole matched table as one `wp:html` block.
    - Reason: WordPress table core blocks can become unstable when colors, backgrounds, borders, or padding are applied at row, header-cell, or body-cell level.
    - For decorated tables, write background color directly on `td` / `th` rather than relying only on `tr`, then keep the result as Custom HTML.
    - This is a temporary safety rule. Add real saved table patterns after checking the office WordPress editor.

14. WordPress table block repair and dictionary-backed output
    - Confirmed the bundled WordPress 7.1.3 `core/table` metadata and save code: `hasFixedLayout` defaults to `true`, and saved HTML adds `has-fixed-layout` to the `table` element when it is enabled.
    - Standard table output now emits one synchronized shape: `<!-- wp:table -->`, `figure.wp-block-table`, and `table.has-fixed-layout`. Empty table sections are omitted instead of emitting an empty `tbody`.
    - Existing `{"hasFixedLayout":false}` input stays auto-layout with a classless `table`. Existing table blocks with unhandled core attributes are preserved unchanged instead of being rebuilt speculatively.
    - HTML tables with inline style, unsupported classes/attributes, mixed unsupported structure, or an outer `div` wrapper are kept as one `wp:html` block. Existing `wp:table` comments are removed before that fallback so the Custom HTML block does not contain nested Gutenberg comments.
    - Core-supported `scope`, `colspan`, `rowspan`, text alignment, inline rich text, `thead` / `tbody` / `tfoot`, and `figcaption` are retained in native table output.
    - Added `dictionaries/table_block_templates.json` plus its validated loader. The JSON owns block comments and table/section/row/cell/caption outlines; Python still owns parsing, escaping, row generation, and error handling.
    - Added the JSON dictionary to `wp-converter.spec` so source and distributed execution use the same template path.
    - WP HTML lint now detects fixed-layout/class mismatches and warns about direct row/cell style inside `wp:table`. Intentional `wp:html` tables are excluded from this warning.
    - Added regression coverage for HTML, Markdown, JSON, CSV/TSV/PSV, WP-TXT, existing Gutenberg comments, decorated 600px-style figures, wrappers, captions, rich cell content, span/scope attributes, Markdown-escaped HTML, template customization, and PyInstaller data inclusion.
    - Real Gutenberg paste, save, reload, and re-edit acceptance is still unverified. The bundled preview/core source confirms the expected save shape but is not a substitute for the editor workflow. A packaged EXE build and launch were not performed in this section.

15. Explicit HTML source conversion to WordPress block HTML
    - Root cause: `select_converter()` checked for existing `<!-- wp:... -->` content before checking the `.html` / `.htm` extension. An HTML source beginning with `<!-- wp:html -->` therefore selected `keep_existing_wordpress_html()` and bypassed `convert_html_to_gutenberg()` completely.
    - Added `HTML_SOURCE_EXTENSIONS` for `.html` and `.htm`, and made this explicit source format take priority over the existing-WordPress-content shortcut. `.wp_html` remains the output/converted format and still preserves existing blocks.
    - Added `convert_source_html_to_gutenberg()`. It removes existing Gutenberg block comments from explicit HTML source, extracts `<body>` when a complete HTML document is supplied, and then runs the normal HTML converter.
    - The normal HTML converter now wraps unsupported-only HTML in one `wp:html` block when no native block was produced. It no longer returns an empty result or relies on unwrapped source HTML for that case.
    - Added regressions at converter-selection, direct HTML conversion, body extraction, and real file I/O levels. Existing Markdown containing already-converted WordPress HTML and existing `.wp_html` behavior remain unchanged.
    - Focused HTML/file-selection/main tests: 55 passed.
    - Full pytest after this repair: 239 passed.
    - Ruff: All checks passed.
    - Targeted Pyright for `html_converter.py`, `file_checker.py`, and `main.py`: 0 errors, 0 warnings, 0 informations.
    - Real Gutenberg editor and packaged EXE acceptance remain unverified.

16. Markdown editing workflow for plain-text drafts
    - Changed the `.txt` helper-editor workflow from newly inserting PRE-WP custom markers to inserting standard Markdown syntax. Direct `.txt` conversion outside the editor remains unchanged.
    - Added separate `MARKDOWN_MARKERS` and retained `PREWP_MARKERS` plus the `MARKERS` compatibility alias. Markdown insertion supports headings, unordered and ordered lists, quotes, bold, inline/fenced code, links, images, pipe tables, and separators.
    - Multi-line heading, list, and quote selections are prefixed line by line. Ordered selections are numbered while blank lines remain blank.
    - Added editing-format switching. `.txt`, `.md`, `.markdown`, and a new untitled editor use Markdown menus and conversion. `.prewp_txt`, `.wp_txt`, and `.wptxt` retain the original marker menu, linter, and converter.
    - Saving an opened `.txt` uses a Markdown Save As dialog with `.md` as the default, preserving the original `.txt`. Existing Markdown files save normally.
    - Direct WordPress HTML export from a `.txt` or Markdown editing session now calls `convert_markdown_to_gutenberg()` explicitly. Legacy PRE-WP sessions continue to call `convert_wp_txt_to_gutenberg()`.
    - Added a narrow Markdown linter for unclosed fenced code, broken link/image closing parentheses, missing spaces after heading markers, and unpaired inline-code backticks. Markdown-looking text inside fenced code is ignored.
    - Added an editing-format label so the user can see `Markdown`, `PRE-WP (compatibility)`, or the existing format.
    - Focused editor/GUI/converter tests: 100 passed.
    - Full pytest: 257 passed.
    - Ruff: All checks passed.
    - Targeted Pyright: 0 errors, 0 warnings, 0 informations.
    - Full Pyright: 1 existing unresolved `pytest` import in `tests/test_wp_html_lint_real_world_tester.py`; no new error remains from this section.
    - Hidden GUI smoke test: Markdown mode label and selected-text heading insertion passed.
    - Physical GUI use, packaged EXE build/launch, and WordPress editor acceptance remain unverified.

17. Save Markdown before editor WordPress export
    - Changed Markdown-mode `WordPress HTMLへ変換して保存` into a serial two-save workflow: choose the Markdown path, save the source, then choose the `.wp_html` path and convert.
    - The converter reads the newly saved UTF-8 Markdown file instead of converting an unsaved editor buffer.
    - Cancelling the Markdown save stops the workflow before the WordPress HTML save dialog. Cancelling the later WordPress dialog leaves the Markdown source safely saved.
    - The intermediate Markdown save suppresses its standalone completion dialog; the final completion message lists both saved paths.
    - PRE-WP compatibility mode keeps its existing direct export behavior.
    - Focused Markdown-editor/GUI/lint tests: 21 passed.
    - Physical GUI use, packaged EXE build/launch, and WordPress editor acceptance remain unverified.

18. PyInstaller runtime-data completeness and verified build
    - Audited all runtime file reads. The required static JSON files are `dictionaries/table_block_templates.json`, `dictionaries/lint_reference.json`, and `correct_data.json`.
    - Updated `wp-converter.spec` to bundle all three files and fixed the one-directory contents folder as `_internal`.
    - Updated `build.ps1` to locate a Python interpreter that actually has PyInstaller. It supports `-PythonPath` and `WP_CONVERTER_PYTHON`, then checks the project `.venv`, `venv_wp_conv312`, and normal `python`.
    - Added pre-build source existence and JSON validation. Added post-build EXE existence, bundled JSON validation, and source/bundle SHA-256 equality checks.
    - `correct_data.json` is bundled as an internal fallback and copied beside the EXE as an editable portable file. An existing adjacent copy is held in memory and restored after rebuilding.
    - Added PyInstaller 6.22.2 to `requestments_dev.txt` and added packaging contract tests.
    - PowerShell AST parse: passed.
    - Focused packaging/table/lint/rewrite tests: 62 passed.
    - Full pytest: 262 passed.
    - Ruff: All checks passed.
    - Packaging-test Pyright: 0 errors, 0 warnings, 0 informations.
    - Actual `build.ps1` run: passed with PyInstaller 6.22.2 and Python 3.12.10.
    - Bundled JSON verification: 3 files passed syntax and SHA-256 checks.
    - Packaged EXE CLI smoke: passed for Markdown table to `wp_html`, exercising the bundled table template.
    - PyInstaller warnings contained conditional/optional platform modules; no required application module omission was identified.
    - Physical GUI operation and WordPress editor acceptance remain unverified.

## Verification

Run the focused real-world tester:

```powershell
D:\Dev\venvs\venv_wp_conv312\Scripts\python.exe -m pytest tests/test_wp_html_lint_real_world_tester.py
```

Latest result:

```text
14 passed
```

Run WP HTML lint tests:

```powershell
D:\Dev\venvs\venv_wp_conv312\Scripts\python.exe -m pytest tests/test_wp_html_lint.py tests/test_wp_html_lint_real_world_tester.py
```

Latest result:

```text
43 passed
```

Run the full suite:

```powershell
D:\Dev\venvs\venv_wp_conv312\Scripts\python.exe -m pytest
```

Latest result:

```text
217 passed
```

Section 14 validation:

```text
Focused table/converter/lint tests: 129 passed
Full pytest: 233 passed
Ruff: All checks passed
Targeted Pyright: 0 errors, 0 warnings, 0 informations
Full Pyright: 1 existing unresolved pytest import in test_wp_html_lint_real_world_tester.py
JSON syntax: passed for dictionaries/table_block_templates.json
Real Gutenberg editor: not run
Packaged EXE build/launch: not run
```

## Next Recommended Steps

1. Lint severity levels
   - Add explicit severity such as `error`, `warning`, and `info` to `LintIssue`.
   - Treat structural corruption as error and restricted-environment display risk as warning.

2. HTML parser context reporting
   - Include current WordPress block context in HTML tag errors.
   - Example: report that `<strong>` is unclosed inside `wp:paragraph`.

3. More Gutenberg stability rules
   - Warn about overly long single paragraph blocks.
   - Warn about repeated `<br><br>` in one `<p>`.
   - Consider recommending paragraph splitting when the content looks like multiple logical paragraphs.

4. Real-world tester expansion
   - Add samples from actual converted articles when new Gutenberg failures are found.
   - Keep each sample as a regression case before changing converter behavior.

5. Editor display improvements
   - Show lint issue count by severity.
   - Add a next/previous issue navigation command.
   - Consider a small lint results panel for long files.
