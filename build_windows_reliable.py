import PyInstaller.__main__
import sys
import os
import platform
import shutil

def build_windows_reliable():
    """Build Windows app with multiple fallback options to avoid DLL issues."""
    
    if platform.system() != "Windows":
        print("This script is for Windows builds only")
        return False
    
    print("M3U8 Downloader - Windows Reliable Build")
    print("=" * 50)
    
    # Try multiple build configurations
    build_configs = [
        {
            'name': 'Directory Build (Most Reliable)',
            'options': [
                'app.py',
                '--name=M3U8Downloader',
                '--onedir',  # Directory instead of single file
                '--windowed',
                '--clean',
                '--noupx',
                '--strip',
                '--hidden-import=requests',
                '--hidden-import=urllib3',
                '--hidden-import=m3u8',
                '--hidden-import=tempfile',
                '--hidden-import=platform',
                '--hidden-import=threading',
                '--hidden-import=tkinter.scrolledtext',
            ]
        },
        {
            'name': 'Console Build (Fallback)',
            'options': [
                'app.py',
                '--name=M3U8Downloader-Console',
                '--onedir',
                '--console',  # Show console for debugging
                '--clean',
                '--noupx',
                '--hidden-import=requests',
                '--hidden-import=urllib3',
                '--hidden-import=m3u8',
                '--hidden-import=tempfile',
                '--hidden-import=platform',
                '--hidden-import=threading',
                '--hidden-import=tkinter.scrolledtext',
            ]
        }
    ]
    
    # Add common options
    for config in build_configs:
        if os.path.exists('app_icon.ico'):
            config['options'].append('--icon=app_icon.ico')
        
        if os.path.exists('version_info.txt'):
            config['options'].append('--version-file=version_info.txt')
        
        # Exclude problematic modules
        exclude_modules = [
            'matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2',
            'tensorflow', 'torch', 'jupyter', 'IPython'
        ]
        
        for module in exclude_modules:
            config['options'].append(f'--exclude-module={module}')
    
    # Try each configuration
    for i, config in enumerate(build_configs, 1):
        print(f"\nAttempt {i}: {config['name']}")
        print("-" * 30)
        
        try:
            print("Building...")
            PyInstaller.__main__.run(config['options'])
            
            # Check if build succeeded
            if '--onedir' in config['options']:
                exe_path = "dist/M3U8Downloader/M3U8Downloader.exe"
                if 'Console' in config['name']:
                    exe_path = "dist/M3U8Downloader-Console/M3U8Downloader-Console.exe"
            else:
                exe_path = "dist/M3U8Downloader.exe"
            
            if os.path.exists(exe_path):
                size_mb = os.path.getsize(exe_path) / (1024 * 1024)
                print(f"SUCCESS: Build completed!")
                print(f"Executable: {exe_path}")
                print(f"Size: {size_mb:.1f} MB")
                print(f"\nRecommendation: Test this build on a clean Windows machine")
                return True
            else:
                print(f"Build completed but executable not found at: {exe_path}")
                
        except Exception as e:
            print(f"Build failed: {e}")
            if i < len(build_configs):
                print("Trying next configuration...")
                continue
    
    print("\nAll build attempts failed.")
    print("Possible solutions:")
    print("1. Update PyInstaller: pip install --upgrade pyinstaller")
    print("2. Try Python 3.10 instead of 3.11")
    print("3. Use virtual environment")
    print("4. Run as administrator")
    return False

if __name__ == "__main__":
    build_windows_reliable()
