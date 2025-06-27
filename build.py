import PyInstaller.__main__
import sys
import os

# Build configuration
build_options = [
    'app.py',  # Your main app file
    '--name=M3U8Downloader',
    '--windowed',  # No console window
    '--onefile',   # Single executable
    '--icon=app_icon.ico',  # Optional: add an icon
    '--add-data=app_icon.ico;.',  # Include icon in bundle
    '--hidden-import=requests',
    '--hidden-import=urllib3',
    '--clean',
]

# Platform-specific options
if sys.platform == 'darwin':  # macOS
    build_options.extend([
        '--osx-bundle-identifier=com.elfadouaki.m3u8downloader',
        '--target-arch=universal2',  # Universal binary
    ])
elif sys.platform == 'win32':  # Windows
    build_options.extend([
        '--version-file=version_info.txt',  # Optional version info
    ])

# Run PyInstaller
PyInstaller.__main__.run(build_options)