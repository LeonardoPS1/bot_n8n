@echo off
REM ============================================
REM Claudio Bot - Deploy to Your VPS
REM ============================================
REM VPS Configuration
REM ============================================

SET VPS_HOST=51.222.207.250
SET VPS_USER=ubuntu
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

REM Check for plink (PuTTY)
where plink >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] plink.exe not found!
    echo.
    echo Please install PuTTY (includes plink):
    echo Download from: https://www.putty.org/
    echo.
    echo Or use this command: winget install PuTTY.PuTTY
    echo.
    pause
    exit /b 1
)

echo =======================================================================
echo   Authentication
echo =======================================================================
echo.
echo Choose authentication method:
echo.
echo [1] Password authentication
echo [2] SSH Key authentication
echo.
set /p AUTH_CHOICE="Select option (1 or 2): "

if "%AUTH_CHOICE%"=="1" (
    echo.
    set /p VPS_PASS="Enter VPS password: "
    echo.
) else (
    echo.
    echo Using SSH key authentication...
    echo Make sure your key is loaded in Pageant or specified.
    echo.
    set VPS_PASS=
)

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
if defined VPS_PASS (
    plink -ssh -pw %VPS_PASS% %VPS_USER%@%VPS_HOST% "sudo systemctl stop claudio-server claudio-telegram-bot 2>/dev/null || echo Services not running or already stopped"
) else (
    plink -ssh %VPS_USER%@%VPS_HOST% "sudo systemctl stop claudio-server claudio-telegram-bot 2>/dev/null || echo Services not running or already stopped"
)

if errorlevel 1 (
    echo [WARNING] Could not stop services (may not be installed yet)
)

echo.
echo =======================================================================
echo   STEP 3/5: Copying files to VPS
echo =======================================================================
echo.

echo Copying Python files...
if defined VPS_PASS (
    pscp -pw %VPS_PASS% claudio_complete.py %VPS_USER%@%VPS_HOST%:/tmp/
    if errorlevel 1 (
        echo [ERROR] Failed to copy claudio_complete.py
        pause
        exit /b 1
    )
    pscp -pw %VPS_PASS% bot_v2.py %VPS_USER%@%VPS_HOST%:/tmp/
    pscp -pw %VPS_PASS% n8n_database.py %VPS_USER%@%VPS_HOST%:/tmp/
    pscp -pw %VPS_PASS% n8n_mcp_tools.py %VPS_USER%@%VPS_HOST%:/tmp/
    pscp -pw %VPS_PASS% requirements.txt %VPS_USER%@%VPS_HOST%:/tmp/
    pscp -r -pw %VPS_PASS% skills %VPS_USER%@%VPS_HOST%:/tmp/
    pscp -pw %VPS_PASS% .env.example %VPS_USER%@%VPS_HOST%:/tmp/
) else (
    pscp claudio_complete.py %VPS_USER%@%VPS_HOST%:/tmp/
    if errorlevel 1 (
        echo [ERROR] Failed to copy claudio_complete.py
        pause
        exit /b 1
    )
    pscp bot_v2.py %VPS_USER%@%VPS_HOST%:/tmp/
    pscp n8n_database.py %VPS_USER%@%VPS_HOST%:/tmp/
    pscp n8n_mcp_tools.py %VPS_USER%@%VPS_HOST%:/tmp/
    pscp requirements.txt %VPS_USER%@%VPS_HOST%:/tmp/
    pscp -r skills %VPS_USER%@%VPS_HOST%:/tmp/
    pscp .env.example %VPS_USER%@%VPS_HOST%:/tmp/
)

echo Copying configuration...
echo.
echo =======================================================================
echo   STEP 4/5: Installing on VPS
echo =======================================================================
echo.

echo Connecting to VPS and installing...
if defined VPS_PASS (
    plink -ssh -pw %VPS_PASS% %VPS_USER%@%VPS_HOST% bash -c 'sudo bash -s' <<'ENDSSH'
) else (
    plink -ssh %VPS_USER%@%VPS_HOST% bash -c 'sudo bash -s' <<'ENDSSH'
)
echo "======================================================================="
echo "  Installing Claudio Bot on VPS"
echo "======================================================================="

echo ""
echo "[1/6] Creating user and directory..."
sudo useradd -m -s /bin/bash claudio 2>/dev/null || echo "User claudio already exists"
sudo mkdir -p %PROJECT_DIR%
sudo chown -R claudio:claudio %PROJECT_DIR%

echo ""
echo "[2/6] Copying files..."
sudo mv /tmp/*.py %PROJECT_DIR%/
sudo mv /tmp/skills %PROJECT_DIR%/
sudo mv /tmp/requirements.txt %PROJECT_DIR%/
sudo mv /tmp/.env.example %PROJECT_DIR%/

echo ""
echo "[3/6] Setting up Python environment..."
cd %PROJECT_DIR%
sudo -u claudio python3 -m venv venv 2>/dev/null || echo "venv already exists"
sudo -u claudio venv/bin/pip install -q -r requirements.txt

echo ""
echo "[4/6] Creating or updating .env file..."
if [ ! -f %PROJECT_DIR%/.env ]; then
    sudo cp %PROJECT_DIR%/.env.example %PROJECT_DIR%/.env
    echo ".env file created. Please edit it with your credentials."
    echo "Run: sudo nano %PROJECT_DIR%/.env"
else
    echo ".env file already exists, backing up..."
    sudo cp %PROJECT_DIR%/.env %PROJECT_DIR%/.env.backup
fi

echo ""
echo "[5/6] Creating systemd services..."
sudo tee /etc/systemd/system/claudio-server.service > /dev/null <<'SVCEOF'
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

sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null <<'SVCEOF'
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

echo ""
echo "[6/6] Reloading and enabling services..."
sudo systemctl daemon-reload
sudo systemctl enable claudio-server.service claudio-telegram-bot.service

echo ""
echo "======================================================================="
echo "  Installation Complete!"
echo "======================================================================="

echo ""
echo "To start services manually:"
echo "  sudo systemctl start claudio-server claudio-telegram-bot"
echo ""
echo "To check status:"
echo "  sudo systemctl status claudio-server claudio-telegram-bot"
echo ""
ENDSSH

if errorlevel 1 (
    echo [WARNING] Some installation steps may have failed. Check above.
)

echo.
echo =======================================================================
echo   STEP 5/5: Starting services
echo =======================================================================
echo.

echo Starting Claudio services...
if defined VPS_PASS (
    plink -ssh -pw %VPS_PASS% %VPS_USER%@%VPS_HOST% "sudo systemctl start claudio-server claudio-telegram-bot"
) else (
    plink -ssh %VPS_USER%@%VPS_HOST% "sudo systemctl start claudio-server claudio-telegram-bot"
)

echo.
echo =======================================================================
echo   DEPLOYMENT COMPLETE!
echo =======================================================================
echo.
echo Your VPS: %VPS_HOST%
echo User: %VPS_USER%
echo.
echo Next steps:
echo   1. Configure your .env file:
if defined VPS_PASS (
    echo      plink -ssh -pw %VPS_PASS% %VPS_USER%@%VPS_HOST% "sudo nano %PROJECT_DIR%/.env"
) else (
    echo      plink -ssh %VPS_USER%@%VPS_HOST% "sudo nano %PROJECT_DIR%/.env"
)
echo.
echo   2. Check service status:
if defined VPS_PASS (
    echo      plink -ssh -pw %VPS_PASS% %VPS_USER%@%VPS_HOST% "sudo systemctl status claudio-telegram-bot"
) else (
    echo      plink -ssh %VPS_USER%@%VPS_HOST% "sudo systemctl status claudio-telegram-bot"
)
echo.
echo   3. View logs:
if defined VPS_PASS (
    echo      plink -ssh -pw %VPS_PASS% %VPS_USER%@%VPS_HOST% "sudo journalctl -u claudio-telegram-bot -f"
) else (
    echo      plink -ssh %VPS_USER%@%VPS_HOST% "sudo journalctl -u claudio-telegram-bot -f"
)
echo.
echo   4. Admin commands in Telegram:
echo      /status - Check current model
echo      /models - List available models
echo      /switch anthropic - Switch provider
echo      /addkey - Add API key securely
echo      /admin - Show admin help
echo.

pause
