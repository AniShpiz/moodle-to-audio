"""
Moodle Video to MP3 Converter
=============================
Downloads authenticated videos from Moodle and converts them to MP3.

Usage:
1. Run the JS snippet in your browser console on the Moodle video page
2. Paste the extracted links into links.txt
3. Run: python download_and_convert.py
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if yt-dlp is installed."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ytdlp():
    """Install yt-dlp via pip."""
    print("Installing yt-dlp...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp"], check=True)

def download_and_convert():
    # Check dependencies
    if not check_dependencies():
        install_ytdlp()
    
    # Check for links file
    if not os.path.exists("links.txt"):
        print("❌ Error: links.txt not found!")
        print("\nלא נמצא קובץ links.txt")
        print("הדבק את הלינקים שחילצת מהדפדפן לתוך links.txt")
        return
    
    # Read and count links
    with open("links.txt", "r") as f:
        links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    
    if not links:
        print("❌ links.txt is empty!")
        return
    
    print(f"🎬 Found {len(links)} video links")
    print("📥 Starting download with browser cookies...")
    print("-" * 50)
    
    # Create output folder
    os.makedirs("mp3_output", exist_ok=True)
    
    # yt-dlp command with browser cookies for authentication
    command = [
        "yt-dlp",
        "--cookies-from-browser", "chrome",   # Use Chrome cookies for auth
        "-x",                                  # Extract audio only
        "--audio-format", "mp3",               # Convert to MP3
        "--audio-quality", "192K",             # Good quality for transcription
        "-o", "mp3_output/%(title)s.%(ext)s",  # Output to mp3_output folder
        "--no-playlist",                       # Don't treat as playlist
        "--retries", "3",                      # Retry on failure
        "-a", "links.txt"                      # Batch input file
    ]
    
    try:
        subprocess.run(command, check=True)
        print("\n" + "=" * 50)
        print("✅ Success! All MP3 files are in the 'mp3_output' folder")
        print("🎧 Ready for NotebookLM!")
        
        # List output files
        mp3_files = [f for f in os.listdir("mp3_output") if f.endswith(".mp3")]
        print(f"\n📁 Created {len(mp3_files)} MP3 files:")
        for f in mp3_files[:10]:  # Show first 10
            print(f"   • {f}")
        if len(mp3_files) > 10:
            print(f"   ... and {len(mp3_files) - 10} more")
            
    except subprocess.CalledProcessError as e:
        print("\n❌ Error during download/conversion")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome is closed (cookies can't be read while Chrome is open)")
        print("2. Try with Edge instead: change 'chrome' to 'edge' in the script")
        print("3. Make sure FFmpeg is installed and in PATH")
        print(f"\nError details: {e}")

if __name__ == "__main__":
    download_and_convert()
