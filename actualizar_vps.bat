@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo   Actualizar Claudio Bot en VPS
echo ==========================================
echo.
echo Este script conectara al VPS y actualizara
echo el codigo con los ultimos cambios del repositorio.
echo.

set VPS_HOST=51.222.207.250
set VPS_USER=ubuntu
set VPS_PATH=/opt/claudio-bot
set REPO=https://github.com/LeonardoPS1/bot_n8n.git

echo 1. Creando script de actualizacion...
(
echo #!/bin/bash
echo set -e
echo.
echo echo "=== Actualizando Claudio Bot ==="
echo echo.
echo.
echo # Cambiar al directorio del proyecto
echo cd %VPS_PATH%
echo.
echo # Guardar cambios locales si hay
echo git stash 2^>/dev/null ^|^| true
echo.
echo # Obtener ultimos cambios
echo git fetch origin master
echo git reset --hard origin/master
echo git pull origin master
echo.
echo # Instalar dependencias nuevas si las hay
echo source venv/bin/activate
echo pip install -q -r requirements.txt 2^>/dev/null ^|^| true
echo.
echo # Reiniciar servicios
echo echo "Reiniciando servicios..."
echo sudo systemctl restart claudio-server
echo sudo systemctl restart claudio-telegram-bot
echo.
echo # Esperar un momento
echo sleep 3
echo.
echo # Verificar estado
echo echo "=== Estado de los Servicios ==="
echo sudo systemctl status claudio-server --no-pager -l ^| head -10
echo sudo systemctl status claudio-telegram-bot --no-pager -l ^| head -10
echo.
echo echo "=== Actualizacion Completada ==="
) > update_script.sh

echo 2. Enviando script al VPS...
echo    Cuando se te pida contrasena, usa: Cool220479..@
echo.

scp -o StrictHostKeyChecking=no update_script.sh %VPS_USER%@%VPS_HOST:/tmp/

echo.
echo 3. Ejecutando actualizacion en el VPS...
echo.

ssh -o StrictHostKeyChecking=no %VPS_USER%@%VPS_HOST "bash /tmp/update_script.sh"

echo.
del update_script.sh
echo ==========================================
echo   Actualizacion Completada
echo ==========================================
echo.
echo Bot debe estar funcionando ahora con los cambios.
echo Prueba enviarle un mensaje en Telegram.
echo.
pause
