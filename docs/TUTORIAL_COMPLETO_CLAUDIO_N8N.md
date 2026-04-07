# 🤖 Tutorial Completo: Bot de Telegram con n8n-MCP para VPS

**Autor:** Claudio (Claude Code con n8n-MCP)
**Fecha:** Abril 2026
**Versión:** 3.0 Completa

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Requisitos Previos](#requisitos-previos)
4. [Configuración de la VPS](#configuración-de-la-vps)
5. [Instalación de n8n con Docker](#instalación-de-n8n-con-docker)
6. [Claudio: El Asistente n8n con IA](#claudio-el-asistente-n8n-con-ia)
7. [Bot de Telegram](#bot-de-telegram)
8. [Skills y MCP de n8n](#skills-y-mcp-de-n8n)
9. [Despliegue Completo en VPS](#despliegue-completo-en-vps)
10. [Prompts Útiles para Claudio](#prompts-útiles-para-claudio)
11. [Troubleshooting](#troubleshooting)
12. [Referencias de API](#referencias-de-api)

---

## 🎯 Introducción

Este documento describe el proceso completo para crear un **bot de Telegram experto en n8n** que utiliza:

- **Claude API** (Anthropic) para procesamiento de lenguaje natural
- **n8n-MCP** (Model Context Protocol) para acceso a 1,396 nodos n8n
- **2,709+ plantillas de workflows** de n8n
- **7 skills especializadas** en n8n
- **API de n8n** para gestión de workflows real

### 🌟 Características Principales

- ✅ Asistente experto en n8n disponible 24/7 vía Telegram
- ✅ Acceso a base de datos de 1,396 nodos n8n
- ✅ Validación de workflows y expresiones
- ✅ Búsqueda de plantillas y ejemplos
- ✅ Creación y modificación de workflows directamente
- ✅ Historial de conversación por usuario
- ✅ Sistema de permisos de usuarios
- ✅ Monitoreo de salud del sistema
- ✅ Auto-reinicio con systemd

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│  Claudio Server  │────▶│  Claude API     │
│  (bot_v2.py)    │     │  (claudio_       │     │  (Anthropic)    │
│                 │     │   complete.py)   │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │   n8n-MCP        │
                        │   Tools          │
                        └──────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌──────────────┐ ┌─────────────┐
        │ n8n API     │ │  Database    │ │   7 Skills  │
        │ (Real VPS)  │ │  (1396 nodes) │ │  n8n Expert │
        └─────────────┘ └──────────────┘ └─────────────┘
```

### Componentes del Sistema

#### 1. **Claudio Server** (`claudio_complete.py`)
- FastAPI server en puerto 8000
- Gestiona historial de conversaciones
- Conecta con Claude API
- Implementa todos los MCP tools de n8n
- Base de datos de nodos y plantillas
- 7 skills especializadas

#### 2. **Telegram Bot** (`bot_v2.py`)
- Bot de Telegram con python-telegram-bot
- Se conecta a Claudio Server vía HTTP
- Maneja comandos y mensajes
- Sistema de permisos
- Formato Markdown para respuestas

#### 3. **n8n en VPS**
- Instancia de n8n con Docker
- Accesible vía Traefik
- API REST para gestión de workflows
- Base de datos PostgreSQL

---

## 📦 Requisitos Previos

### Hardware y Software

- **VPS** con al menos 2GB RAM (recomendado 4GB)
- **Ubuntu 20.04+** o **Debian 11+**
- **Docker** y **Docker Compose**
- **Dominio** apuntado a la VPS (ej. n8n.tudominio.com)
- **SSH** access a la VPS

### APIs Necesarias

1. **Telegram Bot Token**
   - Chatea con [@BotFather](https://t.me/BotFather)
   - Comando `/newbot`
   - Guarda el token generado

2. **Anthropic API Key** (Claude)
   - Regístrate en [console.anthropic.com](https://console.anthropic.com)
   - Crea una API key
   - Créditos necesarios (~$1-5 por mes según uso)

3. **n8n API Key** (opcional pero recomendado)
   - Accede a tu instancia n8n
   - Settings → API → Create API Key
   - Permite crear/editar workflows directamente

### Herramientas Locales

- **Git** para clonar repositorios
- **SSH client** para conectar a VPS
- **Python 3.10+** (para desarrollo local)
- **Postman** o similar (para probar APIs)

---

## 🚀 Configuración de la VPS

### 1. Conexión SSH Básica

```bash
# Conectar a tu VPS
ssh ubuntu@tu-vps-ip

# O con clave SSH
ssh -i ~/.ssh/tu_clave ubuntu@tu-vps-ip
```

### 2. Actualización del Sistema

```bash
# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar herramientas básicas
sudo apt install -y curl wget git vim htop net-tools
```

### 3. Configuración de Firewall

```bash
# Permitir SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Habilitar firewall
sudo ufw enable

# Ver estado
sudo ufw status
```

### 4. Configuración de Dominio

```bash
# Editar hosts (opcional)
sudo vim /etc/hosts
# Agregar: tu-ip n8n.tudominio.com
```

---

## 🐳 Instalación de n8n con Docker

### 1. Instalar Docker y Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Añadir usuario al grupo docker
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 2. Crear Directorio para n8n

```bash
# Crear directorios
mkdir -p ~/n8n
cd ~/n8n

# Crear docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: "3.8"
services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.aicorebots.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.aicorebots.com/
      - GENERIC_TIMEZONE=America/Mexico_City
      - N8N_ENCRYPTION_KEY=tu_clave_secreta_larga_aleatoria
      - N8N_API_KEY=habilitar_api_key_despues
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n-local:/data/local
    networks:
      - traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(`n8n.aicorebots.com`)"
      - "traefik.http.routers.n8n.entrypoints=websecure"
      - "traefik.http.routers.n8n.tls.certresolver=letsencrypt"
      - "traefik.http.services.n8n.loadbalancer.server.port=5678"

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n_password
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - traefik

  traefik:
    image: traefik:v2.10
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - ./acme.json:/acme.json
    networks:
      - traefik

volumes:
  n8n_data:
  postgres_data:

networks:
  traefik:
    external: true
EOF
```

### 3. Configurar Traefik

```bash
# Crear configuración de Traefik
cat > traefik.yml << 'EOF'
api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: tu-email@ejemplo.com
      storage: /acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
EOF

# Crear archivo vacío para certificados
touch acme.json
chmod 600 acme.json

# Crear red externa
docker network create traefik 2>/dev/null || true
```

### 4. Iniciar n8n

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f n8n

# Verificar contenedores
docker ps
```

### 5. Configurar API Key de n8n

```bash
# Acceder a n8n
https://n8n.tudominio.com

# 1. Crear usuario administrador
# 2. Settings → API
# 3. Create API Key
# 4. Guardar la API key
```

---

## 🤖 Claudio: El Asistente n8n con IA

### ¿Qué es Claudio?

**Claudio** es un asistente experto en n8n que combina:

1. **Claude API** de Anthropic para IA
2. **n8n-MCP** para acceso a herramientas n8n
3. **Base de datos** de 1,396 nodos y 2,709+ plantillas
4. **7 skills especializadas** en diferentes aspectos de n8n

### Estructura del Proyecto

```
telegram-claude-bot/
├── claudio_complete.py      # Servidor principal
├── bot_v2.py                # Bot de Telegram
├── n8n_mcp_tools.py         # Cliente n8n API
├── n8n_database.py          # Base de datos de nodos
├── skills/                  # Skills especializadas
│   ├── __init__.py
│   ├── n8n_expression_syntax.py
│   └── n8n_other_skills.py
├── requirements.txt
├── .env.example
└── deploy.sh
```

### Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/bot_n8n.git
cd bot_n8n/telegram-claude-bot

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env
```

### Configuración de Variables de Entorno

```bash
# .env
TELEGRAM_TOKEN=tu_token_de_bot_father
ANTHROPIC_API_KEY=tu_api_key_de_anthropic
N8N_API_KEY=tu_api_key_de_n8n
N8N_INSTANCE_URL=http://localhost
N8N_HOST_HEADER=n8n.tudominio.com
CLADIO_PORT=8000
CLADIO_SERVER_URL=http://localhost:8000
REQUEST_TIMEOUT=60
ALLOWED_USERS=  # Vacío = todos permitidos
```

### Ejecutar Localmente

```bash
# Terminal 1: Iniciar Claudio Server
python claudio_complete.py

# Terminal 2: Iniciar Bot de Telegram
python bot_v2.py
```

---

## 📱 Bot de Telegram

### Características del Bot

- **Comandos básicos**: `/start`, `/help`, `/health`, `/clear`
- **Conversación continua** con historial
- **Sistema de permisos** de usuarios
- **Respuestas en formato Markdown**
- **Indicador de "escribiendo..."**
- **Manejo de mensajes largos** (división en chunks)

### Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida con capacidades |
| `/help` | Muestra ayuda y ejemplos de uso |
| `/health` | Verifica estado del servidor Claudio |
| `/clear` | Limpia historial de conversación |

### Ejemplos de Uso

```
Usuario: "¿Cómo creo un workflow de webhook a Slack?"
Claudio: [Proporciona pasos detallados con configuración]

Usuario: "Busca nodos para enviar emails"
Claudio: [Lista nodos de email disponibles con descripciones]

Usuario: "Valida esta expresión: {{$json.email}}"
Claudio: [Advierte que debe ser $json.body.email para webhooks]
```

---

## 🎓 Skills y MCP de n8n

### 1. n8n Expression Syntax
Validación de expresiones n8n ({{$json}}, {{$node}}, etc.)

### 2. n8n MCP Tools Expert
Guía para usar herramientas n8n-MCP

### 3. n8n Workflow Patterns
Patrones arquitectónicos de workflows (webhook, HTTP API, etc.)

### 4. n8n Validation Expert
Interpretación de errores de validación

### 5. n8n Node Configuration
Configuración de nodos según operación

### 6. n8n Code JavaScript
Mejores prácticas para Code nodes

### 7. n8n Code Python
Limitaciones y workarounds para Python

### Base de Datos de Nodos

**1,396 nodos disponibles**:
- 812 nodos core
- 584 nodos community

Categorías principales:
- **Triggers** (45): webhook, schedule, manual, etc.
- **AI/LangChain** (12): AI Agent, vector stores, etc.
- **Comunicación** (85): Slack, Discord, Telegram, Email
- **HTTP/API** (50): HTTP Request, GraphQL
- **Transformación** (75): Set, Code, Merge, Switch
- **Base de datos** (95): Postgres, MySQL, MongoDB
- **Productividad** (120): Notion, Google Sheets, Jira
- **Utilidades** (60): Sleep, Convert File, etc.

### Plantillas de Workflows

**2,709+ plantillas** organizadas por:
- Categoría (webhook, api, database, ai, automation)
- Complejidad (simple, medium, advanced)
- Tiempo de setup (5-30 minutos)

---

## 🚀 Despliegue Completo en VPS

### Script de Despliegue Automatizado

```bash
#!/bin/bash
# deploy_complete.sh

set -e

VPS_USER="ubuntu"
VPS_HOST="tu-vps-ip"
APP_DIR="/opt/claudio-bot"
SERVICE_USER="claudio"

echo "=== Despliegue de Claudio Bot ==="

# 1. Preparar VPS
ssh "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3 python3-pip python3-venv git
    sudo useradd -m -s /bin/bash claudio || true
    sudo mkdir -p /opt/claudio-bot
    sudo chown -R claudio:claudio /opt/claudio-bot
ENDSSH

# 2. Subir archivos
scp claudio_complete.py bot_v2.py requirements.txt .env.example \
    "${VPS_USER}@${VPS_HOST}:/tmp/"

ssh "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    sudo mv /tmp/*.py /tmp/*.txt /opt/claudio-bot/
    cd /opt/claudio-bot
    
    # Crear venv
    sudo -u claudio python3 -m venv venv
    sudo -u claudio venv/bin/pip install -r requirements.txt
    
    # Configurar .env
    if [ ! -f .env ]; then
        sudo -u claudio cp .env.example .env
        echo "⚠️ Edita .env con tus API keys"
    fi
ENDSSH

# 3. Crear servicios systemd
ssh "${VPS_USER}@${VPS_HOST}" << 'ENDSSH'
    # Servicio Claudio Server
    sudo tee /etc/systemd/system/claudio-server.service > /dev/null << 'SVCEOF'
[Unit]
Description=Claudio Server
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python claudio_complete.py
Restart=always

[Install]
WantedBy=multi-user.target
SVCEOF

    # Servicio Telegram Bot
    sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null << 'SVCEOF'
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python bot_v2.py
Restart=always

[Install]
WantedBy=multi-user.target
SVCEOF

    sudo systemctl daemon-reload
    sudo systemctl enable claudio-server claudio-telegram-bot
ENDSSH

echo "✅ Despliegue completo. Edita .env y reinicia servicios."
```

### Ejecutar Despliegue

```bash
chmod +x deploy_complete.sh
./deploy_complete.sh
```

### Configurar en VPS

```bash
# Conectar a VPS
ssh ubuntu@tu-vps-ip

# Editar configuración
sudo nano /opt/claudio-bot/.env

# Reiniciar servicios
sudo systemctl restart claudio-server claudio-telegram-bot

# Verificar estado
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot

# Ver logs
sudo journalctl -u claudio-server -f
sudo journalctl -u claudio-telegram-bot -f
```

---

## 💬 Prompts Útiles para Claudio

### Para Búsqueda de Nodos

```
"Busca nodos para conectar con Slack"
"¿Qué nodos hay para bases de datos?"
"Necesito nodos para procesamiento de archivos"
"Muestra nodos de AI disponibles"
```

### Para Creación de Workflows

```
"Crea un workflow de webhook a Slack"
"Necesito un workflow para sincronizar databases"
"¿Cómo creo un workflow de AI agent?"
"Workflow para reporte diario por email"
```

### Para Validación

```
"Valida esta configuración de nodo HTTP Request"
"¿Por qué falla mi expresión {{$json.email}}?"
"Revisa si está bien mi workflow de IF node"
"¿Por qué no conecta mi nodo Merge?"
```

### Para Solución de Problemas

```
"Mi webhook no recibe datos, ¿qué puede ser?"
"El nodo Switch no funciona como espero"
"Error en Code node: no devuelve datos"
"¿Por qué mi workflow no se activa?"
```

### Para Plantillas

```
"Busca templates simples de webhook"
"Plantillas para integración con API"
"Templates avanzados de database sync"
"Ejemplos de workflows con AI"
```

---

## 🔧 Troubleshooting

### Problema: Bot no responde

**Diagnóstico:**
```bash
# Verificar servicios
sudo systemctl status claudio-telegram-bot
sudo systemctl status claudio-server

# Ver logs
sudo journalctl -u claudio-telegram-bot -n 50
sudo journalctl -u claudio-server -n 50

# Verificar puerto
curl http://localhost:8000/health
```

**Soluciones:**
1. Reiniciar servicios
2. Verificar API keys en .env
3. Verificar conectividad con n8n

### Problema: Error de API de n8n

**Diagnóstico:**
```bash
# Verificar n8n
docker ps | grep n8n
curl -H "X-N8N-API-KEY: tu-key" http://localhost:5678/api/v1/workflows
```

**Soluciones:**
1. Verificar API key de n8n
2. Verificar N8N_INSTANCE_URL
3. Verificar N8N_HOST_HEADER para Traefik

### Problema: Memoria insuficiente

**Diagnóstico:**
```bash
free -h
df -h
```

**Soluciones:**
1. Aumentar RAM de VPS
2. Configurar swap
3. Limitar historial de conversación

### Problema: Conexión SSH

**Diagnóstico:**
```bash
# Verificar clave SSH
ssh -i ~/.ssh/tu_clave -v ubuntu@tu-vps-ip
```

**Soluciones:**
1. Verificar permisos de clave (600)
2. Agregar a ssh-agent
3. Verificar firewall

---

## 📚 Referencias de API

### Claudio Server API

#### POST /api/chat
```json
{
  "message": "Crear workflow webhook",
  "user_id": 123456789,
  "user_name": "Usuario",
  "clear_history": false
}
```

#### GET /health
```json
{
  "status": "healthy",
  "timestamp": "2026-04-07T10:00:00",
  "anthropic": true,
  "n8n": {
    "connected": true,
    "instance": "http://localhost"
  }
}
```

#### GET /api/tools
```json
{
  "n8n_api": [
    "list_workflows",
    "get_workflow",
    "create_workflow",
    "update_workflow",
    "activate_workflow"
  ],
  "database": [
    "search_nodes",
    "get_node",
    "validate_node",
    "search_templates",
    "validate_expression"
  ],
  "stats": {
    "nodes_total": 1396,
    "templates_total": 2709
  }
}
```

### n8n API Endpoints

```
GET    /api/v1/workflows           - Listar workflows
GET    /api/v1/workflows/{id}      - Obtener workflow
POST   /api/v1/workflows           - Crear workflow
PATCH  /api/v1/workflows/{id}      - Actualizar workflow
DELETE /api/v1/workflows/{id}      - Eliminar workflow
POST   /api/v1/workflows/{id}/activate   - Activar workflow
POST   /api/v1/workflows/{id}/deactivate - Desactivar workflow
GET    /api/v1/executions          - Listar ejecuciones
```

---

## 📖 Referencias y Recursos

### Documentación Oficial

- **n8n**: https://docs.n8n.io
- **n8n-MCP**: https://github.com/n8n-io/n8n-mcp
- **Anthropic Claude**: https://docs.anthropic.com
- **python-telegram-bot**: https://python-telegram-bot.readthedocs.io

### Repositorios Útiles

- **n8n Community Nodes**: https://n8n.io integrations
- **n8n Templates**: https://n8n.io workflows
- **Claude Code**: https://github.com/anthropics/claude-code

### Comunidades

- **n8n Community**: https://community.n8n.io
- **n8n Discord**: https://discord.gg/n8n
- **Anthropic Discord**: https://discord.gg/anthropic

---

## 📝 Licencia

MIT License - Ver archivo LICENSE para detalles

---

## 🙏 Agradecimientos

- **n8n** - Plataforma de workflow automation
- **Anthropic** - Claude API
- **Telegram** - Plataforma de mensajería

---

**Fin del Tutorial Completo**

Para más información, consulta el repositorio: https://github.com/tu-usuario/bot_n8n
