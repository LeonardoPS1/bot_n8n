# ==========================================
# ACTUALIZAR CLAUDIO BOT EN VPS - PowerShell
# ==========================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ACTUALIZAR CLAUDIO BOT EN VPS" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$VPS_HOST = "51.222.207.250"
$VPS_USER = "ubuntu"
$VPS_PASSWORD = "Cool220479..@"
$VPS_PATH = "/opt/claudio-bot"

Write-Host "Conectando al VPS: $VPS_HOST..." -ForegroundColor Yellow
Write-Host ""

# Crear el script remoto
$remoteScript = @"
cd $VPS_PATH || exit 1
echo "=== Actualizando desde repositorio ==="
git fetch origin master
git reset --hard origin/master
git pull origin master

echo ""
echo "=== Reiniciando servicios ==="
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot

sleep 3

echo ""
echo "=== Estado de claudio-server ==="
sudo systemctl status claudio-server --no-pager | head -15

echo ""
echo "=== Estado de claudio-telegram-bot ==="
sudo systemctl status claudio-telegram-bot --no-pager | head -15

echo ""
echo "=== Actualizacion completada ==="
"@

# Guardar script temporal
$remoteScript | Out-File -Encoding UTF8 "$env:TEMP\update_claudio.sh"

# Usar plink si está disponible, si no intentar ssh
$plinkPath = "C:\Program Files\PuTTY\plink.exe"
if (Test-Path $plinkPath) {
    Write-Host "Usando plink (PuTTY)..." -ForegroundColor Green
    & $plinkPath -ssh -batch -pw $VPS_PASSWORD "$VPS_USER@$VPS_HOST" -m "$env:TEMP\update_claudio.sh"
} else {
    Write-Host "Usando ssh (requiere que ingreses contraseña)..." -ForegroundColor Yellow
    Write-Host "Contraseña: $VPS_PASSWORD" -ForegroundColor Cyan
    Write-Host ""
    ssh -o StrictHostKeyChecking=no "$VPS_USER@$VPS_HOST" "bash -s" < "$env:TEMP\update_claudio.sh"
}

# Limpiar
Remove-Item "$env:TEMP\update_claudio.sh" -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  ACTUALIZACION COMPLETADA" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Prueba el bot en Telegram ahora:" -ForegroundColor White
Write-Host "  - HOLA" -ForegroundColor Gray
Write-Host "  - /status" -ForegroundColor Gray
Write-Host "  - LISTA LOS WORKFLOWS" -ForegroundColor Gray
Write-Host ""
