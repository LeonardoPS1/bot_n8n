#!/bin/bash
# ============================================
# Claudio Bot - Deployment Script for VPS
# ============================================
# Este script instala y configura Claudio Bot en una VPS Ubuntu/Debian
# Uso: bash deploy_vps_complete.sh
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuración
VPS_INSTALL_DIR="/opt/claudio-bot"
VPS_SERVICE_USER="claudio"
REPO_URL="https://github.com/LeonardoPS1/bot_n8n.git"

# Funciones de utilidad
print_header() {
    echo -e "\n${CYAN}${BOLD}======================================================================${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
    echo -e "${CYAN}${BOLD}======================================================================${NC}\n"
}

print_step() {
    echo -e "\n${YELLOW}${BOLD}>>> $1${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================
# INICIO DEL SCRIPT
# ============================================
print_header "CLAUDIO BOT - VPS DEPLOYMENT SCRIPT"

echo -e "${BOLD}Este script realizará lo siguiente:${NC}"
echo "  1. Actualizar el sistema e instalar dependencias"
echo "  2. Crear usuario y directorios para Claudio"
echo "  3. Clonar el repositorio desde GitHub"
echo "  4. Ejecutar el instalador interactivo"
echo "  5. Configurar servicios systemd"
echo "  6. Iniciar los servicios"

echo ""
read -p "$(echo -e ${YELLOW}"¿Continuar? (y/N): "${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Instalación cancelada"
    exit 0
fi

# ============================================
# PASO 1: Actualizar sistema e instalar dependencias
# ============================================
print_step "PASO 1/6: Actualizando sistema e instalando dependencias"

print_info "Actualizando paquetes..."
sudo apt-get update -qq

print_info "Instalando dependencias..."
sudo apt-get install -y python3 python3-pip python3-venv git curl > /dev/null 2>&1

print_success "Dependencias instaladas"

# ============================================
# PASO 2: Crear usuario y directorios
# ============================================
print_step "PASO 2/6: Creando usuario y directorios"

# Crear usuario si no existe
if id "$VPS_SERVICE_USER" &>/dev/null; then
    print_info "Usuario '$VPS_SERVICE_USER' ya existe"
else
    print_info "Creando usuario '$VPS_SERVICE_USER'..."
    sudo useradd -m -s /bin/bash $VPS_SERVICE_USER
    print_success "Usuario creado"
fi

# Crear directorio de instalación
print_info "Creando directorio de instalación..."
sudo mkdir -p $VPS_INSTALL_DIR
sudo chown -R $VPS_SERVICE_USER:$VPS_SERVICE_USER $VPS_INSTALL_DIR
print_success "Directorio creado: $VPS_INSTALL_DIR"

# ============================================
# PASO 3: Clonar repositorio
# ============================================
print_step "PASO 3/6: Clonando repositorio desde GitHub"

if [ -d "$VPS_INSTALL_DIR/.git" ]; then
    print_info "El repositorio ya existe, actualizando..."
    sudo -u $VPS_SERVICE_USER git -C $VPS_INSTALL_DIR pull
else
    print_info "Clonando repositorio..."
    sudo -u $VPS_SERVICE_USER git clone $REPO_URL $VPS_INSTALL_DIR
fi
print_success "Repositorio clonado/actualizado"

# ============================================
# PASO 4: Ejecutar instalador interactivo
# ============================================
print_step "PASO 4/6: Ejecutando instalador interactivo"

print_info "Cambiando al directorio de instalación..."
cd $VPS_INSTALL_DIR

print_info "Instalando dependencias Python básicas..."
sudo -u $VPS_SERVICE_USER python3 -m venv venv
sudo -u $VPS_SERVICE_USER venv/bin/pip install -q -r requirements.txt

print_header "INSTALLER WIZARD"
print_info "A continuación responderás algunas preguntas para configurar Claudio"

echo ""
# Ejecutar instalador como usuario claudio
sudo -u $VPS_SERVICE_USER bash -c "
source venv/bin/activate
python3 install.py
"

# Verificar que se creó .env
if [ ! -f "$VPS_INSTALL_DIR/.env" ]; then
    print_error "No se creó el archivo .env. El instalador falló o fue cancelado."
    exit 1
fi

print_success "Configuración completada"

# ============================================
# PASO 5: Configurar servicios systemd
# ============================================
print_step "PASO 5/6: Configurando servicios systemd"

# Servicio del Servidor Claudio
print_info "Creando servicio claudio-server..."
sudo tee /etc/systemd/system/claudio-server.service > /dev/null <<EOF
[Unit]
Description=Claudio Server
After=network.target

[Service]
Type=simple
User=$VPS_SERVICE_USER
WorkingDirectory=$VPS_INSTALL_DIR
EnvironmentFile=$VPS_INSTALL_DIR/.env
ExecStart=$VPS_INSTALL_DIR/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Servicio del Bot de Telegram
print_info "Creando servicio claudio-telegram-bot..."
sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=$VPS_SERVICE_USER
WorkingDirectory=$VPS_INSTALL_DIR
EnvironmentFile=$VPS_INSTALL_DIR/.env
ExecStart=$VPS_INSTALL_DIR/venv/bin/python bot_v2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Recargar systemd
print_info "Recargando systemd..."
sudo systemctl daemon-reload

print_success "Servicios configurados"

# ============================================
# PASO 6: Iniciar servicios
# ============================================
print_step "PASO 6/6: Iniciando servicios"

print_info "Habilitando servicios..."
sudo systemctl enable claudio-server.service claudio-telegram-bot.service

print_info "Iniciando servicios..."
sudo systemctl start claudio-server.service

# Esperar un momento antes de iniciar el bot
sleep 3

sudo systemctl start claudio-telegram-bot.service

print_success "Servicios iniciados"

# ============================================
# VERIFICACIÓN
# ============================================
print_step "VERIFICACIÓN"

sleep 2

echo ""
echo "Estado del Servidor Claudio:"
sudo systemctl status claudio-server.service --no-pager -l || true

echo ""
echo "Estado del Bot de Telegram:"
sudo systemctl status claudio-telegram-bot.service --no-pager -l || true

# ============================================
# INSTRUCCIONES FINALES
# ============================================
print_header "INSTALACIÓN COMPLETADA"

echo ""
echo -e "${GREEN}${BOLD}¡Claudio Bot ha sido instalado exitosamente!${NC}\n"

echo -e "${YELLOW}Comandos útiles:${NC}"
echo "  Ver logs del servidor:"
echo "    ${CYAN}sudo journalctl -u claudio-server -f${NC}"
echo ""
echo "  Ver logs del bot:"
echo "    ${CYAN}sudo journalctl -u claudio-telegram-bot -f${NC}"
echo ""
echo "  Reiniciar servicios:"
echo "    ${CYAN}sudo systemctl restart claudio-server claudio-telegram-bot${NC}"
echo ""
echo "  Detener servicios:"
echo "    ${CYAN}sudo systemctl stop claudio-server claudio-telegram-bot${NC}"
echo ""
echo -e "${YELLOW}Para verificar health check:${NC}"
echo "    ${CYAN}curl http://localhost:8000/health${NC}"
echo ""

# Verificar si hay errores
if sudo systemctl is-failed claudio-server.service || sudo systemctl is-failed claudio-telegram-bot.service; then
    echo -e "${RED}${BOLD}⚠ ADVERTENCIA: Uno o más servicios fallaron al iniciar${NC}"
    echo ""
    echo "Revisa los logs para identificar el problema:"
    echo "  ${CYAN}sudo journalctl -u claudio-server -n 50${NC}"
    echo "  ${CYAN}sudo journalctl -u claudio-telegram-bot -n 50${NC}"
else
    echo -e "${GREEN}${BOLD}✓ Todos los servicios están funcionando correctamente${NC}"
    echo ""
    echo -e "${YELLOW}Ahora puedes:${NC}"
    echo "  1. Abre Telegram y busca tu bot"
    echo "  2. Inicia una conversación con /start"
    echo "  3. ¡Comienza a crear workflows de n8n!"
fi

echo ""
