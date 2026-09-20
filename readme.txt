wp-converter portable package
=============================

Purpose:
wp-converter converts plain text, Markdown, and HTML into WordPress Gutenberg-compatible HTML.

How to start:
Run wp-converter.exe in this folder.

Portable runtime policy:
This package is designed to keep runtime files inside this application folder when possible.
Python modules should be installed into runtime/venv by module_installer.py.
Caches and temporary files should be placed under cache/, data/, logs/, and install_records/.

Cleaner:
Use module_cleaner.exe before deleting this folder.

Recommended removal order:
1. Close wp-converter.exe.
2. Run module_cleaner.exe --scan.
3. Run module_cleaner.exe --dry-run.
4. If the listed candidates are safe, run module_cleaner.exe --clean.
5. Delete the whole wp-converter folder manually.

Do not delete:
- Existing Python installations outside this folder.
- Existing virtual environments outside this folder.
- Shared AI models or shared caches outside this folder.

License:
See LICENSE.txt.
