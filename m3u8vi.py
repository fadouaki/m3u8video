#!/usr/bin/env python3
"""
M3U8 Video Downloader Script
Downloads video segments from M3U8 playlists and combines them into a single file.
"""

import requests
import os
import sys
from urllib.parse import urljoin, urlparse
import subprocess
import tempfile
import shutil
from pathlib import Path
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class M3U8Downloader:
    def __init__(self, headers=None, timeout=30):
        self.session = requests.Session()
        self.timeout = timeout
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if headers:
            self.session.headers.update(headers)
        else:
            # Default headers to mimic a browser
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            })
    
    def download_m3u8(self, m3u8_url, output_file, temp_dir=None):
        """
        Download video from M3U8 URL
        
        Args:
            m3u8_url (str): URL to the M3U8 playlist
            output_file (str): Output video file path
            temp_dir (str): Temporary directory for segments (optional)
        """
        try:
            print(f"Fetching M3U8 playlist: {m3u8_url}")
            
            # Test connectivity first
            print("Testing connection...")
            
            # Get the M3U8 playlist with timeout
            response = self.session.get(m3u8_url, timeout=self.timeout)
            response.raise_for_status()
            
            print("✓ Successfully connected to server")
            
            playlist_content = response.text
            print(f"✓ Playlist downloaded ({len(playlist_content)} bytes)")
            
            # Show playlist preview for debugging
            print("\n--- Playlist Preview ---")
            lines = playlist_content.strip().split('\n')
            for i, line in enumerate(lines[:10]):  # Show first 10 lines
                print(f"{i+1:2d}: {line}")
            if len(lines) > 10:
                print("    ... (truncated)")
            print("--- End Preview ---\n")
            
            base_url = self._get_base_url(m3u8_url)
            print(f"Base URL: {base_url}")
            
            # Parse segments from playlist
            segments = self._parse_playlist(playlist_content, base_url)
            
            if not segments:
                print("❌ No video segments found in the playlist")
                print("Playlist content preview:")
                print(playlist_content[:500] + "..." if len(playlist_content) > 500 else playlist_content)
                return False
            
            print(f"✓ Found {len(segments)} segments")
            
            # Show first few segment URLs for debugging
            print("First few segments:")
            for i, seg in enumerate(segments[:3]):
                print(f"  {i+1}: {seg}")
            
            # Create temporary directory for segments
            if temp_dir is None:
                temp_dir = tempfile.mkdtemp()
            
            os.makedirs(temp_dir, exist_ok=True)
            print(f"Using temp directory: {temp_dir}")
            
            # Download all segments
            segment_files = []
            failed_count = 0
            
            for i, segment_url in enumerate(segments):
                segment_file = os.path.join(temp_dir, f"segment_{i:05d}.ts")
                
                print(f"Downloading segment {i+1}/{len(segments)}: {os.path.basename(segment_url)}")
                
                if self._download_segment(segment_url, segment_file):
                    segment_files.append(segment_file)
                    # Show file size
                    size = os.path.getsize(segment_file)
                    print(f"  ✓ Downloaded {size} bytes")
                else:
                    failed_count += 1
                    print(f"  ❌ Failed to download segment {i+1}")
                    
                    # Stop if too many failures
                    if failed_count > len(segments) * 0.1:  # More than 10% failed
                        print(f"Too many failures ({failed_count}), stopping download")
                        break
            
            if not segment_files:
                print("❌ No segments were downloaded successfully")
                return False
            
            print(f"✓ Successfully downloaded {len(segment_files)}/{len(segments)} segments")
            
            # Combine segments using ffmpeg
            print("Combining segments...")
            success = self._combine_segments(segment_files, output_file)
            
            # Cleanup temporary files
            print("Cleaning up temporary files...")
            shutil.rmtree(temp_dir)
            
            if success:
                print(f"✓ Video downloaded successfully: {output_file}")
                return True
            else:
                print("❌ Failed to combine segments")
                return False
                
        except requests.exceptions.ConnectTimeout:
            print(f"❌ Connection timeout to {urlparse(m3u8_url).netloc}")
            print("Possible solutions:")
            print("1. Check your internet connection")
            print("2. Try using a VPN if the content is geo-restricted")
            print("3. Check if the URL is correct and accessible")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error: {str(e)}")
            print("The server might be down or the URL might be incorrect")
            return False
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP error: {str(e)}")
            if e.response.status_code == 403:
                print("Access forbidden - you might need authentication or the content is restricted")
            elif e.response.status_code == 404:
                print("File not found - check if the URL is correct")
            return False
        except Exception as e:
            print(f"❌ Error downloading video: {str(e)}")
            return False
    
    def _get_base_url(self, url):
        """Get base URL for resolving relative segment URLs"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{'/'.join(parsed.path.split('/')[:-1])}/"
    
    def _parse_playlist(self, playlist_content, base_url):
        """Parse M3U8 playlist and handle both master and media playlists"""
        lines = playlist_content.strip().split('\n')
        
        # Check if this is a master playlist (contains variant streams)
        is_master_playlist = any('#EXT-X-STREAM-INF' in line for line in lines)
        
        if is_master_playlist:
            print("Variant playlist detected. Selecting the highest resolution stream.")
            return self._parse_master_playlist(lines, base_url)
        else:
            print("Media playlist detected. Parsing segments.")
            return self._parse_media_playlist(lines, base_url)
    
    def _parse_master_playlist(self, lines, base_url):
        """Parse master playlist and return the highest quality stream URL"""
        streams = []
        
        for i, line in enumerate(lines):
            if line.startswith('#EXT-X-STREAM-INF'):
                # Next line should be the stream URL
                if i + 1 < len(lines):
                    stream_url = lines[i + 1].strip()
                    
                    # Extract bandwidth/resolution info
                    bandwidth = 0
                    resolution = ""
                    
                    if 'BANDWIDTH=' in line:
                        try:
                            bandwidth = int(line.split('BANDWIDTH=')[1].split(',')[0])
                        except:
                            pass
                    
                    if 'RESOLUTION=' in line:
                        try:
                            resolution = line.split('RESOLUTION=')[1].split(',')[0]
                        except:
                            pass
                    
                    # Convert relative URL to absolute
                    if not stream_url.startswith('http'):
                        stream_url = urljoin(base_url, stream_url)
                    
                    streams.append({
                        'url': stream_url,
                        'bandwidth': bandwidth,
                        'resolution': resolution
                    })
        
        if not streams:
            raise Exception("No valid streams found in master playlist")
        
        # Select the highest bandwidth stream
        best_stream = max(streams, key=lambda x: x['bandwidth'])
        
        print(f"Available streams: {len(streams)}")
        for stream in streams:
            marker = " (SELECTED)" if stream == best_stream else ""
            print(f"  - {stream['resolution']} @ {stream['bandwidth']} bps{marker}")
        
        print(f"Selected stream URL: {best_stream['url']}")
        
        # Now fetch and parse the selected stream playlist
        return self._fetch_and_parse_media_playlist(best_stream['url'])
    
    def _fetch_and_parse_media_playlist(self, playlist_url):
        """Fetch a media playlist and parse its segments"""
        try:
            print(f"Fetching media playlist: {playlist_url}")
            response = self.session.get(playlist_url, timeout=self.timeout)
            response.raise_for_status()
            
            playlist_content = response.text
            base_url = self._get_base_url(playlist_url)
            
            lines = playlist_content.strip().split('\n')
            return self._parse_media_playlist(lines, base_url)
            
        except Exception as e:
            raise Exception(f"Error fetching the M3U8 playlist: {str(e)}")
    
    def _parse_media_playlist(self, lines, base_url):
        """Parse media playlist and extract segment URLs"""
        segments = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # This is a segment URL
                if line.startswith('http'):
                    segments.append(line)
                else:
                    # Relative URL, join with base URL
                    segments.append(urljoin(base_url, line))
        
        return segments
    
    def _download_segment(self, segment_url, output_file, max_retries=3):
        """Download a single segment with retry logic"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(segment_url, stream=True, timeout=self.timeout)
                response.raise_for_status()
                
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return True
                
            except requests.exceptions.Timeout:
                print(f"    Timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"    Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        return False
    
    def _combine_segments(self, segment_files, output_file):
        """Combine TS segments using ffmpeg"""
        try:
            # Create a text file listing all segments
            list_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            
            for segment_file in segment_files:
                list_file.write(f"file '{segment_file}'\n")
            
            list_file.close()
            
            # Use ffmpeg to concatenate segments
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', list_file.name,
                '-c', 'copy',
                '-y',  # Overwrite output file
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up the list file
            os.unlink(list_file.name)
            
            if result.returncode == 0:
                return True
            else:
                print(f"ffmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("ffmpeg not found. Please install ffmpeg to combine segments.")
            print("Alternative: Use the downloaded segments manually")
            return False
        except Exception as e:
            print(f"Error combining segments: {str(e)}")
            return False

def test_url_connectivity(url):
    """Test if a URL is accessible"""
    try:
        print(f"Testing connectivity to: {url}")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = session.head(url, timeout=10)
        print(f"✓ Server responded with status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ URL is accessible")
            return True
        else:
            print(f"⚠ URL returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - server may be down or slow")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - check URL and internet connection")
        return False
    except Exception as e:
        print(f"❌ Error testing URL: {str(e)}")
        return False

def main():
    # Option 1: Use command line arguments
    if len(sys.argv) >= 3:
        m3u8_url = sys.argv[1]
        output_file = sys.argv[2]
        temp_dir = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Option 2: Set URLs directly for VS Code Run button
    else:
        # Replace these with your actual URLs
        m3u8_url = "http://sample.vodobox.net/skate_phantom_flex_4k/skate_phantom_flex_4k.m3u8"
        output_file = "downloaded_video.mp4"
        temp_dir = None
        
        if m3u8_url == "https://your-m3u8-url-here.m3u8":
            print("Please edit the script and replace 'your-m3u8-url-here.m3u8' with your actual M3U8 URL")
            print("Or use command line: python m3u8_downloader.py <m3u8_url> <output_file>")
            sys.exit(1)
    
    # Test connectivity first
    print("=== Testing URL connectivity ===")
    if not test_url_connectivity(m3u8_url):
        print("URL test failed. Proceeding anyway...")
    
    print("\n=== Starting download ===")
    
    # Optional: Add custom headers if needed for authentication
    headers = {
        # 'Authorization': 'Bearer your_token_here',
        # 'Referer': 'https://example.com',
    }
    
    downloader = M3U8Downloader(headers=headers, timeout=30)
    success = downloader.download_m3u8(m3u8_url, output_file, temp_dir)
    
    if success:
        print("Download completed successfully!")
    else:
        print("Download failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()