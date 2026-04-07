#!/bin/bash
# Deploy Bot Híbrido: Gemini + Claudio to VPS

set -e

VPS_USER="ubuntu"
VPS_HOST="tu-vps-ip"
APP_DIR="/opt/claudio-bot"
SERVICE_USER="claudio"

echo "=== Despliegue Bot Híbrido ==="

# Upload bot_hibrido.py and updated requirements
scp bot_hibrido.py requirements_hibrido.txt .env.hibrido.example \
    "${VPS_USER}@${VPS_HOST}:/tmp/"

ssh "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    cd $APP_DIR

    # Backup original bot
    cp bot_v2.py bot_v2.py.backup 2>/dev/null || true

    # Move new files
    mv /tmp/bot_hibrido.py ./
    mv /tmp/requirements_hibrido.txt ./requirements.txt
    mv /tmp/.env.hibrido.example ./.env.example

    # Install new dependencies
    sudo -u $SERVICE_USER venv/bin/pip install google-generativeai

    # Update systemd service for hybrid bot
    sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null << 'SVCEOF'
[Unit]
Description=Claudio Telegram Bot (Híbrido: Gemini + Claude)
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python bot_hibrido.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

    # Reload and restart
    sudo systemctl daemon-reload
    sudo systemctl restart claudio-telegram-bot

    # Check status
    sudo systemctl status claudio-telegram-bot --no-pager
ENDSSH

echo "✅ Bot Híbrido desplegado"
echo ""
echo "⚠️ Configura .env con GEMINI_API_KEY:"
echo "   ssh ${VPS_USER}@${VPS_HOST} 'sudo nano $APP_DIR/.env'"
