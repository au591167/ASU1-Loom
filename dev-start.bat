@echo off
REM ASU1-Loom Development Launcher (Windows)
REM Quick start script for Windows users

echo.
echo ========================================
echo   ASU1-Loom Development Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

echo Starting ASU1-Loom...
echo.

REM Run the Python launcher
python dev-launcher.py

pause
