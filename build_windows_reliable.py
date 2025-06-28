import PyInstaller.__main__
import sys
import os
import platform
import shutil

def download_and_bundle_ffmpeg():
    """Download FFmpeg for Windows and prepare for bundling."""
    print("Step 1: Downloading FFmpeg for Windows...")
    
    import tempfile
    import zipfile
    import requests
    import os
    import shutil
    
    # Check if already downloaded
    if os.path.exists("ffmpeg.exe"):
        size = os.path.getsize("ffmpeg.exe") / (1024 * 1024)
        print(f"FFmpeg already exists: ffmpeg.exe ({size:.1f} MB)")
        return "ffmpeg.exe"
    
    try:
        # Download FFmpeg
        ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-4.4.4-essentials_build.zip"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")
            
            print("   Downloading FFmpeg...")
            response = requests.get(ffmpeg_url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print("   Extracting FFmpeg...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find ffmpeg.exe
            for root, dirs, files in os.walk(temp_dir):
                if 'ffmpeg.exe' in files:
                    ffmpeg_source = os.path.join(root, 'ffmpeg.exe')
                    ffmpeg_dest = "ffmpeg.exe"
                    shutil.copy2(ffmpeg_source, ffmpeg_dest)
                    
                    size = os.path.getsize(ffmpeg_dest) / (1024 * 1024)
                    print(f"   SUCCESS: FFmpeg downloaded ({size:.1f} MB)")
                    return ffmpeg_dest
            
            print("   ERROR: ffmpeg.exe not found in download")
            return None
            
    except Exception as e:
        print(f"   ERROR: Failed to download FFmpeg: {e}")
        return None

def build_windows_reliable():
    """Build Windows app with multiple fallback options to avoid DLL issues."""
    
    if platform.system() != "Windows":
        print("This script is for Windows builds only")
        return False
    
    print("M3U8 Downloader - Windows Reliable Build")
    print("=" * 50)
    
    # Download FFmpeg first
    ffmpeg_path = download_and_bundle_ffmpeg()
    if not ffmpeg_path:
        print("WARNING: FFmpeg not available - app will need external FFmpeg")
        ffmpeg_path = None
    
    # Try multiple build configurations with DLL fixes
    build_configs = [
        {
            'name': 'Directory Build - No UPX (Most Reliable)',
            'options': [
                'app.py',
                '--name=M3U8Downloader',
                '--onedir',  # Directory instead of single file
                '--windowed',
                '--clean',
                '--noupx',  # Prevents DLL loading issues
                '--noconfirm',  # Don't ask for confirmation
                '--hidden-import=requests',
                '--hidden-import=urllib3',
                '--hidden-import=m3u8',
                '--hidden-import=tempfile',
                '--hidden-import=platform',
                '--hidden-import=threading',
                '--hidden-import=tkinter.scrolledtext',
                '--hidden-import=certifi',
                '--hidden-import=charset_normalizer',
                '--collect-all=requests',  # Include all requests components
                '--collect-all=urllib3',   # Include all urllib3 components
            ]
        },
        {
            'name': 'Console Build (Debugging)',
            'options': [
                'app.py',
                '--name=M3U8Downloader-Console',
                '--onedir',
                '--console',  # Show console for debugging
                '--clean',
                '--noupx',
                '--noconfirm',
                '--hidden-import=requests',
                '--hidden-import=urllib3',
                '--hidden-import=m3u8',
                '--hidden-import=tempfile',
                '--hidden-import=platform',
                '--hidden-import=threading',
                '--hidden-import=tkinter.scrolledtext',
                '--collect-all=requests',
                '--collect-all=urllib3',
            ]
        },
        {
            'name': 'Single File (Last Resort)',
            'options': [
                'app.py',
                '--name=M3U8Downloader-SingleFile',
                '--onefile',
                '--console',  # Show console to see errors
                '--noupx',
                '--noconfirm',
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
        # Add FFmpeg bundling if available
        if ffmpeg_path:
            config['options'].append(f'--add-binary={ffmpeg_path};.')
            print(f"   Will bundle FFmpeg in {config['name']}")
        
        if os.path.exists('app_icon.ico'):
            config['options'].append('--icon=app_icon.ico')
        
        if os.path.exists('version_info.txt'):
            config['options'].append('--version-file=version_info.txt')
        
        # Exclude problematic modules
        exclude_modules = [
            'matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2',
            'tensorflow', 'torch', 'jupyter', 'IPython', 'notebook'
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
                
                # Check if FFmpeg bundling worked
                if ffmpeg_path:
                    if size_mb > 80:  # Should be much larger with FFmpeg
                        print(f"SUCCESS: FFmpeg appears to be bundled (large size)")
                    else:
                        print(f"WARNING: Size seems small for bundled FFmpeg")
                        # Check if ffmpeg.exe exists in the directory
                        dir_path = os.path.dirname(exe_path)
                        bundled_ffmpeg = os.path.join(dir_path, "ffmpeg.exe")
                        if os.path.exists(bundled_ffmpeg):
                            print(f"SUCCESS: Found bundled ffmpeg.exe in directory")
                        else:
                            print(f"WARNING: ffmpeg.exe not found in {dir_path}")
                
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
