#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
One-time Chrome launcher for FJ Service Center
Launches Chrome in full screen mode only once, then creates a flag file
"""

import os
import subprocess
import time
import sys
import platform

# Determine flag file location based on OS
if platform.system() == "Windows":
    FLAG_FILE = os.path.join(os.getcwd(), ".chrome_launched")
else:
    FLAG_FILE = "/home/runner/workspace/.chrome_launched"

def safe_print(message):
    """Print message with proper encoding handling"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        safe_message = message.encode('ascii', 'ignore').decode('ascii')
        print(safe_message)

def launch_chrome_once():
    """Launch Chrome in full screen mode only if not already launched"""
    
    # Check if Chrome was already launched
    if os.path.exists(FLAG_FILE):
        safe_print("Chrome sudah pernah diluncurkan. Buka manual: http://localhost:5001")
        return False
    
    safe_print("Meluncurkan Chrome dalam mode full screen...")
    
    # Chrome commands to try based on OS
    if platform.system() == "Windows":
        chrome_commands = [
            ['chrome', '--start-fullscreen', '--new-window', 'http://localhost:5001'],
            [r'C:\Program Files\Google\Chrome\Application\chrome.exe', '--start-fullscreen', '--new-window', 'http://localhost:5001'],
            [r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe', '--start-fullscreen', '--new-window', 'http://localhost:5001'],
        ]
    else:
        chrome_commands = [
            ['google-chrome', '--start-fullscreen', '--new-window', '--no-first-run', '--disable-default-browser-check', 'http://localhost:5001'],
            ['chromium-browser', '--start-fullscreen', '--new-window', '--no-first-run', '--disable-default-browser-check', 'http://localhost:5001'],
            ['chrome', '--start-fullscreen', '--new-window', 'http://localhost:5001'],
        ]
    
    for cmd in chrome_commands:
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, timeout=5)
            if result.returncode == 0:
                safe_print("Chrome berhasil diluncurkan dalam mode full screen!")
                # Create flag file
                with open(FLAG_FILE, 'w', encoding='utf-8') as f:
                    f.write(f"Chrome launched at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                return True
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    safe_print("Tidak dapat meluncurkan Chrome")
    safe_print("Silakan buka manual: http://localhost:5001")
    return False

def reset_chrome_flag():
    """Remove the Chrome launch flag to allow launching again"""
    if os.path.exists(FLAG_FILE):
        os.remove(FLAG_FILE)
        safe_print("Flag Chrome direset. Chrome akan diluncurkan lagi saat startup berikutnya.")
    else:
        safe_print("Flag Chrome sudah tidak ada.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_chrome_flag()
    else:
        launch_chrome_once()