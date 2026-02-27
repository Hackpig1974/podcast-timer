@echo off
echo ========================================
echo    Podcast Timer - Setup and Launch
echo ========================================
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet
echo.
echo Done! Launching Podcast Timer...
echo.
python podcast_timer.py

REM Only pause if there was an error
if errorlevel 1 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
)
