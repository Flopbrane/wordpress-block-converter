# WordPress Block Converter

Convert plain text, Markdown, and simple HTML files into WordPress Gutenberg-compatible HTML blocks.

This project is designed as a small beginner-friendly Python tool for preparing article drafts before pasting them into the WordPress block editor.

## Features

- Convert plain text paragraphs into WordPress paragraph blocks
- Convert Markdown headings and paragraphs
- Convert simple HTML headings, paragraphs, and lists
- Convert YouTube URLs into WordPress embed blocks
- Convert TikTok URLs into WordPress embed blocks
- Choose files with a simple GUI
- Run from the command line when needed
- Uses only the Python standard library

## Supported Input Files

| Format | Extensions |
|---|---|
| Plain text | `.txt` |
| Markdown | `.md`, `.markdown` |
| HTML | `.html`, `.htm` |

## Supported WordPress Blocks

| Content | WordPress block |
|---|---|
| Paragraph | `core/paragraph` |
| Heading | `core/heading` |
| HTML list / table | `core/html` |
| Code | `core/code` |
| Quote | `core/quote` |
| Spacer | `core/spacer` |
| YouTube / TikTok embed | `core/embed` |

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
├─ converters/
│  ├─ markdown_converter.py
│  ├─ text_converter.py
│  └─ html_converter.py
├─ blocks/
│  ├─ code.py
│  ├─ embed.py
│  ├─ heading.py
│  ├─ html_block.py
│  ├─ list_block.py
│  ├─ paragraph.py
│  ├─ quote.py
│  └─ spacer.py
└─ dictionaries/
   ├─ markdown_dict.py
   ├─ text_dict.py
   └─ html_dict.py
```

## Development Policy

The project keeps each responsibility small:

- `main.py` handles file selection, command-line arguments, and saving
- `converters/` converts each input format
- `blocks/` creates WordPress block HTML
- `dictionaries/` stores conversion rules and patterns

The current goal is a minimal, stable converter rather than a full Markdown or HTML parser.

## Notes

This tool generates HTML intended for the WordPress block editor. For complex HTML, custom themes, or plugin-specific blocks, manual checking in WordPress is recommended.

## License

No license has been selected yet.
