#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows-specific startup script for FJ Service Center
Handles encoding issues and Windows Chrome paths
"""

import os
import sys
import subprocess
import time
import platform
from threading import Thread

# Set UTF-8 encoding for Windows console
if platform.system() == "Windows":
    os.system("chcp 65001 >nul")

def safe_print(message):
    """Print with encoding safety"""
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode('ascii', 'ignore').decode('ascii'))

def launch_chrome_windows():
    """Launch Chrome on Windows with full screen"""
    time.sleep(3)  # Wait for server
    
    safe_print("Mencoba meluncurkan Chrome...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    # Try specific paths first
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            try:
                subprocess.Popen([
                    chrome_path, 
                    "--start-fullscreen", 
                    "--new-window", 
                    "http://localhost:5001"
                ])
                safe_print("Chrome berhasil diluncurkan!")
                return True
            except Exception:
                continue
    
    # Try system PATH
    try:
        subprocess.Popen(["chrome", "--start-fullscreen", "--new-window", "http://localhost:5001"])
        safe_print("Chrome diluncurkan dari PATH")
        return True
    except Exception:
        pass
    
    safe_print("Tidak dapat meluncurkan Chrome otomatis")
    safe_print("Silakan buka manual: http://localhost:5001")
    return False

def print_banner():
    """Print startup banner"""
    safe_print("=" * 60)
    safe_print("FJ SERVICE CENTER - INVOICE MANAGEMENT SYSTEM")
    safe_print("=" * 60)
    safe_print("Fitur:")
    safe_print("   - Buat dan kelola invoice service")
    safe_print("   - Database SQLite")
    safe_print("   - Generate PDF")
    safe_print("   - Tracking customer")
    safe_print("   - Interface bahasa Indonesia")
    safe_print("=" * 60)
    safe_print("Aplikasi berjalan di port 5001...")
    safe_print("Akses di: http://localhost:5001")
    safe_print("=" * 60)

def main():
    """Main function"""
    print_banner()
    
    # Start Chrome launcher in background
    chrome_thread = Thread(target=launch_chrome_windows, daemon=True)
    chrome_thread.start()
    
    # Import and run Flask app
    try:
        from app import app
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        safe_print("\nShutting down FJ Service Center...")
    except Exception as e:
        safe_print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()