#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Startup script for FJ Service Center Application
Runs on port 5001 with auto-launch functionality
"""

import os
import sys
import subprocess
import time
import webbrowser
from threading import Thread

def print_banner():
    """Print startup banner"""
    print("="*60)
    print("🚀 FJ SERVICE CENTER - INVOICE MANAGEMENT SYSTEM")
    print("="*60)
    print("📋 Features:")
    print("   ✓ Create and manage service invoices")
    print("   ✓ SQLite database storage")
    print("   ✓ PDF generation")
    print("   ✓ Customer tracking")
    print("   ✓ Indonesian language interface")
    print("="*60)
    print("🌐 Application starting on port 5001...")
    print("📱 Access at: http://localhost:5001")
    print("="*60)

def open_browser_after_delay():
    """Launch Chrome in full screen mode once using dedicated launcher"""
    time.sleep(2)  # Wait for server to fully start
    try:
        # Use the dedicated Chrome launcher
        result = subprocess.run([sys.executable, 'chrome_launcher.py'], 
                              capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
    except Exception as e:
        print(f"ℹ️  Chrome launcher error: {e}")
        print("📱 Please manually open: http://localhost:5001")

def main():
    """Main startup function"""
    print_banner()
    
    # Start browser opener in background thread
    browser_thread = Thread(target=open_browser_after_delay, daemon=True)
    browser_thread.start()
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down FJ Service Center...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()