#!/bin/bash
# Claudio Bot - Quick Start Script for Linux/Mac

echo "======================================================================"
echo "  Claudio Bot - Starting..."
echo "======================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""

    echo "Installing dependencies..."
    venv/bin/pip install -q -r requirements.txt
    echo ""
fi

echo "======================================================================"
echo "  Starting Claudio Server and Telegram Bot"
echo "======================================================================"
echo ""

# Start Claudio Server
echo "[1/2] Starting Claudio Server..."
venv/bin/python claudio_complete.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Start Telegram Bot
echo "[2/2] Starting Telegram Bot..."
venv/bin/python bot_v2.py &
BOT_PID=$!

echo ""
echo "======================================================================"
echo "  Claudio is now running!"
echo "======================================================================"
echo ""
echo "Check your Telegram bot to start chatting."
echo ""
echo "Server PID: $SERVER_PID"
echo "Bot PID: $BOT_PID"
echo ""
echo "To stop: kill $SERVER_PID $BOT_PID"
echo "Or press Ctrl+C"
echo ""

# Wait for background processes
wait
