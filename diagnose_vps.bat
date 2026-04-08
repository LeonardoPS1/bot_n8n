@echo off
setlocal enabledelayedexpansion

set VPS_HOST=51.222.207.250
set VPS_USER=ubuntu

echo ==========================================
echo   Claudio Bot - VPS Diagnostics
echo ==========================================
echo.

echo Checking services status...
echo.

(
echo sudo systemctl status claudio-server --no-pager -l
echo echo "---"
echo sudo systemctl status claudio-telegram-bot --no-pager -l
echo echo "---"
echo echo "Server logs:"
echo sudo journalctl -u claudio-server -n 30 --no-pager
echo echo "---"
echo echo "Bot logs:"
echo sudo journalctl -u claudio-telegram-bot -n 30 --no-pager
echo echo "---"
echo echo "Restarting services..."
echo sudo systemctl restart claudio-server
echo sudo systemctl restart claudio-telegram-bot
echo echo "---"
echo echo "New status:"
echo sudo systemctl status claudio-server --no-pager -l | head -10
echo sudo systemctl status claudio-telegram-bot --no-pager -l | head -10
) > commands.sh

ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_HOST% < commands.sh
del commands.sh

echo.
echo ==========================================
echo   Diagnostics Complete
echo ==========================================
pause
