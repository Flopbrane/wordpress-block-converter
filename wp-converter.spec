# -*- mode: python ; coding: utf-8 -*-


app_datas = [
    ('readme.txt', '.'),
    ('readme_jp.txt', '.'),
    ('LICENSE.txt', '.'),
    ('module_installer.py', '.'),
    ('portable_runtime.py', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=app_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='wp-converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

cleaner_a = Analysis(
    ['module_cleaner.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
cleaner_pyz = PYZ(cleaner_a.pure)

cleaner_exe = EXE(
    cleaner_pyz,
    cleaner_a.scripts,
    [],
    exclude_binaries=True,
    name='module_cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    cleaner_exe,
    a.binaries,
    cleaner_a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='wp-converter',
)
