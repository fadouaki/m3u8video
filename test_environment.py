#!/usr/bin/env python3
"""
Environment Test Script for M3U8 Downloader
Tests if all required dependencies are available for building.
"""

import sys
import os
import platform

def test_python_version():
    """Test Python version."""
    print(f"Python version: {sys.version}")
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 8:
        print("SUCCESS: Python version is compatible")
        return True
    else:
        print("ERROR: Python 3.8+ required")
        return False

def test_imports():
    """Test required imports."""
    tests_passed = 0
    total_tests = 0
    
    # Test core dependencies
    dependencies = [
        ("requests", "HTTP client"),
        ("m3u8", "M3U8 playlist parser"),
        ("tkinter", "GUI framework"),
    ]
    
    for module, description in dependencies:
        total_tests += 1
        try:
            __import__(module)
            print(f"SUCCESS: {module} - {description}")
            tests_passed += 1
        except ImportError as e:
            print(f"ERROR: {module} - {description} - {e}")
    
    # Test PyInstaller specifically
    total_tests += 1
    try:
        import PyInstaller
        import PyInstaller.__main__
        print(f"SUCCESS: PyInstaller {PyInstaller.__version__} - Executable builder")
        tests_passed += 1
    except ImportError as e:
        print(f"ERROR: PyInstaller - Executable builder - {e}")
    
    return tests_passed == total_tests

def test_platform_tools():
    """Test platform-specific tools."""
    system = platform.system()
    print(f"\nPlatform: {system} {platform.release()}")
    
    if system == "Windows":
        print("Windows-specific checks:")
        print("- Will download FFmpeg automatically during build")
        return True
    elif system == "Darwin":
        print("macOS-specific checks:")
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"SUCCESS: FFmpeg found: {ffmpeg_path}")
            return True
        else:
            print("ERROR: FFmpeg not found - install with: brew install ffmpeg")
            return False
    else:  # Linux
        print("Linux-specific checks:")
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"SUCCESS: FFmpeg found: {ffmpeg_path}")
            return True
        else:
            print("ERROR: FFmpeg not found - install with: sudo apt install ffmpeg")
            return False

def main():
    """Main test function."""
    print("M3U8 Downloader - Environment Test")
    print("=" * 50)
    
    # Test Python version
    python_ok = test_python_version()
    
    print("\nTesting imports...")
    imports_ok = test_imports()
    
    print("\nTesting platform tools...")
    platform_ok = test_platform_tools()
    
    print("\n" + "=" * 50)
    if python_ok and imports_ok and platform_ok:
        print("SUCCESS: ALL TESTS PASSED - Ready to build!")
        print("\nTo build the application, run:")
        print("  python build.py")
        return True
    else:
        print("ERROR: SOME TESTS FAILED - Please fix issues above")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        if platform.system() == "Darwin":
            print("  brew install ffmpeg")
        elif platform.system() not in ["Windows"]:
            print("  sudo apt install ffmpeg  # Ubuntu/Debian")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
