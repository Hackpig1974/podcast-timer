@echo off
echo ========================================
echo Building Podcast Timer EXE
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Check if Pillow is installed (for icon creation)
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Pillow not found. Installing...
    pip install Pillow
    echo.
)

REM Create the icon if it doesn't exist
if not exist podcast_icon.ico (
    echo Creating application icon...
    python create_icon.py
    echo.
)

echo Building executable...
echo.

REM Build the EXE with PyInstaller
pyinstaller --onefile --windowed --name "PodcastTimer" --icon=podcast_icon.ico podcast_timer.py

echo.
echo ========================================
echo Build complete!
echo ========================================
echo.
echo The executable can be found in the 'dist' folder:
echo %CD%\dist\PodcastTimer.exe
echo.
echo Press any key to open the dist folder...
pause >nul
explorer dist
