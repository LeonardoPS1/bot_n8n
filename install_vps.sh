#!/bin/bash
#
# Claudio Bot - VPS Installer
# Instala Claudio Bot en un servidor VPS Ubuntu/Debian
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funciones
print_header() {
    echo -e "\n${CYAN}============================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================${NC}\n"
}

print_step() {
    echo -e "\n${CYAN}➜ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Verificar root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script debe ejecutarse como root (use sudo)"
   exit 1
fi

print_header "CLAUDIO BOT - INSTALADOR VPS"
echo "Este script instalará Claudio Bot en tu VPS"
echo "Distribución detectada: $(lsb_release -s -d)"
echo ""

# Actualizar sistema
print_step "Actualizando paquetes del sistema..."
apt-get update -qq
apt-get upgrade -y -qq
print_success "Sistema actualizado"

# Instalar dependencias
print_step "Instalando dependencias..."
apt-get install -y -qq python3 python3-pip python3-venv git curl > /dev/null 2>&1
print_success "Dependencias instaladas"

# Crear usuario
print_step "Configurando usuario..."
if ! id -u claudio > /dev/null 2>&1; then
    useradd -m -s /bin/bash claudio
    print_success "Usuario 'claudio' creado"
else
    print_success "Usuario 'claudio' ya existe"
fi

# Directorio de instalación
INSTALL_DIR="/opt/claudio-bot"
print_step "Creando directorio de instalación: $INSTALL_DIR"
mkdir -p $INSTALL_DIR
chown claudio:claudio $INSTALL_DIR

# Descargar código
print_step "Descargando código..."
if [ -d "$INSTALL_DIR/.git" ]; then
    cd $INSTALL_DIR
    sudo -u claudio git pull > /dev/null 2>&1
    print_success "Código actualizado"
else
    if [ -n "$1" ]; then
        # Clonar desde repositorio personalizado
        sudo -u claudio git clone "$1" $INSTALL_DIR
    else
        # Usar el directorio actual si estamos en un repo git
        if [ -d ".git" ]; then
            cp -r . $INSTALL_DIR/
            chown -R claudio:claudio $INSTALL_DIR
        else
            print_error "No se encontró repositorio git. Por favor, especifica una URL:"
            echo "  bash install_vps.sh https://github.com/usuario/repo.git"
            exit 1
        fi
    fi
    print_success "Código descargado"
fi

cd $INSTALL_DIR

# Crear entorno virtual
print_step "Creando entorno virtual Python..."
sudo -u claudio python3 -m venv venv
print_success "Entorno virtual creado"

# Instalar dependencias Python
print_step "Instalando dependencias Python..."
sudo -u claudio venv/bin/pip install --upgrade pip -q
sudo -u claudio venv/bin/pip install -r requirements.txt -q
print_success "Dependencias Python instaladas"

# Verificar archivo .env
print_step "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    print_error "Archivo .env no encontrado"
    echo ""
    echo "Por favor, crea el archivo .env con tu configuración:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "O ejecuta el instalador interactivo:"
    echo "  sudo -u claudio python install.py"
    exit 1
fi
print_success "Archivo .env encontrado"

# Crear servicios systemd
print_step "Creando servicios systemd..."

cat > /etc/systemd/system/claudio-server.service << 'EOF'
[Unit]
Description=Claudio AI Server
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
Environment="PATH=/opt/claudio-bot/venv/bin"
ExecStart=/opt/claudio-bot/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/claudio-telegram-bot.service << 'EOF'
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
Environment="PATH=/opt/claudio-bot/venv/bin"
ExecStart=/opt/claudio-bot/venv/bin/python bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload > /dev/null 2>&1
print_success "Servicios systemd creados"

# Configurar firewall (si ufw está activo)
if command -v ufw &> /dev/null; then
    print_step "Configurando firewall..."
    ufw allow 8001/tcp > /dev/null 2>&1
    print_success "Firewall configurado"
fi

# Iniciar servicios
print_step "Iniciando servicios..."
systemctl enable claudio-server claudio-telegram-bot > /dev/null 2>&1
systemctl start claudio-server claudio-telegram-bot
print_success "Servicios iniciados"

# Esperar y verificar estado
sleep 5

print_header "VERIFICACIÓN DE INSTALACIÓN"

# Verificar servidor
if systemctl is-active --quiet claudio-server; then
    print_success "Claudio Server: ACTIVO"
else
    print_error "Claudio Server: FALLÓ"
    journalctl -u claudio-server -n 10 --no-pager
fi

# Verificar bot
if systemctl is-active --quiet claudio-telegram-bot; then
    print_success "Claudio Telegram Bot: ACTIVO"
else
    print_error "Claudio Telegram Bot: FALLÓ"
    journalctl -u claudio-telegram-bot -n 10 --no-pager
fi

# Health check
print_step "Verificando health endpoint..."
if curl -s http://localhost:8001/health > /dev/null; then
    print_success "Servidor respondiendo correctamente"
else
    print_error "Servidor no responde"
fi

echo ""
print_header "INSTALACIÓN COMPLETADA"
echo ""
echo "Servicios instalados:"
echo "  • Claudio Server:  http://localhost:8001"
echo "  • Telegram Bot:    Ejecutándose"
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status claudio-server"
echo "  sudo systemctl status claudio-telegram-bot"
echo "  sudo systemctl restart claudio-server"
echo "  sudo systemctl restart claudio-telegram-bot"
echo "  sudo journalctl -u claudio-server -f"
echo "  sudo journalctl -u claudio-telegram-bot -f"
echo ""
echo "Logs:"
echo "  sudo journalctl -u claudio-server -n 50"
echo "  sudo journalctl -u claudio-telegram-bot -n 50"
echo ""
echo "${GREEN}¡Claudio Bot está listo para usar!${NC}"
echo ""
