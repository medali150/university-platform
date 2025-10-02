@echo off
echo ================================================
echo           DATABASE CLEANUP UTILITY
echo ================================================
echo.

cd /d "%~dp0"

echo Choose an option:
echo 1. Safe clear (with confirmation)
echo 2. Quick clear (no confirmation)
echo 3. Cancel
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Running safe database clear...
    python clear_database.py
) else if "%choice%"=="2" (
    echo.
    echo Running quick database clear...
    python quick_clear.py
) else if "%choice%"=="3" (
    echo Operation cancelled.
) else (
    echo Invalid choice. Please run the script again.
)

echo.
pause