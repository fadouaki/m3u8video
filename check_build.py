#!/usr/bin/env python3
"""
Check if FFmpeg is properly bundled in the built executable
"""

import os
import sys
import platform

def check_build_results():
    """Check if the build included FFmpeg properly."""
    
    system = platform.system()
    print(f"Checking build results for {system}...")
    print("=" * 40)
    
    # Define expected paths based on platform
    if system == "Windows":
        if os.path.exists("dist/M3U8Downloader"):
            # Directory build
            exe_path = "dist/M3U8Downloader/M3U8Downloader.exe"
            bundle_dir = "dist/M3U8Downloader"
        else:
            # Single file build
            exe_path = "dist/M3U8Downloader.exe"
            bundle_dir = "dist"
        expected_ffmpeg = "ffmpeg.exe"
    elif system == "Darwin":
        exe_path = "dist/M3U8Downloader.app/Contents/MacOS/M3U8Downloader"
        bundle_dir = "dist/M3U8Downloader.app/Contents/MacOS"
        expected_ffmpeg = "ffmpeg"
    else:
        exe_path = "dist/M3U8Downloader/M3U8Downloader"
        bundle_dir = "dist/M3U8Downloader"
        expected_ffmpeg = "ffmpeg"
    
    # Check if executable exists
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✓ Executable found: {exe_path}")
        print(f"  Size: {size_mb:.1f} MB")
        
        # Check size to infer if FFmpeg is bundled
        if size_mb > 80:
            print(f"✓ Size suggests FFmpeg is bundled (>80MB)")
        else:
            print(f"⚠ Size suggests FFmpeg might NOT be bundled (<80MB)")
    else:
        print(f"✗ Executable NOT found: {exe_path}")
        return False
    
    # Check if FFmpeg binary exists in bundle directory
    ffmpeg_in_bundle = os.path.join(bundle_dir, expected_ffmpeg)
    if os.path.exists(ffmpeg_in_bundle):
        ffmpeg_size = os.path.getsize(ffmpeg_in_bundle) / (1024 * 1024)
        print(f"✓ FFmpeg found in bundle: {ffmpeg_in_bundle}")
        print(f"  FFmpeg size: {ffmpeg_size:.1f} MB")
    else:
        print(f"⚠ FFmpeg NOT found in bundle: {ffmpeg_in_bundle}")
        
        # List contents of bundle directory
        print(f"\nContents of {bundle_dir}:")
        if os.path.exists(bundle_dir):
            for item in os.listdir(bundle_dir):
                item_path = os.path.join(bundle_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path) / (1024 * 1024)
                    print(f"  {item} ({size:.1f} MB)")
                else:
                    print(f"  {item}/ (directory)")
    
    # Check if source FFmpeg exists (what should be bundled)
    source_ffmpeg = f"./{expected_ffmpeg}"
    if os.path.exists(source_ffmpeg):
        source_size = os.path.getsize(source_ffmpeg) / (1024 * 1024)
        print(f"\n✓ Source FFmpeg available: {source_ffmpeg} ({source_size:.1f} MB)")
    else:
        print(f"\n⚠ Source FFmpeg NOT found: {source_ffmpeg}")
        print("  This explains why FFmpeg wasn't bundled")
    
    return True

if __name__ == "__main__":
    check_build_results()
