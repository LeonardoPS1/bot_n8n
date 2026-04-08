#!/bin/bash
set -e

VPS_HOST="51.222.207.250"
VPS_USER="ubuntu"
VPS_PATH="/opt/claudio-bot"

echo "=== Actualizando Claudio Bot en VPS ==="
echo ""

# Crear script de actualización remoto
cat > /tmp/remote_update.sh << 'EOF'
#!/bin/bash
set -e
echo "=== Actualizando desde repositorio ==="
cd /opt/claudio-bot

# Backup de .env
cp .env .env.backup 2>/dev/null || true

# Actualizar código
git fetch origin master
git reset --hard origin/master
git pull origin master

# Restaurar .env
mv .env.backup .env 2>/dev/null || true

# Activar venv
source venv/bin/activate

# Instalar nuevas dependencias
pip install -q -r requirements.txt 2>/dev/null || true

echo "=== Reiniciando servicios ==="
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot

sleep 3

echo "=== Estado de servicios ==="
sudo systemctl status claudio-server --no-pager -l | head -15
echo "---"
sudo systemctl status claudio-telegram-bot --no-pager -l | head -15

echo ""
echo "=== Logs recientes ==="
sudo journalctl -u claudio-server -n 10 --no-pager
EOF

# Copiar script al VPS
scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=30 /tmp/remote_update.sh ${VPS_USER}@${VPS_HOST}:/tmp/update.sh 2>/dev/null || echo "SCP failed, trying direct SSH..."

# Ejecutar actualización
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=30 ${VPS_USER}@${VPS_HOST} "bash /tmp/update.sh" 2>&1 || echo "SSH connection failed"

echo ""
echo "=== Actualización completada ==="
rm -f /tmp/remote_update.sh
