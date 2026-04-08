# 📘 Guía de Instalación Completa - Claudio Bot v4.6.1

> **Guía paso a paso para instalar y configurar Claudio Bot con múltiples proveedores de IA**

---

## 📋 Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Métodos de Instalación](#métodos-de-instalación)
3. [Configuración de Proveedores IA](#configuración-de-proveedores-ia)
4. [Configuración de Telegram](#configuración-de-telegram)
5. [Integración con n8n](#integración-con-n8n)
6. [Despliegue en VPS](#despliegue-en-vps)
7. [Verificación Post-Instalación](#verificación-post-instalación)
8. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

### Sistema Operativo
- **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+
- **Windows**: Windows 10+ con WSL2
- **macOS**: macOS 11+ (Big Sur)

### Software Necesario
```bash
# Python 3.9 o superior
python3 --version

# Git (para clonar el repositorio)
git --version

# pip (gestor de paquetes Python)
pip3 --version
```

### Hardware Mínimo
- **CPU**: 2 cores
- **RAM**: 2GB (4GB recomendado para Ollama)
- **Disco**: 10GB disponibles
- **Red**: Conexión a internet estable

---

## Métodos de Instalación

### 🎯 Método 1: Instalador Interactivo (Recomendado)

El instalador te guiará paso a paso con preguntas interactivas.

```bash
# Clonar el repositorio
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n

# Ejecutar instalador
python3 install.py
```

**El instalador te preguntará:**

#### 1️⃣ **Selección de Proveedor IA**
```
═══════════════════════════════════════════════════════
    CONFIGURACIÓN DE PROVEEDOR IA
═══════════════════════════════════════════════════════

Selecciona tu proveedor IA principal:

[1] Multi-Proveedor (con auto-fallback) ⭐ RECOMENDADO
    Intenta múltiples proveedores en orden
    
[2] Anthropic Claude (claude-sonnet-4)
    Más potente, pero más costoso
    
[3] OpenAI GPT-4 (gpt-4o-mini)
    Rápido y económico
    
[4] Google Gemini (gemini-2.5-pro)
    Gratis hasta cierto límite
    
[5] Alibaba Qwen
    Muy económico
    
[6] DeepSeek
    La opción más barata
    
[7] Ollama (Local y GRATIS)
    Requiere descargar modelo
    
[8] Modelo Personalizado
    Usa tu propia API compatible

Tu elección [1-8]: 
```

#### 2️⃣ **Configuración de API Keys**
```
═══════════════════════════════════════════════════════
    CONFIGURACIÓN DE API KEYS
═══════════════════════════════════════════════════════

Ingresa tu API Key para [Proveedor]:
(Si no tienes una, presiona Enter para omitir)

API Key: 
```

#### 3️⃣ **Configuración de Telegram**
```
═══════════════════════════════════════════════════════
    CONFIGURACIÓN DE TELEGRAM
═══════════════════════════════════════════════════════

1. Abre Telegram y busca @BotFather
2. Envía /newbot y sigue las instrucciones
3. Copia el token que te da BotFather

Tu Token de Telegram: 
```

#### 4️⃣ **Configuración de Seguridad**
```
═══════════════════════════════════════════════════════
    CONFIGURACIÓN DE SEGURIDAD
═══════════════════════════════════════════════════════

Obtén tu User ID:
1. Abre Telegram y busca @userinfobot
2. Envía /start
3. Copia tu ID numérico

Tu User ID: 
```

#### 5️⃣ **Integración con n8n (Opcional)**
```
═══════════════════════════════════════════════════════
    INTEGRACIÓN CON N8N (OPCIONAL)
═══════════════════════════════════════════════════════

¿Quieres integrar con n8n? [y/N]: 

Si es así, ingresa:
URL de tu instancia n8n: https://n8n.tudominio.com
API Key de n8n: 
```

#### 6️⃣ **Modo de Despliegue**
```
═══════════════════════════════════════════════════════
    MODO DE DESPLIEGUE
═══════════════════════════════════════════════════════

[1] Local (Desarrollo)
    Ejecutar en tu máquina local
    
[2] VPS (Producción) ⭐ RECOMENDADO
    Desplegar en servidor VPS
    
[3] Docker
    Usar contenedores Docker

Tu elección [1-3]: 
```

#### 7️⃣ **Confirmación**
```
═══════════════════════════════════════════════════════
    RESUMEN DE CONFIGURACIÓN
═══════════════════════════════════════════════════════

Proveedor: Multi-Proveedor
Modelos: openai, ollama, deepseek, gemini, anthropic
Telegram: ✓ Configurado
n8n: ✓ Integrado
Modo: VPS

¿Guardar configuración e instalar? [y/N]: 
```

---

### 📦 Método 2: Instalación Manual

Si prefieres configurar todo manualmente:

```bash
# 1. Clonar repositorio
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar y editar configuración
cp .env.example .env
nano .env  # o tu editor favorito

# 5. Ejecutar
python3 bot_v2.py           # Terminal 1
python3 claudio_complete.py # Terminal 2
```

---

## Configuración de Proveedores IA

### 🟦 Anthropic Claude

```bash
# 1. Crear cuenta en console.anthropic.com
# 2. Ir a Settings → API Keys
# 3. Crear nueva API Key

# En .env:
ANTHROPIC_API_KEY=sk-ant-tu-key-aqui
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

**Modelos disponibles:**
- `claude-sonnet-4-20250514` - Más reciente y capaz
- `claude-3-5-sonnet-20241022` - Potente y económico
- `claude-3-haiku-20240307` - Rápido y barato

### 🟩 OpenAI

```bash
# 1. Ir a platform.openai.com
# 2. Settings → API Keys
# 3. Crear nueva API Key

# En .env:
OPENAI_API_KEY=sk-proj-tu-key-aqui
OPENAI_MODEL=gpt-4o-mini
```

**Modelos disponibles:**
- `gpt-4o-mini` - Rápido y económico ⭐
- `gpt-4o` - Más capaz
- `gpt-4-turbo` - Potente
- `gpt-3.5-turbo` - Económico (legacy)

### 🟨 Google Gemini

```bash
# 1. Ir a ai.google.dev
# 2. Create API Key
# 3. Copiar la key

# En .env:
GEMINI_API_KEY=AIzaSy-tu-key-aqui
GEMINI_MODEL=gemini-2.5-pro
```

**Modelos disponibles:**
- `gemini-2.5-pro` - Más potente ⭐
- `gemini-2.5-flash` - Rápido
- `gemini-3.1-pro-preview` - Último modelo (preview)
- `gemini-3.1-flash-lite-preview` - Ultra rápido (preview)

### 🟧 Alibaba Qwen

```bash
# 1. Ir a dashscope.aliyun.com
# 2. Crear API Key

# En .env:
QWEN_API_KEY=tu-key-aqui
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**Modelos disponibles:**
- `qwen-plus` - Recomendado
- `qwen-turbo` - Rápido y barato
- `qwen-max` - Más potente

### 🟪 DeepSeek

```bash
# 1. Ir a platform.deepseek.com
# 2. Crear API Key

# En .env:
DEEPSEEK_API_KEY=sk-tu-key-aqui
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**Modelos disponibles:**
- `deepseek-chat` - Chat general ⭐
- `deepseek-coder` - Especializado en código

### 🟫 Ollama (GRATIS y Local)

```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Descargar modelo
ollama pull phi3:mini  # 2.2GB - rápido y eficiente
# o
ollama pull llama3      # 4GB - más potente

# 3. Iniciar servicio
sudo systemctl start ollama
sudo systemctl enable ollama

# En .env:
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

**Modelos disponibles:**
- `phi3:mini` - Rápido, 2.2GB ⭐
- `llama3` - Potente, 4GB
- `mistral` - Equilibrado
- `codellama` - Para código

---

## Configuración de Telegram

### 1. Crear el Bot

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Sigue las instrucciones:
   - Escribe un nombre para tu bot (ej: "Claudio n8n")
   - Escribe un username (ej: "claudio_n8n_bot")
4. Copia el **token** que te da (ej: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Obtener tu User ID

1. Abre Telegram y busca **@userinfobot**
2. Envía `/start`
3. Copia tu **ID numérico** (ej: `123456789`)

### 3. Configurar el Bot

```bash
# En .env:
TELEGRAM_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ALLOWED_USERS=123456789  # Tu ID
ALLOWED_ADMIN_USERS=123456789  # Tu ID como admin
```

---

## Integración con n8n

### Opción A: n8n Cloud

```bash
# En .env:
N8N_INSTANCE_URL=https://app.n8n.cloud
N8N_API_KEY=tu_api_key_de_n8n_cloud
```

### Opción B: n8n Self-Hosted

```bash
# En .env:
N8N_INSTANCE_URL=https://n8n.tudominio.com
N8N_API_KEY=tu_api_key
N8N_HOST_HEADER=n8n.tudominio.com  # Para Traefik
```

### Obtener API Key de n8n

1. Entra a tu instancia n8n
2. Ve a **Settings** → **API**
3. Haz clic en **Create API Key**
4. Dale un nombre (ej: "Claudio Bot")
5. Copia la key generada

---

## Despliegue en VPS

### 🚀 Script Automático

```bash
# Usar el script de despliegue
python3 deploy_vps.py
```

**El script te preguntará:**
1. IP o dominio del VPS
2. Usuario SSH
3. Contraseña o clave SSH
4. Confirmación de despliegue

### 📝 Manualmente

#### 1. Conectar al VPS
```bash
ssh ubuntu@tu-vps-ip
```

#### 2. Instalar dependencias
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

#### 3. Clonar repositorio
```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
```

#### 4. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Configurar
```bash
cp .env.example .env
nano .env  # Editar con tus credenciales
```

#### 6. Crear servicios systemd
```bash
# Servicio del servidor
sudo tee /etc/systemd/system/claudio-server.service << EOF
[Unit]
Description=Claudio COMPLETE Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bot_n8n
EnvironmentFile=/home/ubuntu/bot_n8n/.env
ExecStart=/home/ubuntu/bot_n8n/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Servicio del bot
sudo tee /etc/systemd/system/claudio-telegram-bot.service << EOF
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bot_n8n
EnvironmentFile=/home/ubuntu/bot_n8n/.env
ExecStart=/home/ubuntu/bot_n8n/venv/bin/python bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### 7. Iniciar servicios
```bash
sudo systemctl daemon-reload
sudo systemctl enable claudio-server claudio-telegram-bot
sudo systemctl start claudio-server claudio-telegram-bot
```

#### 8. Verificar estado
```bash
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot
```

---

## Verificación Post-Instalación

### ✅ Checklist de Verificación

- [ ] Bot responde en Telegram
- [ ] Comando `/status` funciona
- [ ] Proveedor IA responde correctamente
- [ ] n8n está conectado (si configuraste)
- [ ] Auto-fallback funciona (si configuraste multi-provider)

### 🧪 Pruebas Rápidas

```bash
# En Telegram, prueba estos comandos:

/start              # Debería darte la bienvenida
/status              # Debería mostrar estado actual
/models              # Debería listar modelos disponibles
/hola               # Debería responder

# Si integraste n8n:
cuantos workflows tienes?   # Debería listar tus workflows
```

### 📊 Ver Logs

```bash
# En VPS
sudo journalctl -u claudio-server -f
sudo journalctl -u claudio-telegram-bot -f
```

---

## Solución de Problemas

### ❌ "Bot no responde"

**Solución:**
```bash
# 1. Verificar que los servicios estén corriendo
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot

# 2. Verificar TOKEN en .env
grep TELEGRAM_TOKEN .env

# 3. Reiniciar servicios
sudo systemctl restart claudio-server claudio-telegram-bot
```

### ❌ "Error: timeout"

**Solución:**
```bash
# Aumentar timeout en .env
echo "REQUEST_TIMEOUT=120" >> .env

# Cambiar a proveedor más rápido
/switch openai  # en Telegram
```

### ❌ "n8n connection error"

**Solución:**
```bash
# Verificar URL y API key
grep N8N_ .env

# Probar conexión manual
curl -H "X-N8N-API-KEY: tu_key" https://n8n.tu-url.com/api/v1/workflows
```

### ❌ "Ollama not responding"

**Solución:**
```bash
# Verificar que Ollama esté corriendo
sudo systemctl status ollama

# Descargar modelo si falta
ollama pull phi3:mini
```

### ❌ "OpenAI API error"

**Solución:**
```bash
# Verificar API key y saldo
grep OPENAI_API_KEY .env

# Probar con otro modelo
OPENAI_MODEL=gpt-4o-mini  # más económico
```

---

## 🎞️ Vídeo Tutoriales

### Instalación Básica
[![Instalación Básica](https://img.youtube.com/vi/XXXXX/maxresdefault.jpg)](https://youtube.com/watch?v=XXXXX)

### Configuración Multi-Proveedor
[![Multi-Proveedor](https://img.youtube.com/vi/XXXXX/maxresdefault.jpg)](https://youtube.com/watch?v=XXXXX)

### Despliegue en VPS
[![Despliegue VPS](https://img.youtube.com/vi/XXXXX/maxresdefault.jpg)](https://youtube.com/watch?v=XXXXX)

---

## 📞 Soporte

Si necesitas ayuda:

- 📖 [Wiki del Proyecto](https://github.com/LeonardoPS1/bot_n8n/wiki)
- 🐛 [Reportar Issues](https://github.com/LeonardoPS1/bot_n8n/issues)
- 💬 [Discord](https://discord.gg/claudio-bot)
- 📧 Email: support@claudio-bot.com

---

**¡Listo! Tu bot Claudio debería estar funcionando.** 🎉

[← Volver al README](README.md)
