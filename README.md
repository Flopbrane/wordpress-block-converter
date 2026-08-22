# WordPress Block Converter

Convert plain text, Markdown, and simple HTML files into WordPress Gutenberg-compatible HTML blocks.

This project is designed as a small beginner-friendly Python tool for preparing article drafts before pasting them into the WordPress block editor.

## Features

- Convert plain text paragraphs into WordPress paragraph blocks
- Convert Markdown headings, paragraphs, lists, quotes, code blocks, tables, separators, images, and shortcodes
- Convert simple HTML headings, paragraphs, lists, quotes, code blocks, tables, images, links, and shortcodes
- Convert YouTube, YouTube Shorts, TikTok, Vimeo, and other supported service URLs into WordPress embed blocks
- Convert direct media/file URLs into `image`, `video`, `audio`, or `file` blocks
- Keep common inline formatting such as links, bold, and italic text
- Insert a 24px spacer between plain text paragraphs
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
| List | `core/html` by default |
| Code | `core/code` |
| Quote | `core/quote` |
| Spacer | `core/spacer` |
| Separator | `core/separator` |
| Table | `core/table` |
| Custom HTML | `core/html` |
| Image | `core/image` |
| Video file | `core/video` |
| Audio file | `core/audio` |
| Download file | `core/file` |
| Shortcode | `core/shortcode` |
| External service URL | `core/embed` |

## Conversion Details

### Plain Text

- Blank lines split paragraphs.
- Line breaks inside a paragraph become `<br><br>`.
- A 24px spacer block is inserted between paragraphs.

### Markdown

Supported Markdown-style input includes:

- Headings: `#`, `##`, up to `######`
- Paragraphs
- Unordered lists: `-`, `*`, `+`
- Ordered lists: `1.` or `1)`
- Code fences: triple backticks
- Quotes: `> quote`
- Tables: `| column | column |`
- Images: `![alt](https://example.com/image.jpg)`
- Links: `[label](https://example.com/)`
- Bold and italic: `**bold**`, `*italic*`
- Separators: `---`, `***`, `___`
- Spacer marker: `[spacer]` or `[spacer:60]`
- WordPress shortcodes: `[shortcode ...]`
- Standalone URLs for embeds, media, and files

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

### URL Handling

Standalone URLs are handled by type:

| URL type | Output block |
|---|---|
| YouTube / YouTube Shorts / TikTok / Vimeo / Instagram / X / Twitter / Dailymotion / Twitch / TED / Spotify / SoundCloud | `core/embed` |
| `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`, `.avif` | `core/image` |
| `.mp4`, `.webm`, `.mov`, `.m4v` | `core/video` |
| `.mp3`, `.wav`, `.ogg`, `.m4a` | `core/audio` |
| `.pdf`, `.zip`, Office files | `core/file` |
| Other URLs inside text | normal HTML link |

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
│  ├─ image.py
│  ├─ inline.py
│  ├─ list_block.py
│  ├─ media.py
│  ├─ paragraph.py
│  ├─ quote.py
│  ├─ separator.py
│  ├─ shortcode.py
│  ├─ spacer.py
│  └─ table.py
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
