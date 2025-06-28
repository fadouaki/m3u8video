import PyInstaller.__main__
import sys
import os
import platform
import shutil
import requests
import zipfile
import tempfile

def download_ffmpeg_windows():
    """Download FFmpeg for Windows if not found locally."""
    print("FFmpeg not found locally. Downloading...")
    
    # FFmpeg download URL (static build from gyan.dev)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-4.4.4-essentials_build.zip"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        
        print("   Downloading FFmpeg archive...")
        response = requests.get(ffmpeg_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r   Progress: {percent:.1f}%", end="", flush=True)
        
        print("\n   Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find ffmpeg.exe in extracted files
        for root, dirs, files in os.walk(temp_dir):
            if 'ffmpeg.exe' in files:
                ffmpeg_source = os.path.join(root, 'ffmpeg.exe')
                ffmpeg_dest = os.path.join(os.getcwd(), 'ffmpeg.exe')
                shutil.copy2(ffmpeg_source, ffmpeg_dest)
                print(f"SUCCESS: FFmpeg downloaded to: {ffmpeg_dest}")
                return ffmpeg_dest
        
        raise Exception("FFmpeg.exe not found in downloaded archive")

def find_or_download_ffmpeg():
    """Find FFmpeg locally or download it automatically."""
    system = platform.system()
    
    # First, check if FFmpeg is already available
    if system == "Windows":
        ffmpeg_names = ["ffmpeg.exe"]
        local_paths = [
            "./ffmpeg.exe",
            "ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe"
        ]
    else:
        ffmpeg_names = ["ffmpeg"]
        local_paths = [
            "./ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/usr/bin/ffmpeg"
        ]
    
    # Check system PATH
    for name in ffmpeg_names:
        path = shutil.which(name)
        if path:
            print(f"SUCCESS: Found FFmpeg in PATH: {path}")
            return path
    
    # Check local paths
    for path in local_paths:
        if os.path.exists(path):
            print(f"SUCCESS: Found FFmpeg locally: {path}")
            return path
    
    # Download if not found (Windows only for now)
    if system == "Windows":
        try:
            return download_ffmpeg_windows()
        except Exception as e:
            print(f"ERROR: Failed to download FFmpeg: {e}")
            return None
    else:
        print(f"WARNING: FFmpeg not found on {system}")
        if system == "Darwin":
            print("   Install with: brew install ffmpeg")
        else:
            print("   Install with: sudo apt install ffmpeg")
        return None

def main():
    """Main build function with auto-bundle."""
    system = platform.system()
    
    print("M3U8 Downloader - Auto-Bundle Build")
    print("=" * 50)
    
    # Step 1: Ensure FFmpeg is available
    print("\nStep 1: Locating FFmpeg...")
    ffmpeg_path = find_or_download_ffmpeg()
    
    if not ffmpeg_path:
        print("ERROR: Could not locate or download FFmpeg")
        print("   The app will still build, but users will need FFmpeg installed")
        ffmpeg_path = None
    else:
        print(f"SUCCESS: FFmpeg ready: {ffmpeg_path}")
    
    # Step 2: Prepare build options
    print("\nStep 2: Preparing build configuration...")
    
    if system == "Windows":
        data_sep = ';'
        icon_arg = '--icon=app_icon.ico'
    elif system == "Darwin":
        data_sep = ':'
        icon_arg = '--icon=app_icon.icns'
    else:
        data_sep = ':'
        icon_arg = ''
    
    # Core build options
    build_options = [
        'app.py',
        '--name=M3U8Downloader',
        '--onefile',
        '--windowed',
        '--clean',
        '--noupx',  # Prevents DLL issues on Windows
        '--strip',
        
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
        '--hidden-import=idna',
    ]
    
    # Bundle FFmpeg if available
    if ffmpeg_path:
        build_options.append(f'--add-binary={ffmpeg_path}{data_sep}.')
        print("INFO: FFmpeg will be bundled with the executable!")
    
    # Add icon if available
    if icon_arg and (
        (system == 'Darwin' and os.path.exists('app_icon.icns')) or
        (system == 'Windows' and os.path.exists('app_icon.ico'))
    ):
        build_options.append(icon_arg)
    
    # Add data files
    if os.path.exists('app_icon.ico'):
        build_options.append(f'--add-data=app_icon.ico{data_sep}.')
    
    # Platform-specific options
    if system == 'Windows':
        if os.path.exists('version_info.txt'):
            build_options.append('--version-file=version_info.txt')
    elif system == 'Darwin':
        build_options.extend([
            '--osx-bundle-identifier=com.elfadouaki.m3u8downloader',
        ])
    
    # Exclude unnecessary modules
    exclude_modules = [
        'matplotlib', 'numpy', 'scipy', 'pandas', 'PIL', 'cv2',
        'tensorflow', 'torch', 'jupyter', 'IPython', 'notebook'
    ]
    
    for module in exclude_modules:
        build_options.append(f'--exclude-module={module}')
    
    print("Build configuration:")
    for option in build_options:
        if '--add-binary=' in option and 'ffmpeg' in option:
            print(f"  {option} <- FFmpeg bundled!")
        else:
            print(f"  {option}")
    
    # Step 3: Build the application
    print(f"\nStep 3: Building executable...")
    
    try:
        PyInstaller.__main__.run(build_options)
        
        # Step 4: Verify the build
        print(f"\nSUCCESS: Build completed successfully!")
        
        if system == "Windows":
            exe_path = "dist/M3U8Downloader.exe"
            print(f"Executable: {exe_path}")
        elif system == "Darwin":
            app_path = "dist/M3U8Downloader.app"
            print(f"Application: {app_path}")
        else:
            exe_path = "dist/M3U8Downloader"
            print(f"Executable: {exe_path}")
        
        # Check file size
        if system == "Windows" and os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"File size: {size_mb:.1f} MB")
        
        if ffmpeg_path:
            print(f"\nSUCCESS: Self-contained executable created!")
            print(f"- FFmpeg is bundled inside")
            print(f"- No additional software required for users")
            print(f"- Ready for distribution")
        else:
            print(f"\nWARNING: Build completed, but FFmpeg not bundled")
            print(f"   Users will need to install FFmpeg separately")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: Build failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\nNext Steps:")
        print("1. Test the executable on a clean system")
        print("2. Distribute the single file")
        print("3. Users can run it immediately!")
    else:
        print("\nTroubleshooting:")
        print("1. Install missing dependencies")
        print("2. Check internet connection (for FFmpeg download)")
        print("3. Run as administrator if needed")
