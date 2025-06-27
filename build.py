import PyInstaller.__main__
import sys
import os

# Determine correct --add-data format
if sys.platform == 'win32':
    data_sep = ';'
    icon_arg = '--icon=app_icon.ico'
elif sys.platform == 'darwin':
    data_sep = ':'
    icon_arg = '--icon=app_icon.icns'

# Build configuration
build_options = [
    'app.py',
    '--name=M3U8Downloader',
    '--windowed',
    '--onefile',
    icon_arg,
    f'--add-data=app_icon.ico{data_sep}.',
    '--hidden-import=requests',
    '--hidden-import=urllib3',
    '--clean',
]

# Platform-specific options
if sys.platform == 'darwin':
    build_options.extend([
        '--osx-bundle-identifier=com.elfadouaki.m3u8downloader',
        '--target-architecture=universal2',
    ])
elif sys.platform == 'win32':
    build_options.extend([
        '--version-file=version_info.txt',
    ])

# Run PyInstaller
PyInstaller.__main__.run(build_options)
