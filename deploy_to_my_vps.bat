@echo off
REM ============================================
REM Claudio Bot - Deploy to Your VPS
REM ============================================
REM VPS Configuration - UPDATE THESE WITH YOUR DATA
REM ============================================

SET VPS_HOST=51.222.207.250
SET VPS_USER=root
SET PROJECT_DIR=/opt/claudio-bot

echo =======================================================================
echo   Claudio Bot - Deploy to Your VPS
echo =======================================================================
echo.
echo VPS: %VPS_HOST%
echo User: %VPS_USER%
echo Directory: %PROJECT_DIR%
echo.
echo.
echo =======================================================================
echo   STEP 1/5: Pulling latest changes from GitHub
echo =======================================================================
echo.

cd /d %~dp0
git pull origin master

if errorlevel 1 (
    echo [ERROR] Git pull failed. Make sure you're in a git repository.
    pause
    exit /b 1
)

echo.
echo =======================================================================
echo   STEP 2/5: Stopping current services on VPS
echo =======================================================================
echo.

echo Stopping Claudio services...
ssh %VPS_USER%@%VPS_HOST% "systemctl stop claudio-server claudio-telegram-bot 2>NUL || echo Services not running or already stopped"

echo.
echo =======================================================================
echo   STEP 3/5: Copying files to VPS
echo =======================================================================
echo.

echo Copying Python files...
scp claudio_complete.py %VPS_USER%@%VPS_HOST%:/tmp/
if errorlevel 1 (
    echo [ERROR] Failed to copy claudio_complete.py
    pause
    exit /b 1
)

scp bot_v2.py %VPS_USER%@%VPS_HOST%:/tmp/
scp n8n_database.py %VPS_USER%@%VPS_HOST%:/tmp/
scp n8n_mcp_tools.py %VPS_USER%@%VPS_HOST%:/tmp/
scp requirements.txt %VPS_USER%@%VPS_HOST%:/tmp/

echo Copying skills directory...
scp -r skills %VPS_USER%@%VPS_HOST%:/tmp/

echo Copying configuration...
scp .env.example %VPS_USER%@%VPS_HOST%:/tmp/

echo.
echo =======================================================================
echo   STEP 4/5: Installing on VPS
echo =======================================================================
echo.

echo Connecting to VPS and installing...
ssh %VPS_USER%@%VPS_HOST% bash -c "'"
echo =======================================================================
echo   Installing Claudio Bot on VPS
echo =======================================================================

echo ''
echo '[1/6] Creating user and directory...'
useradd -m -s /bin/bash claudio 2^>^/dev/null ^|^^ true
mkdir -p %PROJECT_DIR%
chown -R claudio:claudio %PROJECT_DIR%

echo ''
echo '[2/6] Copying files...'
mv /tmp/*.py %PROJECT_DIR%/
mv /tmp/skills %PROJECT_DIR%/
mv /tmp/requirements.txt %PROJECT_DIR%/
mv /tmp/.env.example %PROJECT_DIR%/

echo ''
echo '[3/6] Setting up Python environment...'
cd %PROJECT_DIR%
sudo -u claudio python3 -m venv venv 2^>^/dev/null ^|^^ echo venv already exists
sudo -u claudio venv/bin/pip install -q -r requirements.txt

echo ''
echo '[4/6] Creating or updating .env file...'
if [ ! -f .env ]; then
    cp .env.example .env
    echo .env file created. Please edit it with your credentials.
    echo Run: nano %PROJECT_DIR%/.env
else
    echo .env file already exists, backing up...
    cp .env .env.backup
fi

echo ''
echo '[5/6] Creating systemd services...'
tee /etc/systemd/system/claudio-server.service ^> /dev/null '<<'SVCEOF'
[Unit]
Description=Claudio Server
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory=%PROJECT_DIR%
EnvironmentFile=%PROJECT_DIR%/.env
ExecStart=%PROJECT_DIR%/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

tee /etc/systemd/system/claudio-telegram-bot.service ^> /dev/null '<<'SVCEOF'
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory=%PROJECT_DIR%
EnvironmentFile=%PROJECT_DIR%/.env
ExecStart=%PROJECT_DIR%/venv/bin/python bot_v2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SVCEOF

echo ''
echo '[6/6] Reloading and enabling services...'
systemctl daemon-reload
systemctl enable claudio-server.service claudio-telegram-bot.service

echo ''
echo =======================================================================
echo   Installation Complete!
echo =======================================================================

echo ''
echo To start services manually:
echo   sudo systemctl start claudio-server claudio-telegram-bot
echo ''
echo To check status:
echo   sudo systemctl status claudio-server claudio-telegram-bot
echo ''

"'"

echo.
echo =======================================================================
echo   STEP 5/5: Starting services
echo =======================================================================
echo.

echo Starting Claudio services...
ssh %VPS_USER%@%VPS_HOST% "systemctl start claudio-server claudio-telegram-bot"

echo.
echo =======================================================================
echo   DEPLOYMENT COMPLETE!
echo =======================================================================
echo.
echo Your VPS: %VPS_HOST%
echo.
echo Next steps:
echo   1. Configure your .env file:
echo      ssh %VPS_USER%@%VPS_HOST% "nano %PROJECT_DIR%/.env"
echo.
echo   2. Check service status:
echo      ssh %VPS_USER%@%VPS_HOST% "sudo systemctl status claudio-telegram-bot"
echo.
echo   3. View logs:
echo      ssh %VPS_USER%@%VPS_HOST% "sudo journalctl -u claudio-telegram-bot -f"
echo.
echo   4. Admin commands in Telegram:
echo      /status - Check current model
echo      /models - List available models
echo      /switch anthropic - Switch provider
echo      /addmodel - Add custom model
echo      /admin - Show admin help
echo.

pause
