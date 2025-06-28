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
    'app.py',
    '--name=M3U8Downloader',
    '--windowed',
    '--onefile',
    '--clean',
    # Reduce antivirus false positives
    '--noupx',  # Don't use UPX compression
    '--strip',  # Strip debug symbols
    # Hidden imports
    '--hidden-import=requests',
    '--hidden-import=urllib3',
    '--hidden-import=m3u8',
    '--hidden-import=tempfile',
    '--hidden-import=platform',
    '--hidden-import=threading',
    '--hidden-import=tkinter.scrolledtext',
    '--hidden-import=certifi',
    '--hidden-import=charset_normalizer',
]

# Add icon if available
if icon_arg and (
    (sys.platform == 'darwin' and os.path.exists('app_icon.icns')) or
    (sys.platform == 'win32' and os.path.exists('app_icon.ico'))
):
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
    build_options.extend([
        # Windows-specific options to reduce false positives
        '--console',  # Show console for debugging (remove for final build)
        '--disable-windowed-traceback',
    ])
    if os.path.exists('version_info.txt'):
        build_options.append('--version-file=version_info.txt')

# Add exclude options to reduce file size and false positives
exclude_modules = [
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
]

for module in exclude_modules:
    build_options.append(f'--exclude-module={module}')

print("Building with options:")
for option in build_options:
    print(f"  {option}")

# Run PyInstaller
try:
    PyInstaller.__main__.run(build_options)
    print(" Build completed successfully!")
    print("The executable will be in the 'dist' folder.")
    
    if sys.platform == 'win32':
        print(" To reduce antivirus false positives:")
        print("1. Submit the file to VirusTotal for analysis")
        print("2. Consider code signing for production releases")
        print("3. Build reputation by having users mark as safe")
        print("4. Use Windows Defender exclusions during development")
    else:
        print("\nIMPORTANT: Make sure FFmpeg is installed on target systems:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        
except Exception as e:
    print(f" Build failed: {e}")
    sys.exit(1)