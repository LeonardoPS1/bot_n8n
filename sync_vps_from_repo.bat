@echo off
REM Script to sync VPS with GitHub repository (Windows)
REM Execute: sync_vps_from_repo.bat

setlocal enabledelayedexpansion

set VPS_HOST=51.222.207.250
set VPS_USER=ubuntu
set VPS_PATH=/opt/claudio-bot
set REPO_URL=https://github.com/LeonardoPS1/bot_n8n.git

echo ==========================================
echo   Syncing VPS with GitHub Repository
echo ==========================================
echo.

REM Check for plink (PuTTY SSH)
where plink >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set SSH_CMD=plink -ssh -batch
    goto :run_ssh
)

REM Check for ssh (Git Bash / OpenSSH)
where ssh >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set SSH_CMD=ssh -o StrictHostKeyChecking=no
    goto :run_ssh
)

echo ERROR: SSH client not found!
echo Please install PuTTY (with plink) or Git Bash (with ssh)
echo.
pause
exit /b 1

:run_ssh
echo Connecting to VPS: %VPS_USER%@%VPS_HOST%
echo.

REM Create commands to execute on VPS
(
echo cd %VPS_PATH% ^|^| ^^( echo 'Path not found, cloning...' ^&^& mkdir -p %VPS_PATH% ^&^& cd /opt ^&^& rm -rf claudio-bot ^&^& git clone %REPO_URL% claudio-bot ^&^& cd claudio-bot^^^)
echo git fetch origin master
echo git reset --hard origin/master
echo git pull origin master
echo '=========================================='
echo 'Repository synced successfully'
echo '=========================================='
echo ''
echo 'Current files:'
ls -la *.md *.py 2^>/dev/null ^| head -20
echo ''
echo 'Restarting services...'
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot
echo ''
echo 'Services status:'
sudo systemctl status claudio-server --no-pager -l ^| head -5
sudo systemctl status claudio-telegram-bot --no-pager -l ^| head -5
) > temp_commands.sh

%SSH_CMD% %VPS_USER%@%VPS_HOST% < temp_commands.sh
del temp_commands.sh

echo.
echo ==========================================
echo   Sync Complete - Check for errors above
echo ==========================================
echo.
pause
