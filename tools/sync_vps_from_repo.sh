#!/bin/bash
# Script to sync VPS with GitHub repository
# Execute: ./sync_vps_from_repo.sh

VPS_HOST="51.222.207.250"
VPS_USER="ubuntu"
VPS_PATH="/opt/claudio-bot"
REPO_URL="https://github.com/LeonardoPS1/bot_n8n.git"

echo "=========================================="
echo "  Syncing VPS with GitHub Repository"
echo "=========================================="
echo ""

# Ask for VPS password
echo "Enter VPS password for user $VPS_USER:"
read -s VPS_PASS

# Commands to execute on VPS
SSH_COMMANDS="
cd $VPS_PATH || { echo 'Path not found, cloning...' && mkdir -p $VPS_PATH && cd /opt && rm -rf claudio-bot && git clone $REPO_URL claudio-bot && cd claudio-bot; }
git fetch origin master
git reset --hard origin/master
git pull origin master
echo '=========================================='
echo 'Repository synced successfully'
echo '=========================================='
echo ''
echo 'Current files:'
ls -la *.md *.py 2>/dev/null | head -20
echo ''
echo 'Restarting services...'
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot
echo ''
echo 'Services status:'
sudo systemctl status claudio-server --no-pager -l | head -5
sudo systemctl status claudio-telegram-bot --no-pager -l | head -5
"

# Execute commands via SSH
echo "$SSH_COMMANDS" | ssh -o StrictHostKeyChecking=no $VPS_USER@$VPS_HOST "bash -s"

echo ""
echo "✓ VPS synced with repository"
