import PyInstaller.__main__
import sys
import os
import platform

# Determine correct --add-data format
if sys.platform == 'win32':
    data_sep = ';'
    icon_arg = '--icon=app_icon.ico'
elif sys.platform == 'darwin':
    data_sep = ':'
    icon_arg = '--icon=app_icon.icns'
else:  # Linux
    data_sep = ':'
    icon_arg = ''

# Build configuration
build_options = [
    'app.py',  # Use the fixed version
    '--name=M3U8Downloader',
    '--windowed',
    '--onefile',
    '--clean',
    '--hidden-import=requests',
    '--hidden-import=urllib3',
    '--hidden-import=m3u8',
    '--hidden-import=tempfile',
    '--hidden-import=platform',
    '--hidden-import=threading',
    '--hidden-import=tkinter.scrolledtext',
]

# Add icon if available
if icon_arg:
    build_options.append(icon_arg)

# Add data files
if os.path.exists('app_icon.ico'):
    build_options.append(f'--add-data=app_icon.ico{data_sep}.')

# Platform-specific options
if sys.platform == 'darwin':
    build_options.extend([
        '--osx-bundle-identifier=com.elfadouaki.m3u8downloader',
        # Removed universal2 to avoid compatibility issues
    ])
elif sys.platform == 'win32':
    if os.path.exists('version_info.txt'):
        build_options.extend([
            '--version-file=version_info.txt',
        ])

print("Building with options:")
for option in build_options:
    print(f"  {option}")

# Run PyInstaller
PyInstaller.__main__.run(build_options)

print("\nBuild completed!")
print("The executable will be in the 'dist' folder.")
if sys.platform != 'win32':
    print("\nIMPORTANT: Make sure FFmpeg is installed on target systems:")
    print("  macOS: brew install ffmpeg")
    print("  Ubuntu/Debian: sudo apt install ffmpeg")
    print("  Or download from: https://ffmpeg.org/download.html")
