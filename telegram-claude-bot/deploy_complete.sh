#!/bin/bash
# Deploy Claudio COMPLETE to VPS

set -e

VPS_USER="ubuntu"
VPS_HOST="51.222.207.250"
VPS_PASSWORD="Cool220479..@"
APP_DIR="/opt/claudio-bot"

echo "[=== Deploying Claudio COMPLETE ===]"

# Create SSH connection helper
ssh_exec() {
    sshpass -p "$VPS_PASSWORD" ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "$1"
}

# Stop services
echo "[1] Stopping services..."
ssh_exec "sudo systemctl stop claudio-server claudio-telegram-bot"

# Create directory structure
echo "[2] Creating directory structure..."
ssh_exec "sudo mkdir -p $APP_DIR/skills"

# Copy files using scp
echo "[3] Copying files..."
sshpass -p "$VPS_PASSWORD" scp -o StrictHostKeyChecking=no \
    claudio_complete.py \
    n8n_database.py \
    "$VPS_USER@$VPS_HOST:$APP_DIR/"

# Create skills files remotely
echo "[4] Creating skills modules..."
ssh_exec "cat > $APP_DIR/skills/__init__.py" < 'ENDOFFILE'
#!/usr/bin/env python3
"""Claudio Skills Package"""
from . import n8n_expression_syntax
from . import n8n_other_skills
SKILLS = {
    'expression_syntax': n8n_expression_syntax,
    'other': n8n_other_skills
}
ENDOFFILE"

# Update systemd
echo "[5] Updating systemd service..."
ssh_exec "sudo bash -c \"cat > /etc/systemd/system/claudio-server.service << 'SVCEOF'
[Unit]
Description=Claudio COMPLETE
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF
\""

ssh_exec "sudo systemctl daemon-reload"

# Start services
echo "[6] Starting services..."
ssh_exec "sudo systemctl start claudio-server"
sleep 3
ssh_exec "sudo systemctl start claudio-telegram-bot"

# Test
echo "[7] Testing..."
ssh_exec "curl -s http://localhost:8000/health | head -20"

echo ""
echo "[+] Deploy COMPLETE!"
