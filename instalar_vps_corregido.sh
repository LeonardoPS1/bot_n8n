#!/bin/bash
# Script para corregir la instalación en VPS
# Ejecutar en el VPS: bash -c "$(curl -fsSL https://raw.githubusercontent.com/LeonardoPS1/bot_n8n/master/instalar_vps_corregido.sh)"

set -e

echo "========================================"
echo "  CORREGIR INSTALACION CLAUDIO BOT"
echo "========================================"
echo ""

# Backup del directorio actual si existe
if [ -d "/opt/claudio-bot" ]; then
    echo "Haciendo backup del directorio actual..."
    sudo mv /opt/claudio-bot /opt/claudio-bot.backup.$(date +%Y%m%d_%H%M%S)
fi

# Clonar repositorio
echo "Clonando repositorio desde GitHub..."
cd /opt
sudo rm -rf claudio-bot
sudo git clone https://github.com/LeonardoPS1/bot_n8n.git claudio-bot
cd claudio-bot

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -q -r requirements.txt

# Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Edita .env con tus credenciales:"
    echo "   nano /opt/claudio-bot/.env"
fi

# Crear servicios systemd
echo "Configurando servicios systemd..."

# Servicio claudio-server
sudo tee /etc/systemd/system/claudio-server.service > /dev/null <<EOF
[Unit]
Description=Claudio AI Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/claudio-bot
Environment="PATH=/opt/claudio-bot/venv/bin"
ExecStart=/opt/claudio-bot/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Servicio claudio-telegram-bot
sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/claudio-bot
Environment="PATH=/opt/claudio-bot/venv/bin"
ExecStart=/opt/claudio-bot/venv/bin/python bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicios
sudo systemctl enable claudio-server
sudo systemctl enable claudio-telegram-bot

# Iniciar servicios
echo "Iniciando servicios..."
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot

sleep 3

echo ""
echo "========================================"
echo "  INSTALACION COMPLETADA"
echo "========================================"
echo ""
echo "Servicios iniciados:"
sudo systemctl status claudio-server --no-pager | head -5
sudo systemctl status claudio-telegram-bot --no-pager | head -5
echo ""
echo "Para verificar logs:"
echo "  sudo journalctl -u claudio-server -f"
echo "  sudo journalctl -u claudio-telegram-bot -f"
echo ""
