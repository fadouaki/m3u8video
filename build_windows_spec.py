import PyInstaller.__main__
import sys
import os
import platform

def create_windows_spec_file():
    """Create a custom spec file for Windows to avoid DLL issues."""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Windows-specific fixes for DLL loading
import os
import sys

# Add current directory to path for finding ffmpeg
current_dir = os.path.dirname(os.path.abspath('.'))

a = Analysis(
    ['app.py'],
    pathex=[current_dir],
    binaries=[
        # Bundle FFmpeg if available
        ('ffmpeg.exe', '.') if os.path.exists('ffmpeg.exe') else None,
    ],
    datas=[
        ('app_icon.ico', '.') if os.path.exists('app_icon.ico') else None,
    ],
    hiddenimports=[
        'requests',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',
        'm3u8',
        'tempfile',
        'platform',
        'threading',
        'tkinter.scrolledtext',
        'certifi',
        'charset_normalizer',
        'idna',
        'email.mime',
        'email.mime.multipart',
        'email.mime.text',
        'email.mime.base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy', 
        'scipy',
        'pandas',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
        'jupyter',
        'IPython',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filter out None entries from binaries and datas
a.binaries = [x for x in a.binaries if x is not None]
a.datas = [x for x in a.datas if x is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='M3U8Downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,  # Disable UPX to avoid DLL issues
    console=False,  # GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=True,
    upx=False,  # Disable UPX to avoid DLL issues
    upx_exclude=[],
    name='M3U8Downloader',
)
'''
    
    with open('windows_build.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created custom windows_build.spec file")
    return 'windows_build.spec'

def build_with_spec():
    """Build using custom spec file."""
    
    if platform.system() != "Windows":
        print("This script is for Windows builds only")
        return False
    
    print("M3U8 Downloader - Windows Spec Build")
    print("=" * 50)
    
    # Download FFmpeg first
    try:
        from build_windows_reliable import download_and_bundle_ffmpeg
        ffmpeg_path = download_and_bundle_ffmpeg()
    except ImportError:
        # Fallback if import fails
        ffmpeg_path = "ffmpeg.exe" if os.path.exists("ffmpeg.exe") else None
    
    # Create spec file
    spec_file = create_windows_spec_file()
    
    # Build with spec file
    try:
        print("\\nBuilding with custom spec file...")
        result = PyInstaller.__main__.run([
            spec_file,
            '--clean',
            '--noconfirm'
        ])
        
        # Check results
        exe_path = "dist/M3U8Downloader/M3U8Downloader.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\\nSUCCESS: Spec build completed!")
            print(f"Executable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            
            if ffmpeg_path and size_mb > 80:
                print(f"SUCCESS: FFmpeg bundled successfully")
            elif ffmpeg_path:
                print(f"WARNING: Check if FFmpeg bundling worked")
            
            return True
        else:
            print(f"ERROR: Executable not found")
            return False
            
    except Exception as e:
        print(f"ERROR: Spec build failed: {e}")
        return False

if __name__ == "__main__":
    build_with_spec()
