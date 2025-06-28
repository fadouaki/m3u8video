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
    
    # FFmpeg download URL (reliable source)
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
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
                        print("\r   Progress: {:.1f}%".format(percent), end="", flush=True)
        
        print("\n   Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find ffmpeg.exe in extracted files
        for root, dirs, files in os.walk(temp_dir):
            if 'ffmpeg.exe' in files:
                ffmpeg_source = os.path.join(root, 'ffmpeg.exe')
                ffmpeg_dest = os.path.join(os.getcwd(), 'ffmpeg.exe')
                shutil.copy2(ffmpeg_source, ffmpeg_dest)
                print("SUCCESS: FFmpeg downloaded to: {}".format(ffmpeg_dest))
                return ffmpeg_dest
        
        raise Exception("FFmpeg.exe not found in downloaded archive")

def get_bundleable_ffmpeg():
    """Get FFmpeg that can be bundled with PyInstaller."""
    system = platform.system()
    
    # For bundling, we need a local copy that we can redistribute
    # First check if we already have a local bundleable copy
    if system == "Windows":
        local_bundleable = "./ffmpeg.exe"
    else:
        local_bundleable = "./ffmpeg"
    
    if os.path.exists(local_bundleable):
        print("SUCCESS: Found bundleable FFmpeg: {}".format(local_bundleable))
        return local_bundleable
    
    # For Windows, download FFmpeg
    if system == "Windows":
        try:
            return download_ffmpeg_windows()
        except Exception as e:
            print("ERROR: Failed to download FFmpeg: {}".format(e))
            return None
    
    # For macOS, copy system FFmpeg to local directory for bundling
    elif system == "Darwin":
        system_ffmpeg = shutil.which("ffmpeg")
        if not system_ffmpeg:
            # Try common paths
            common_paths = [
                "/opt/homebrew/bin/ffmpeg",
                "/usr/local/bin/ffmpeg"
            ]
            for path in common_paths:
                if os.path.exists(path):
                    system_ffmpeg = path
                    break
        
        if system_ffmpeg:
            print("Found system FFmpeg: {}".format(system_ffmpeg))
            print("Copying to local directory for bundling...")
            shutil.copy2(system_ffmpeg, "./ffmpeg")
            print("SUCCESS: FFmpeg copied for bundling: ./ffmpeg")
            return "./ffmpeg"
        else:
            print("ERROR: FFmpeg not found on macOS")
            print("   Install with: brew install ffmpeg")
            return None
    
    # For Linux, copy system FFmpeg to local directory for bundling
    else:
        system_ffmpeg = shutil.which("ffmpeg")
        if not system_ffmpeg:
            system_ffmpeg = "/usr/bin/ffmpeg"
        
        if os.path.exists(system_ffmpeg):
            print("Found system FFmpeg: {}".format(system_ffmpeg))
            print("Copying to local directory for bundling...")
            shutil.copy2(system_ffmpeg, "./ffmpeg")
            print("SUCCESS: FFmpeg copied for bundling: ./ffmpeg")
            return "./ffmpeg"
        else:
            print("ERROR: FFmpeg not found on Linux")
            print("   Install with: sudo apt install ffmpeg")
            return None

def main():
    """Main build function with auto-bundle."""
    system = platform.system()
    
    print("M3U8 Downloader - Auto-Bundle Build")
    print("=" * 50)
    
    # Step 1: Ensure FFmpeg is available for bundling
    print("\nStep 1: Preparing FFmpeg for bundling...")
    ffmpeg_path = get_bundleable_ffmpeg()
    
    if not ffmpeg_path:
        print("ERROR: Could not locate or download FFmpeg")
        print("   The app will still build, but users will need FFmpeg installed")
        ffmpeg_path = None
    else:
        print("SUCCESS: FFmpeg ready: {}".format(ffmpeg_path))
    
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
        '--onedir',   # Changed from --onefile to fix DLL issues
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
        build_options.append('--add-binary={}{}.'.format(ffmpeg_path, data_sep))
        print("INFO: FFmpeg will be bundled with the executable!")
    
    # Add icon if available
    if icon_arg and (
        (system == 'Darwin' and os.path.exists('app_icon.icns')) or
        (system == 'Windows' and os.path.exists('app_icon.ico'))
    ):
        build_options.append(icon_arg)
    
    # Add data files
    if os.path.exists('app_icon.ico'):
        build_options.append('--add-data=app_icon.ico{}.'.format(data_sep))
    
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
        build_options.append('--exclude-module={}'.format(module))
    
    print("Build configuration:")
    for option in build_options:
        if '--add-binary=' in option and 'ffmpeg' in option:
            print("  {} <- FFmpeg bundled!".format(option))
        else:
            print("  {}".format(option))
    
    # Step 3: Build the application
    print("\nStep 3: Building executable...")
    
    try:
        PyInstaller.__main__.run(build_options)
        
        # Step 4: Verify the build
        print("\nSUCCESS: Build completed successfully!")
        
        if system == "Windows":
            exe_path = "dist/M3U8Downloader/M3U8Downloader.exe"
            print("Executable: {}".format(exe_path))
        elif system == "Darwin":
            app_path = "dist/M3U8Downloader.app"
            exe_path = "dist/M3U8Downloader.app/Contents/MacOS/M3U8Downloader"
            print("Application: {}".format(app_path))
        else:
            exe_path = "dist/M3U8Downloader/M3U8Downloader"
            print("Executable: {}".format(exe_path))
        
        # Check file size
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print("File size: {:.1f} MB".format(size_mb))
            
            # If FFmpeg was bundled, size should be much larger
            if ffmpeg_path and size_mb < 80:
                print("WARNING: Size seems small for bundled FFmpeg. Check if bundling worked.")
            elif ffmpeg_path and size_mb > 80:
                print("CONFIRMED: FFmpeg appears to be successfully bundled (large size)")
        else:
            print("WARNING: Could not find executable at {}".format(exe_path))
        
        if ffmpeg_path:
            print("\nSUCCESS: Self-contained executable created!")
            print("- FFmpeg is bundled inside")
            print("- No additional software required for users")
            print("- Ready for distribution")
        else:
            print("\nWARNING: Build completed, but FFmpeg not bundled")
            print("   Users will need to install FFmpeg separately")
        
        return True
        
    except Exception as e:
        print("\nERROR: Build failed: {}".format(e))
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
