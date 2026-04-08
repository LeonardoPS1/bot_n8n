@echo off
REM Claudio Bot - Quick Start Script for Windows

echo ======================================================================
echo   Claudio Bot - Starting...
echo ======================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.

    echo Installing dependencies...
    call venv\Scripts\activate
    pip install -q -r requirements.txt
    echo.
) else (
    call venv\Scripts\activate
)

echo ======================================================================
echo   Starting Claudio Server and Telegram Bot
echo ======================================================================
echo.

REM Start Claudio Server
echo [1/2] Starting Claudio Server on port %CLADIO_PORT%...
start "Claudio Server" cmd /k "venv\Scripts\python claudio_complete.py"

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Start Telegram Bot
echo [2/2] Starting Telegram Bot...
start "Claudio Bot" cmd /k "venv\Scripts\python bot_v2.py"

echo.
echo ======================================================================
echo   Claudio is now running!
echo ======================================================================
echo.
echo Check your Telegram bot to start chatting.
echo.
echo To stop: Close the windows or press Ctrl+C in each window.
echo.
pause
