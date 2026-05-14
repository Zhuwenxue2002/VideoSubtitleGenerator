# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Video Subtitle Generator (Windows build).
Run: pyinstaller build.spec
"""

import sys
from pathlib import Path

import faster_whisper

_fw_assets = str(Path(faster_whisper.__file__).parent / "assets")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('bin/ffmpeg.exe', 'bin'),
        ('bin/ffprobe.exe', 'bin'),
        (_fw_assets, 'faster_whisper/assets'),
    ],
    hiddenimports=[
        'faster_whisper',
        'ctranslate2',
        'tokenizers',
        'huggingface_hub',
        'onnxruntime',
        'av',
        'tqdm',
        'numpy',
        'fsspec',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter.test',
        'unittest',
        'pydoc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoSubtitleGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
