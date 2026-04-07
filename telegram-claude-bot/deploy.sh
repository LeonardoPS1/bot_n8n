#!/bin/bash
# Deploy Claudio Server + Telegram Bot to VPS
# Run this from Git Bash on Windows or directly on VPS

set -e

# VPS Configuration
VPS_USER="ubuntu"
VPS_HOST="51.222.207.250"
VPS_PORT="22"
APP_DIR="/opt/claudio-bot"
SERVICE_USER="claudio"

# SSH key and options for automated deployment
SSH_KEY="$HOME/.ssh/claude_bot"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p $VPS_PORT"
SCP_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P $VPS_PORT"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Claudio Server + Telegram Bot Deployment ===${NC}"
echo "VPS: ${VPS_USER}@${VPS_HOST}"
echo "Directory: $APP_DIR"
echo ""

echo -e "${YELLOW}Step 1: Prepare VPS${NC}"
ssh $SSH_OPTS "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    # Update system
    sudo apt-get update && sudo apt-get upgrade -y

    # Install dependencies
    sudo apt-get install -y python3 python3-pip python3-venv git

    # Create service user
    sudo useradd -m -s /bin/bash $SERVICE_USER || true

    # Create app directory
    sudo mkdir -p $APP_DIR
    sudo chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR

    # Create log directory
    sudo mkdir -p /var/log/claudio-bot
    sudo chown -R $SERVICE_USER:$SERVICE_USER /var/log/claudio-bot
ENDSSH

echo -e "${YELLOW}Step 2: Upload files${NC}"
# Upload application files
scp $SCP_OPTS claudio_server.py bot_v2.py requirements.txt ".env.example" "${VPS_USER}@${VPS_HOST}:~/"
ssh $SSH_OPTS "${VPS_USER}@${VPS_HOST}" "mv ~/claudio_server.py ~/bot_v2.py ~/requirements.txt ~/.env.example $APP_DIR/"

echo -e "${YELLOW}Step 3: Setup Python environment${NC}"
ssh $SSH_OPTS "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    cd $APP_DIR

    # Create virtual environment
    sudo -u $SERVICE_USER python3 -m venv venv

    # Install dependencies
    sudo -u $SERVICE_USER venv/bin/pip install -r requirements.txt
ENDSSH

echo -e "${YELLOW}Step 4: Configure environment${NC}"
ssh $SSH_OPTS "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    cd $APP_DIR

    # Create .env from example if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "⚠️  .env file created from example. Please edit it with your API keys:"
        echo "   sudo nano $APP_DIR/.env"
    fi
ENDSSH

echo -e "${YELLOW}Step 5: Create systemd services${NC}"
ssh $SSH_OPTS "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    # Create Claudio Server service
    sudo tee /etc/systemd/system/claudio-server.service > /dev/null << 'SVCEOF'
[Unit]
Description=Claudio Server (Claude with n8n-MCP)
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python /opt/claudio-bot/claudio_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

    # Create Telegram Bot service
    sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null << 'SVCEOF'
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python /opt/claudio-bot/bot_v2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

    # Reload systemd
    sudo systemctl daemon-reload

    # Enable services
    sudo systemctl enable claudio-server.service
    sudo systemctl enable claudio-telegram-bot.service
ENDSSH

echo -e "${YELLOW}Step 6: Start services${NC}"
ssh $SSH_OPTS "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    # Start Claudio Server first
    sudo systemctl start claudio-server.service

    # Wait a moment for server to start
    sleep 3

    # Start Telegram Bot
    sudo systemctl start claudio-telegram-bot.service

    # Check status
    echo "=== Claudio Server Status ==="
    sudo systemctl status claudio-server.service --no-pager -l
    echo ""
    echo "=== Telegram Bot Status ==="
    sudo systemctl status claudio-telegram-bot.service --no-pager -l
ENDSSH

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env with your API keys:"
echo "      ssh ${VPS_USER}@${VPS_HOST} 'sudo nano $APP_DIR/.env'"
echo ""
echo "   2. Restart services after editing .env:"
echo "      ssh ${VPS_USER}@${VPS_HOST} 'sudo systemctl restart claudio-server claudio-telegram-bot'"
echo ""
echo "📊 Monitor logs:"
echo "   Claudio Server: ssh ${VPS_USER}@${VPS_HOST} 'journalctl -u claudio-server -f'"
echo "   Telegram Bot:   ssh ${VPS_USER}@${VPS_HOST} 'journalctl -u claudio-telegram-bot -f'"
echo ""
echo "🔧 Service management:"
echo "   ssh ${VPS_USER}@${VPS_HOST} 'sudo systemctl {start|stop|restart|status} claudio-server'"
echo "   ssh ${VPS_USER}@${VPS_HOST} 'sudo systemctl {start|stop|restart|status} claudio-telegram-bot'"
