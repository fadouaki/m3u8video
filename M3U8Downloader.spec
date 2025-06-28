# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('/opt/homebrew/bin/ffmpeg', '.')],
    datas=[('app_icon.ico', '.')],
    hiddenimports=['requests', 'urllib3', 'm3u8', 'tempfile', 'platform', 'threading', 'tkinter.scrolledtext', 'certifi', 'charset_normalizer', 'idna'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2', 'tensorflow', 'torch', 'jupyter', 'IPython', 'notebook'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='M3U8Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app_icon.icns'],
)
app = BUNDLE(
    exe,
    name='M3U8Downloader.app',
    icon='app_icon.icns',
    bundle_identifier='com.elfadouaki.m3u8downloader',
)
