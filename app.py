import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import requests
import m3u8
import os
import subprocess
from urllib.parse import urljoin
import threading
import sys
import shutil
import tempfile
import platform

# --- Core Downloader Logic (adapted from your script) ---
# This function is mostly the same, but instead of printing to the console,
# it calls a logger function to update the GUI.

def get_ffmpeg_path():
    """Get the FFmpeg executable path based on the platform and environment."""
    # First, try to find ffmpeg in the system PATH
    if platform.system() == "Windows":
        ffmpeg_names = ["ffmpeg.exe", "ffmpeg"]
    else:
        ffmpeg_names = ["ffmpeg"]
    
    # Check if ffmpeg is in PATH
    for name in ffmpeg_names:
        if shutil.which(name):
            return name
    
    # Check common installation paths
    common_paths = []
    if platform.system() == "Darwin":  # macOS
        common_paths = [
            "/opt/homebrew/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/local/bin/ffmpeg"
        ]
    elif platform.system() == "Windows":
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"
        ]
    else:  # Linux
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/snap/bin/ffmpeg"
        ]
    
    # Check if ffmpeg exists in common paths
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # If running as PyInstaller bundle, check if ffmpeg is bundled with the app
    if getattr(sys, 'frozen', False):
        bundle_dir = os.path.dirname(sys.executable)
        if platform.system() == "Windows":
            bundled_ffmpeg = os.path.join(bundle_dir, "ffmpeg.exe")
        else:
            bundled_ffmpeg = os.path.join(bundle_dir, "ffmpeg")
        
        if os.path.exists(bundled_ffmpeg):
            return bundled_ffmpeg
    
    # Return default name and let subprocess handle the error
    return "ffmpeg"

def get_temp_directory():
    """Get a writable temporary directory."""
    try:
        # Try to create a temp directory in the system temp folder
        temp_dir = tempfile.mkdtemp(prefix="m3u8_segments_")
        return temp_dir
    except:
        # Fallback to user's home directory
        home_dir = os.path.expanduser("~")
        temp_dir = os.path.join(home_dir, "temp_video_segments")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

def download_m3u8_video(m3u8_url, output_filename, log_callback):
    """
    Downloads a video from an M3U8 playlist.

    Args:
        m3u8_url (str): The URL of the M3U8 playlist.
        output_filename (str): The name of the output video file.
        log_callback (function): A function to call for logging messages to the GUI.
    """
    temp_dir = None
    try:
        log_callback("Fetching the M3U8 playlist...")
        response = requests.get(m3u8_url, timeout=15)
        response.raise_for_status()
        playlist = m3u8.loads(response.text, uri=m3u8_url)

        media_playlist = playlist
        if playlist.is_variant:
            log_callback("Variant playlist detected. Selecting the highest resolution stream.")
            sorted_playlists = sorted(
                playlist.playlists,
                key=lambda p: p.stream_info.resolution[0] * p.stream_info.resolution[1] if p.stream_info.resolution else 0,
                reverse=True
            )
            if not sorted_playlists:
                log_callback("Error: No streams with resolution info found.")
                return
            
            media_playlist_url = sorted_playlists[0].absolute_uri
            log_callback(f"Selected stream URL: {media_playlist_url}")
            
            response = requests.get(media_playlist_url)
            response.raise_for_status()
            media_playlist = m3u8.loads(response.text, uri=media_playlist_url)

        # Use a proper temporary directory
        temp_dir = get_temp_directory()
        log_callback(f"Using temporary directory: {temp_dir}")

        log_callback(f"Found {len(media_playlist.segments)} video segments.")
        segment_filenames = []
        for i, segment in enumerate(media_playlist.segments):
            segment_url = segment.absolute_uri
            segment_filename = os.path.join(temp_dir, f"segment_{i:05d}.ts")
            segment_filenames.append(segment_filename)

            log_callback(f"Downloading segment {i+1}/{len(media_playlist.segments)}...")
            try:
                segment_response = requests.get(segment_url, timeout=10, stream=True)
                segment_response.raise_for_status()
                with open(segment_filename, 'wb') as f:
                    for chunk in segment_response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except requests.exceptions.RequestException as e:
                log_callback(f"Error downloading segment {i+1}: {e}")
                continue

        log_callback("All segments downloaded. Combining into a single file using FFmpeg...")
        
        filelist_path = os.path.join(temp_dir, "filelist.txt")
        with open(filelist_path, 'w', encoding='utf-8') as f:
            for seg_file in segment_filenames:
                f.write(f"file '{os.path.abspath(seg_file)}'\n")

        # Get the appropriate FFmpeg path
        ffmpeg_path = get_ffmpeg_path()
        log_callback(f"Using FFmpeg: {ffmpeg_path}")
        
        ffmpeg_command = [
            ffmpeg_path, '-f', 'concat', '-safe', '0', '-i', filelist_path,
            '-c', 'copy', '-y', output_filename
        ]

        # Use subprocess.run to execute FFmpeg
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True, encoding='utf-8', errors='ignore')

        if result.returncode == 0:
            log_callback(f"Video saved successfully as {output_filename}")
        else:
            log_callback("ERROR: FFmpeg failed to combine video segments.")
            log_callback(f"FFmpeg stderr: {result.stderr}")
            # Try to find FFmpeg if not in PATH
            if "No such file or directory" in result.stderr or "not found" in result.stderr or "command not found" in result.stderr:
                log_callback("\nERROR: FFmpeg not found. Please install FFmpeg and ensure it's in your system's PATH.")
                log_callback("Download FFmpeg from: https://ffmpeg.org/download.html")
                log_callback("Or place ffmpeg executable next to this application.")

    except requests.exceptions.RequestException as e:
        log_callback(f"Error fetching the M3U8 playlist: {e}")
    except Exception as e:
        log_callback(f"An unexpected error occurred: {e}")
        import traceback
        log_callback(f"Traceback: {traceback.format_exc()}")
    finally:
        # Clean up temp files
        if temp_dir and os.path.exists(temp_dir):
            try:
                log_callback("Cleaning up temporary files...")
                shutil.rmtree(temp_dir)
                log_callback("Cleanup complete.")
            except Exception as e:
                log_callback(f"Warning: Could not clean up temporary files: {e}")


# --- GUI Application Class ---

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("M3U8 Video Downloader")
        self.geometry("600x450")
        self.configure(bg="#2e2e2e")

        # --- Styles ---
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#2e2e2e", foreground="white", font=("Arial", 10))
        style.configure("TButton", background="#4a4a4a", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("TButton", background=[("active", "#6a6a6a")])
        style.configure("TEntry", fieldbackground="#4a4a4a", foreground="white", borderwidth=1)
        
        # --- Widgets ---
        self.url_label = ttk.Label(self, text="M3U8 URL:")
        self.url_label.pack(pady=(10, 0), padx=10, anchor="w")

        self.url_entry = ttk.Entry(self, width=80)
        self.url_entry.pack(pady=5, padx=10, fill="x")

        self.download_button = ttk.Button(self, text="Download Video", command=self.start_download_thread)
        self.download_button.pack(pady=10, padx=10)

        self.log_area = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD, bg="#1e1e1e", fg="white", font=("Courier New", 9))
        self.log_area.pack(pady=10, padx=10, expand=True, fill="both")

        # Test FFmpeg availability on startup
        self.after(100, self.test_ffmpeg)

    def test_ffmpeg(self):
        """Test if FFmpeg is available and show status."""
        try:
            ffmpeg_path = get_ffmpeg_path()
            result = subprocess.run([ffmpeg_path, '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.log(f"✓ FFmpeg found: {version_line}")
            else:
                self.log("⚠ FFmpeg found but may have issues")
        except Exception as e:
            self.log("⚠ FFmpeg not found or not working properly")
            self.log("Please install FFmpeg for video processing")
            self.log("Download from: https://ffmpeg.org/download.html")

    def log(self, message):
        """Appends a message to the log area in a thread-safe way."""
        def update_log():
            self.log_area.config(state='normal')
            self.log_area.insert(tk.END, str(message) + '\n')
            self.log_area.config(state='disabled')
            self.log_area.see(tk.END)  # Auto-scroll
        
        # Ensure this runs on the main thread
        if threading.current_thread() == threading.main_thread():
            update_log()
        else:
            self.after(0, update_log)

    def start_download_thread(self):
        """Starts the download process in a separate thread to keep the GUI responsive."""
        m3u8_url = self.url_entry.get().strip()
        if not m3u8_url:
            self.log("Please enter an M3U8 URL.")
            return

        output_filename = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
            title="Save Video As"
        )
        if not output_filename:
            self.log("Download cancelled by user.")
            return

        self.download_button.config(state='disabled', text="Downloading...")
        self.log_area.config(state='normal')
        self.log_area.delete(1.0, tk.END)  # Clear log
        self.log_area.config(state='disabled')

        # Run the download function in a new thread
        download_thread = threading.Thread(
            target=self.run_download,
            args=(m3u8_url, output_filename),
            daemon=True
        )
        download_thread.start()

    def run_download(self, m3u8_url, output_filename):
        """The actual function that the thread will execute."""
        try:
            download_m3u8_video(m3u8_url, output_filename, self.log)
        except Exception as e:
            self.log(f"Unexpected error in download thread: {e}")
        finally:
            # When done, re-enable the button (must be done on main thread)
            self.after(0, lambda: self.download_button.config(state='normal', text="Download Video"))


if __name__ == "__main__":
    app = App()
    app.mainloop()
