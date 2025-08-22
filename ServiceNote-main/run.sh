#!/bin/bash
echo "======================================================"
echo "🚀 FJ SERVICE CENTER - STARTING ON PORT 5001"
echo "======================================================"
echo "📋 Invoice Management System"
echo "✓ SQLite Database"
echo "✓ PDF Generation" 
echo "✓ 10-row Invoice Tables"
echo "✓ Indonesian Interface"
echo "✓ Chrome Auto-Launch Full Screen"
echo "======================================================"
echo "🌐 Application URL: http://localhost:5001"
echo "======================================================"

# Kill any existing processes on port 5001
pkill -f "port=5001" 2>/dev/null || true

# Start the application with Chrome auto-launch
cd /home/runner/workspace
python start_app.py