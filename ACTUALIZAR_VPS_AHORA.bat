@echo off
REM ============================================================
REM  ACTUALIZAR CLAUDIO BOT EN VPS - EJECUTAR AHORA
REM ============================================================
REM
REM Este script actualizara el VPS con los ultimos cambios
REM que arreglan el problema de timeout y agregan
REM la funcion de eliminar workflows.
REM
REM Contraseña del VPS: Cool220479..@
REM
REM ============================================================

setlocal enabledelayedexpansion

echo.
echo ==========================================
echo   ACTUALIZAR CLAUDIO BOT EN VPS
echo ==========================================
echo.
echo Este script hara lo siguiente:
echo   1. Conectarse al VPS (51.222.207.250)
echo   2. Actualizar el codigo desde GitHub
echo   3. Reiniciar los servicios
echo   4. Verificar que todo funcione
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo Creando script de actualizacion...
echo.

REM Crear script temporal de actualización
(
echo #!/bin/bash
echo set -e
echo echo "=== Iniciando actualizacion ==="
echo echo "Fecha: $(date)"
echo echo.
echo.
echo # Ir al directorio del proyecto
echo cd /opt/claudio-bot ^|^| exit 1
echo.
echo # Hacer backup de .env
echo cp .env .env.backup.$$ 2^>/dev/null ^|^| true
echo.
echo # Obtener ultimos cambios
echo echo "Obteniendo cambios del repositorio..."
echo git fetch origin master
echo git reset --hard origin/master
echo git pull origin master
echo.
echo # Restaurar .env
echo mv .env.backup.$$ .env 2^>/dev/null ^|^| true
echo.
echo # Instalar dependencias nuevas
echo echo "Instalando dependencias..."
echo source venv/bin/activate ^|^| true
echo pip install -q -r requirements.txt 2^>/dev/null ^|^| true
echo.
echo # Reiniciar servicios
echo echo "Reiniciando servicios..."
echo sudo systemctl restart claudio-server
echo sudo systemctl restart claudio-telegram-bot
echo.
echo # Esperar que inicien
echo sleep 5
echo.
echo # Verificar estado
echo echo "=== Estado de claudio-server ==="
echo sudo systemctl status claudio-server --no-pager ^| head -15
echo echo.
echo echo "=== Estado de claudio-telegram-bot ==="
echo sudo systemctl status claudio-telegram-bot --no-pager ^| head -15
echo echo.
echo echo "=== Logs recientes del servidor ==="
echo sudo journalctl -u claudio-server -n 15 --no-pager
echo echo.
echo echo "=== Actualizacion completada ==="
echo echo "Bot debe estar funcionando ahora."
echo rm -f /tmp/update_claudio.sh
) > update_claudio.sh

echo.
echo ==========================================
echo   CONECTANDO AL VPS
echo ==========================================
echo.
echo Cuando se pida contrasena, usa: Cool220479..@
echo.

REM Crear comando SSH
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@51.222.207.250 "bash -s" < update_claudio.sh

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo   ACTUALIZACION EXITOSA
    echo ==========================================
    echo.
    echo Los cambios se han aplicado correctamente.
    echo.
    echo Ahora prueba el bot en Telegram:
    echo   1. Enviar: HOLA
    echo   2. Enviar: /status
    echo   3. Enviar: LISTA LOS WORKFLOWS
    echo.
) else (
    echo.
    echo ==========================================
    echo   ERROR EN LA ACTUALIZACION
    echo ==========================================
    echo.
    echo Si SSH no esta disponible, intenta:
    echo   1. Instalar PuTTY: https://www.putty.org/
    echo   2. Conectar manualmente:
    echo      ssh ubuntu@51.222.207.250
    echo   3. Ejecutar: cd /opt/claudio-bot ^&^& git pull ^&^& sudo systemctl restart claudio-*
    echo.
)

del update_claudio.sh 2>nul
pause
