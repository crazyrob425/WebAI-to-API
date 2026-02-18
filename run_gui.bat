@echo off
echo Starting WebAI-to-API Desktop GUI...
echo.

REM Check if PyQt6 is installed
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo Installing PyQt6...
    pip install PyQt6 requests
)

REM Run the GUI
cd /d "%~dp0"
python gui\app.py
pause

