@echo off
chcp 65001 >nul
echo ====================================================
echo FJ SERVICE CENTER - CHROME LAUNCHER
echo ====================================================
echo Mencoba meluncurkan Chrome dalam mode full screen...

REM Try different Chrome paths
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --start-fullscreen --new-window http://localhost:5001
    echo Chrome diluncurkan dari Program Files
    goto :end
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --start-fullscreen --new-window http://localhost:5001
    echo Chrome diluncurkan dari Program Files (x86)
    goto :end
)

REM Try system PATH
chrome --start-fullscreen --new-window http://localhost:5001 2>nul
if %errorlevel% == 0 (
    echo Chrome diluncurkan dari PATH
    goto :end
)

echo Tidak dapat menemukan Chrome
echo Silakan buka manual: http://localhost:5001

:end
echo ====================================================