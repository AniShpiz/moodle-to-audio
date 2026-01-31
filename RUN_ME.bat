@echo off
echo ========================================
echo   Moodle Video to MP3 Converter
echo ========================================
echo.

REM Check if links.txt has content
findstr /r /c:"[a-zA-Z]" links.txt >nul 2>&1
if errorlevel 1 (
    echo ERROR: links.txt is empty or missing!
    echo.
    echo Please paste the video links into links.txt first.
    echo.
    pause
    exit /b
)

echo Starting download and conversion...
echo Make sure Chrome is CLOSED for cookie access!
echo.
python download_and_convert.py

echo.
echo ========================================
echo Done! Check the mp3_output folder.
echo ========================================
pause
