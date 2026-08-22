# AGENTS.md

## Project Overview

This project is a Python tool that converts plain text, Markdown, and HTML files into WordPress Gutenberg-compatible HTML.

The main goal is to help beginners create WordPress articles safely and predictably.

## Language

Please explain changes and suggestions in Japanese.

Code comments may be in Japanese when they help readability.

## Naming Rules

Use these names consistently:

- `load_file_path`: path of the input file
- `save_file_path`: path of the output file
- `load_file`: input data file
- `save_file`: output data file

Avoid using vague names such as `input_file` or `output_file` when the above names fit.

## Project Structure

```text
wp_converter/
├─ main.py
├─ converters/
│  ├─ markdown_converter.py
│  ├─ text_converter.py
│  └─ html_converter.py
├─ blocks/
│  ├─ paragraph.py
│  ├─ heading.py
│  ├─ code.py
│  └─ list_block.py
└─ dictionaries/
   ├─ markdown_dict.py
   ├─ text_dict.py
   └─ html_dict.py
````

## Responsibilities

### main.py

- Receive `load_file_path` and `save_file_path`
- Detect file type by extension
- Call the correct converter
- Save the converted WordPress HTML

### converters/

Converters read source text and convert it into WordPress block HTML.

- `markdown_converter.py`: convert Markdown
- `text_converter.py`: convert plain text
- `html_converter.py`: clean and convert existing HTML

### blocks/

Blocks generate WordPress Gutenberg block strings.

- `paragraph.py`: paragraph block
- `heading.py`: heading block
- `code.py`: code block
- `list_block.py`: list or HTML list block

### dictionaries/

Dictionaries define conversion rules.

- `markdown_dict.py`: Markdown symbols and rules
- `text_dict.py`: plain text rules
- `html_dict.py`: HTML tag handling rules

## WordPress Output Policy

Generate WordPress Gutenberg-compatible HTML.

Use block comments such as:

```html
<!-- wp:paragraph -->
<p>本文</p>
<!-- /wp:paragraph -->
```

For headings, use Gutenberg heading blocks.

For lists, prefer simple and stable HTML output. If WordPress list blocks become unstable, use an HTML block.

Example:

```html
<!-- wp:html -->
<ul>
  <li>項目1</li>
  <li>項目2</li>
</ul>
<!-- /wp:html -->
```

## Coding Policy

- Keep the code beginner-friendly.
- Prefer simple functions over complex classes.
- Add type hints where useful.
- Avoid unnecessary abstractions.
- Do not rewrite unrelated files.
- Do not make large refactors unless requested.
- Use only the Python standard library at first.
- Add pandas only if there is a clear benefit.

## Safety Policy

Before changing behavior, explain what will change.

When adding code, keep changes small and testable.

Do not delete files unless explicitly requested.

## Test Policy

When possible, add small sample tests or manual test examples.

Use simple sample files such as:

- `sample.md`
- `sample.txt`
- `sample.html`

Confirm that output can be opened and pasted into WordPress.

## Current Development Goal

First build a minimal working version:

1. Convert plain text paragraphs.
2. Convert Markdown headings and paragraphs.
3. Convert simple HTML paragraphs.
4. Save WordPress-compatible HTML.
5. Add list and code block support after the basic version works.

```text
PowerShellで作るなら、`D:\PC\Python` にいる状態でこれです。
```

```powershell
notepad .\wp_converter\AGENTS.md
```

開いたメモ帳に上の内容を貼り付けて保存すればOKです。

先生としては、最初は --「平文 `.txt` → WordPress段落HTML」だけを完成--させるのがおすすめです。そこが通れば、MarkdownとHTMLは後からかなり楽に足せます。
