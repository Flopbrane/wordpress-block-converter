# WordPress Block Converter

Convert plain text, Markdown, and simple HTML files into WordPress Gutenberg-compatible HTML blocks.

This project is designed as a small beginner-friendly Python tool for preparing article drafts before pasting them into the WordPress block editor.

This tool is designed for users who prefer preparing stable WordPress block HTML outside the visual editor and pasting it into the code editor.

## Features

- Convert plain text paragraphs into WordPress paragraph blocks
- Convert marked plain text `.prewp_txt`, `.wp_txt`, and `.wptxt` files into headings, paragraphs, lists, quotes, code, tables, and images
- Convert Markdown headings, paragraphs, lists, quotes, code blocks, tables, separators, images, and shortcodes
- Convert simple HTML headings, paragraphs, lists, quotes, code blocks, tables, images, links, and shortcodes
- Convert CSV/SSV/TSV/PSV separated-value files into table blocks
- Convert JSON structure data into headings, paragraphs, lists, tables, and FAQ sections
- Convert YouTube, YouTube Shorts, TikTok, Vimeo, and other supported service URLs into WordPress embed blocks
- Convert direct media/file URLs into `image`, `video`, `audio`, or `file` blocks
- Keep common inline formatting such as links, bold, and italic text
- Insert a 24px spacer between plain text paragraphs
- Choose files with a simple GUI
- Run from the command line when needed
- Check converted WordPress block HTML with `wp_html_lint`
- Uses only the Python standard library

## Supported Input Files

| Format           | Extensions                                |
| ---------------- | ----------------------------------------- |
| Plain text       | `.txt`                                    |
| Marked plain text | `.prewp_txt`, `.wp_txt`, `.wptxt`       |
| Markdown         | `.md`, `.markdown`                        |
| HTML             | `.html`, `.htm`                           |
| Separated values | `.csv`, `.ssv`, `.tsv`, `.psv`, `.pipesv` |
| JSON             | `.json`                                   |

## Rules for Plain Text

For ordinary `.txt` files, the converter keeps the rules simple: blank lines become paragraph breaks. If you want to add headings, lists, quotes, code blocks, tables, links, or images before conversion, open the file in `text_editor` and add markers before converting. The marker rules are described in [HOW_TO_USE_FOR_PLAIN_TEXT.md](HOW_TO_USE_FOR_PLAIN_TEXT.md).

Save marked plain text as `.prewp_txt`. Existing `.wp_txt` and `.wptxt` files are still supported for compatibility. A plain `.txt` file is intentionally treated as paragraph-only text.

## Version Support

| Version | Support | Status |
| ------- | ------- | ------ |
| Ver.1.0 | Basic plain text, Markdown, and HTML conversion | Supported |
| Ver.1.1 | Embed URLs, image/video/audio/file URLs, and three conversion modes | Supported |
| Ver.1.2 | Convert CSV / SSV / TSV / PSV into table blocks | Supported |
| Ver.1.3 | Generate headings, paragraphs, lists, tables, and FAQ sections from JSON | Supported |
| Ver.1.4 | Markdown custom layout syntax for image rows, media-text sections, CTA, FAQ, and card layouts | In progress |
| Ver.1.5 | wp_html_lint for block comments, heading levels, tables, links, and images | Supported |
| Ver.1.6 | WP-TXT syntax for stable conversion from lightly marked plain text into headings, lists, quotes, code, tables, and images | Supported |

## Supported WordPress Blocks

| Content              | WordPress block        |
| -------------------- | ---------------------- |
| Paragraph            | `core/paragraph`       |
| Heading              | `core/heading`         |
| List                 | `core/list`            |
| Code                 | `core/code`            |
| Quote                | `core/quote`           |
| Spacer               | `core/spacer`          |
| Separator            | `core/separator`       |
| Table                | `core/table`           |
| Custom HTML          | `core/html`            |
| Image                | `core/image`           |
| Video file           | `core/video`           |
| Audio file           | `core/audio`           |
| Download file        | `core/file`            |
| Shortcode            | `core/shortcode`       |
| External service URL | `core/embed`           |

## Conversion Details

### Plain Text

- Blank lines split paragraphs.
- Line breaks inside a paragraph become `<br><br>`.
- A 24px spacer block is inserted between paragraphs.

### Marked Plain Text

Marked plain text is a lightly marked text format for writing WordPress articles more predictably than plain `.txt`. Use `.prewp_txt` for new files; `.wp_txt` and `.wptxt` remain supported.

The English markers below are recommended for new English-language drafts. Existing Japanese markers are still supported for backward compatibility.

| Syntax | Output |
|---|---|
| `[Heading:Heading text]` | h2 heading |
| `[Subheading:Subheading text]` | h3 heading |
| Blank line | Paragraph break |
| `- Item` or `* Item` | Unordered list |
| `1. Item` | Ordered list |
| `> Quote` | Quote |
| `---` | Separator |
| `[Spacer:50]` | 50px spacer |
| `[Link:Label|https://example.com/]` | Link |
| `[Image:https://example.com/image.jpg|Alt text]` | Image |
| `[Audio:https://example.com/audio.mp3]` | Audio block |
| `[Video:https://example.com/video.mp4]` | Video block |
| `[File:https://example.com/file.pdf]` | File block |
| `[Code]` to `[/Code]` | Code block |
| `[EmphasisCode]` to `[/EmphasisCode]` | Emphasized code block |
| `[List]` to `[/List]` | Explicit unordered list |
| `[OrderedList]` to `[/OrderedList]` | Explicit ordered list |
| `[Table]` to `[/Table]` | Table |
| `[HTML]` to `[/HTML]` | Raw HTML block |
| `[Box]` to `[/Box]` | Boxed content |
| `[Notice]` to `[/Notice]` | Notice box |
| `[Supplement]` to `[/Supplement]` | Supplement box |
| `[Steps]` to `[/Steps]` | Ordered steps |
| `[ImageRow:24px]` to `[/ImageRow]` | Row of images with a gap |

Example:

```text
[Heading:About WordPress]

WordPress is a system for creating websites and blogs.

[Subheading:What it can do]

- Write articles
- Insert images
- Create tables

See [Link:Official site|https://example.com/] for details.

[Image:https://example.com/image.jpg|Example image]

[Audio:https://example.com/audio.mp3]

[Video:https://example.com/video.mp4]

[File:https://example.com/manual.pdf]

[Code]
<p>This is a paragraph.</p>
[/Code]

[EmphasisCode]
functions.php
[/EmphasisCode]

[List]
Item 1
Item 2
Item 3
[/List]

[Table]
Item|Description
h2|Large section
[/Table]
```

### Markdown

Supported Markdown-style input includes:

- Headings: `#`, `##`, up to `######`
- Paragraphs
- Unordered lists: `-`, `*`, `+`
- Ordered lists: `1.` or `1)`
- Code fences: triple backticks
- Inline code: single backticks, such as `` `text` ``, become `<code>text</code>`
- Quotes: `> quote`
- Tables: `| column | column |`
- Images: `![alt](https://example.com/image.jpg)`
- Links: `[label](https://example.com/)`
- Bold and italic: `**bold**`, `*italic*`
- Separators: `---`, `***`, `___`
- Spacer marker: `[spacer]` or `[spacer:60]`
- WordPress shortcodes: `[shortcode ...]`
- Standalone URLs for embeds, media, and files

Backtick syntax is treated as Markdown only. It is converted only for `.md` and `.markdown` files: single-backtick text becomes inline `<code>`, and triple-backtick fences become WordPress `wp:code` blocks. In `.txt`, `.html`, `.htm`, and other formats, backticks are preserved as ordinary text.

#### Markdown Custom Layout Syntax

Ver.1.4 treats content from `:::name` to `:::` as one layout instruction.

Current or planned layout names include:

- `:::image_text_left`: image on the left, text on the right
- `:::image_text_right`: image on the right, text on the left
- `:::image_row_3_gap`: three images with spacing
- `:::image_row_3_no_gap`: three images without spacing
- `:::float_image_left`: left-aligned floating image
- `:::float_image_right`: right-aligned floating image
- `:::cta`: CTA heading, text, and button
- `:::faq`: FAQ
- `:::cards`: card-style layout

Example:

```markdown
:::image_text_left
image: https://example.com/service.jpg
alt: Service image
title: Our Service
text: Add service description text here.
width: 40
:::
```

Example with floating image:

```markdown
:::float_image_left
image: https://example.com/sample.jpg
alt: Sample image
width: 240
:::
```

### HTML

Supported simple HTML input includes:

- `<p>`, `<h1>` to `<h6>`
- `<ul>`, `<ol>`, `<li>`
- `<blockquote>`
- `<pre>`, `<code>`
- `<table>`, `<tr>`, `<th>`, `<td>`
- `<img>`
- `<a>`
- `<strong>`, `<b>`, `<em>`, `<i>`
- `<hr>`

`<b>` is converted to `<strong>`, and `<i>` is converted to `<em>` in the output.

Backticks in `.html` and `.htm` files are preserved as ordinary text. The converter must not rewrite backticks inside HTML content, especially inside `script`, `style`, `pre`, or `code` elements.

### Separated Values

CSV, TSV, SSV, and PSV files are converted into WordPress table blocks.

- `.csv`: comma-separated
- `.tsv`: tab-separated
- `.ssv`: space-separated or semicolon-separated
- `.psv`, `.pipesv`: pipe-separated

The delimiter is also detected from the file contents when possible. The first row is used as the header row.

### JSON

JSON structure data is converted into basic WordPress blocks.

- `title`, `heading`: heading
- `text`, `body`, `description`: paragraph
- `sections`, `blocks`, `content`: sections
- `items`, `list`: list
- `table`, `rows`: table
- `faq`, `faqs`: FAQ

This can be used to draft company pages, service pages, FAQ sections, and product lists from one JSON file.

### URL Handling

Standalone URLs are handled by type:

| URL type                                                                                                                | Output block     |
| ----------------------------------------------------------------------------------------------------------------------- | ---------------- |
| YouTube / YouTube Shorts / TikTok / Vimeo / Instagram / X / Twitter / Dailymotion / Twitch / TED / Spotify / SoundCloud | `core/embed`     |
| `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.avif`                                                               | `core/image`     |
| `.mp4`, `.webm`, `.mov`, `.m4v`                                                                                         | `core/video`     |
| `.mp3`, `.wav`, `.ogg`, `.m4a`                                                                                          | `core/audio`     |
| `.pdf`, `.zip`, Office files                                                                                            | `core/file`      |
| Other URLs inside text                                                                                                  | normal HTML link |

## Requirements

- Python 3.10 or later

No external packages are required.

## Usage

### GUI Mode

Run:

```powershell
python .\main.py --gui
```

Then choose:

1. The source file to convert
2. The destination HTML file to save

If no command-line paths are provided, GUI mode is opened automatically:

```powershell
python .\main.py
```

### Command Line Mode

```powershell
python .\main.py .\sample.md .\sample_wordpress.html
```

To open the helper editor for a plain text draft:

```powershell
python .\main.py .\sample.txt --edit-text
```

### Conversion Modes

Use `--mode` to switch output rules.

| Mode | Purpose |
| ---- | ------- |
| `normal` | Standard conversion. Keeps the existing HTML, Markdown, and embed behavior. |
| `middle` | Office WordPress output. It normalizes h1 to h2 for article bodies, writes heading levels explicitly, and removes dangerous HTML. |
| `high-security` | High-restriction output. It avoids CSS, dangerous tags, and dangerous attributes for safer saving in WordPress. |

```powershell
python .\main.py .\sample.md .\sample_wordpress.html --mode middle
```

For compatibility, the old `office` mode works the same as `middle`, and the old `hi-security` mode works the same as `high-security`.

In `middle`, `high-security`, `office`, and `hi-security` modes, `\\` with whitespace on both sides is treated as an explicit in-paragraph line break and converted to `<br><br>`. Backslashes attached to text, such as Windows paths like `C:\Users\...`, are left unchanged to avoid breaking paths.

For office WordPress output, the converter prefers WordPress core block comments such as `<!-- wp:paragraph -->`, `<!-- wp:heading -->`, `<!-- wp:list -->`, and `<!-- wp:table -->` instead of relying on free-form HTML alone.

### WP HTML / CSS lint

You can check converted WordPress block HTML files and downloaded CSS files.

Recommended: move to the project folder in PowerShell before running the linter.

```powershell
cd D:\PC\Python\wp_converter
python .\lint.py .\sample_wordpress.html
```

To check a `.wp_html` file:

```powershell
python .\lint.py .\your_article.wp_html
```

CSS files are detected automatically by the `.css` extension:

```powershell
python .\lint.py .\style.css
```

If you need to force the mode, use `--input-type`.

```powershell
python .\lint.py .\style.txt --input-type css
python .\lint.py .\your_article.html --input-type wp-html
```

Use `--mode` when checking output for office WordPress or high-security environments. The default lint mode is `high-security`.

```powershell
python .\lint.py .\your_article.wp_html --mode middle
python .\lint.py .\your_article.wp_html --mode high-security
python .\lint.py .\your_article.wp_html --mode normal
```

`normal` runs the standard structural checks. `middle`, `office`, `high-security`, and `hi-security` also warn about blocks and classes that may be hidden, disabled, or unstable in restricted WordPress environments.

If you prefer `python -m`, run it from the parent folder.

```powershell
cd D:\PC\Python
python -m wp_converter.lint .\wp_converter\your_article.wp_html
```

If your current folder is `D:\PC\Python\wp_converter\dictionaries` or another subfolder, move back to `D:\PC\Python\wp_converter` first.

For WordPress HTML, it checks:

- Matching `<!-- wp:paragraph -->` and `<!-- /wp:paragraph -->`
- Core block name typos such as `<!-- wp:paragaph -->`
- `<p>` and `</p>` inside paragraph blocks
- Heading block `level` matching the HTML heading tag from `<h2>` to `<h5>`
- `<figure class="wp-block-table">` and `<table>` inside table blocks
- HTML tag typos such as `<strnog>` and `<spna>` in both plain HTML and WordPress block HTML
- `href` on `<a>` tags
- `rel="noopener"` when `target="_blank"` is used
- `src` and `alt` on `<img>` tags
- Empty paragraph blocks. `<p></p>` and similar blocks are reported as `paragraph ブロックが空です。`.
- Blank lines inside `<p>` in paragraph blocks. These can make Gutenberg move the content to a Custom HTML block.
- Nested HTML tag mistakes such as `<p><strong>text</p>`
- Unclosed HTML tags inside core blocks, such as `<strong>` left open inside `wp:paragraph`
- Dangerous HTML such as `script`, `iframe`, `style`, `onclick`, and `javascript:`
- In non-normal modes, unstable core blocks such as `core/embed`, `core/html`, `core/shortcode`, `core/video`, `core/audio`, `core/file`, `core/gallery`, `core/media-text`, `core/columns`, `core/buttons`, and `core/spacer`
- In non-normal modes, classes found in the CSS audit as hidden or unstable, such as `hidden-post`, `samearea-otheroffice`, `blog-officelist`, `modal`, `swiper`, `visually-hidden`, `screen-reader`, and `sr-only`
- In non-normal modes, inline CSS that restricts display or interaction, such as `display:none`, `visibility:hidden`, `opacity:0`, `pointer-events:none`, `user-select:none`, and `overflow:hidden`

For CSS files, it checks:

- Display-disabling rules such as `display:none`, `visibility:hidden`, `content-visibility:hidden`, `opacity:0`, `width:0`, and `height:0`
- Interaction restrictions such as `pointer-events:none`, `user-select:none`, disabled cursors, and hidden scrollbars
- Layout rules that often break in WordPress or mobile views, such as `overflow:hidden`, `clip`, `clip-path`, `position:fixed`, and very large `z-index`
- External dependencies such as `@import` and `url(https://...)`
- Unmatched CSS braces, because a missing `}` can disable later rules

When issues are found, it prints the line number, problem, and fix hint.

In `text_editor`, use `Tools > lintチェック` to highlight issue lines. Hover over a highlighted line to see the warning and fix hint. Files ending in `.css` are checked with the CSS linter. Files ending in `.wp_html`, `.html`, or `.htm`, and text containing `<!-- wp:`, are checked with the WordPress HTML linter.

To run the real-world lint tester built from an actual article sample:

```powershell
python -m pytest tests/test_wp_html_lint_real_world_tester.py
```

## Example

Input Markdown:

```markdown
# Video Test

This is a paragraph.

https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Output:

```html
<!-- wp:heading {"level":1} -->
<h1>Video Test</h1>
<!-- /wp:heading -->

<!-- wp:paragraph -->
<p>This is a paragraph.</p>
<!-- /wp:paragraph -->

<!-- wp:embed {"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","type":"video","providerNameSlug":"youtube","responsive":true,"className":"wp-embed-aspect-16-9 wp-has-aspect-ratio"} -->
<figure class="wp-block-embed is-type-video is-provider-youtube wp-block-embed-youtube wp-embed-aspect-16-9 wp-has-aspect-ratio">
<div class="wp-block-embed__wrapper">
https://www.youtube.com/watch?v=dQw4w9WgXcQ
</div>
</figure>
<!-- /wp:embed -->
```

## Project Structure

```text
wp_converter/
├─ main.py
├─ storage.py
├─ file_checker.py
├─ gui_maker.py
├─ lint.py
├─ converters/
│  ├─ document_converter.py
│  ├─ hi_security_filter.py
│  ├─ html_converter.py
│  ├─ json_converter.py
│  ├─ markdown_layout_converter.py
│  ├─ markdown_converter.py
│  ├─ separated_values_converter.py
│  ├─ text_converter.py
│  ├─ wp_txt_converter.py
├─ blocks/
│  ├─ code.py
│  ├─ embed.py
│  ├─ heading.py
│  ├─ html_block.py
│  ├─ image.py
│  ├─ inline.py
│  ├─ list_block.py
│  ├─ layout.py
│  ├─ media.py
│  ├─ paragraph.py
│  ├─ quote.py
│  ├─ separator.py
│  ├─ shortcode.py
│  ├─ spacer.py
│  └─ table.py
└─ dictionaries/
   ├─ hi_security_dict.py
   ├─ html_dict.py
   ├─ layout_dict.py
   ├─ json_dict.py
   ├─ markdown_dict.py
   ├─ separated_values_dict.py
   ├─ text_dict.py
   └─ wp_txt_dict.py
```

## Development Policy

The project keeps each responsibility small:

- `main.py` handles file selection, command-line arguments, and saving
- `storage.py` reads source files and writes converted files
- `file_checker.py` checks supported extensions and selects converters
- `gui_maker.py` handles GUI windows and file selection
- `lint.py` checks WordPress block HTML and CSS for common issues
- `converters/` converts each input format
- `blocks/` creates WordPress block HTML
- `dictionaries/` stores conversion rules and patterns

The current goal is a minimal, stable converter rather than a full Markdown or HTML parser.

## Notes

This tool generates HTML intended for the WordPress block editor. For complex HTML, custom themes, or plugin-specific blocks, manual checking in WordPress is recommended.

## License

No license has been selected yet.
