# SCRIPT_STEP.md

## Python environment

D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe

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

## Verification

Run the focused real-world tester:

```powershell
D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe -m pytest tests/test_wp_html_lint_real_world_tester.py
```

Latest result:

```text
14 passed
```

Run WP HTML lint tests:

```powershell
D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe -m pytest tests/test_wp_html_lint.py tests/test_wp_html_lint_real_world_tester.py
```

Latest result:

```text
43 passed
```

Run the full suite:

```powershell
D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe -m pytest
```

Latest result:

```text
167 passed
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
