# 🤖 GUIA DE INSTALACIÓN COMPLETA

## Claudio Bot - Expert n8n Workflow Assistant

---

**Versión:** 4.1
**Fecha:** Abril 2026
**Repositorio:** https://github.com/LeonardoPS1/bot_n8n

---

## 📋 ÍNDICE

1. [Introducción](#1-introducción)
2. [Requisitos Previos](#2-requisitos-previos)
3. [Obtención de Credenciales](#3-obtención-de-credenciales)
4. [Guía de Instalación Paso a Paso](#4-guía-de-instalación-paso-a-paso)
5. [Post-Instalación](#5-post-instalación)
6. [Prueba de Funcionamiento](#6-prueba-de-funcionamiento)
7. [Solución de Problemas](#7-solución-de-problemas)
8. [Preguntas Frecuentes](#8-preguntas-frecuentes)

---

## 1. INTRODUCCIÓN

### ¿Qué es Claudio Bot?

**Claudio Bot** es un asistente inteligente para Telegram especializado en la automatización con n8n. Powered por IA (Anthropic Claude o OpenAI GPT-4), Claudio te ayuda a:

- ✅ Crear workflows de n8n desde descripciones en lenguaje natural
- ✅ Validar expresiones de n8n y corregir errores
- ✅ Generar código para nodos Code (JavaScript/Python)
- ✅ Buscar y explicar los 1,396 nodos disponibles
- ✅ Acceder a 2,709+ plantillas de workflows
- ✅ Debuggear problemas en tus workflows

### Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🧠 **IA Avanzada** | Claude 3.5 Sonnet o GPT-4 para comprensión técnica |
| 📊 **Base de Datos n8n** | Acceso a 1,396 nodos y 2,709+ plantillas |
| 🔧 **Multi-Proveedor** | Anthropic, OpenAI, Ollama o múltiples |
| 🐳 **Docker Ready** | Despliegue fácil con contenedores |
| 🔒 **Seguro** | Restricción por usuario de Telegram |
| 🚀 **Auto-Scaling** | Listo para VPS y producción |

### Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        USUARIO TELEGRAM                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    BOT DE TELEGRAM                          │
│                   (bot_v2.py)                               │
│  • Recibe mensajes                                          │
│  • Gestiona conversaciones                                  │
│  • Entrega respuestas                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CLAUDIO SERVER                              │
│               (claudio_complete.py)                         │
│  • FastAPI Server                                           │
│  • Lógica de IA                                             │
│  • Herramientas n8n MCP                                     │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├──► Anthropic API (Claude)
       ├──► OpenAI API (GPT-4)
       ├──► Ollama API (Local)
       └──► n8n Instance (Opcional)
```

---

## 2. REQUISITOS PREVIOS

### Requisitos por Tipo de Instalación

#### 🖥️ Instalación Local

| Requisito | Versión Mínima | Notas |
|-----------|----------------|-------|
| Python | 3.9+ | Requerido |
| pip | Última versión | Viene con Python |
| Git | Cualquier versión | Para clonar el repo |
| RAM | 2 GB | 4 GB recomendado |
| Espacio Disco | 500 MB | Para dependencias |

#### 🌐 Instalación VPS

| Requisito | Versión Mínima | Notas |
|-----------|----------------|-------|
| SO | Ubuntu 20.04+ / Debian 11+ | Systemd requerido |
| Python | 3.9+ | Incluido en Ubuntu 20.04+ |
| RAM | 1 GB | 2 GB recomendado |
| Espacio Disco | 1 GB | Para instalación completa |
| Acceso SSH | Llave o password | Para configuración |

#### 🐳 Instalación Docker

| Requisito | Versión Mínima | Notas |
|-----------|----------------|-------|
| Docker | 20.10+ | Requerido |
| Docker Compose | 2.0+ | Requerido |
| RAM | 2 GB | 4 GB recomendado |
| Espacio Disco | 2 GB | Para imágenes |

### Verificar Requisitos

```bash
# Verificar Python
python3 --version

# Verificar pip
pip3 --version

# Verificar Git
git --version

# Verificar Docker (opcional)
docker --version
docker-compose --version
```

---

## 3. OBTENCIÓN DE CREDENCIALES

### 3.1 Telegram Bot Token

**Tiempo estimado:** 2 minutos

**Pasos:**

1. Abre Telegram y busca **@BotFather**
2. Inicia el chat con el comando `/start`
3. Crea un nuevo bot con `/newbot`
4. Sigue las instrucciones:
   - Elige un nombre para tu bot (ej: "Claudio Assistant")
   - Elige un usuario para tu bot (ej: "claudio_assistant_bot")
   - El usuario debe terminar en "bot"
5. **Copia el token** que BotFather te da

**Ejemplo de token:**
```
7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ **IMPORTANTE:** Guarda este token de forma segura. No lo compartas públicamente.

---

### 3.2 Anthropic API Key (Claude)

**Tiempo estimado:** 3 minutos

**Pasos:**

1. Ve a https://console.anthropic.com
2. Regístrate o inicia sesión
3. Navega a **Settings → API Keys**
4. Haz clic en **"Create Key"**
5. Dale un nombre a tu key (ej: "Claudio Bot")
6. **Copia la API Key**

**Ejemplo de API Key:**
```
sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Modelos Disponibles:**

| Modelo | Descripción | Uso Recomendado |
|--------|-------------|-----------------|
| claude-sonnet-4-20250514 | Más reciente, mejor calidad | Producción |
| claude-3-5-sonnet-20241022 | Excelente calidad | Alternativa |
| claude-3-haiku-20240307 | Rápido, económico | Desarrollo |

**Precios (aproximados):**
- Sonnet 4: ~$3/1M tokens input, ~$15/1M tokens output
- Haiku: ~$0.25/1M tokens input, ~$1.25/1M tokens output

---

### 3.3 OpenAI API Key (GPT-4)

**Tiempo estimado:** 3 minutos

**Pasos:**

1. Ve a https://platform.openai.com
2. Regístrate o inicia sesión
3. Navega a **API Keys → Create new secret key**
4. Dale un nombre a tu key
5. **Copia la API Key**

**Ejemplo de API Key:**
```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Modelos Disponibles:**

| Modelo | Descripción | Uso Recomendado |
|--------|-------------|-----------------|
| gpt-4o | Más reciente, mejor calidad | Producción |
| gpt-4-turbo | Alta calidad | Alternativa |
| gpt-3.5-turbo | Rápido, económico | Desarrollo |

---

### 3.4 n8n API Key (OPCIONAL)

**Tiempo estimado:** 2 minutos

**Pasos:**

1. Accede a tu instancia de n8n
2. Ve a **Settings → API**
3. Haz clic en **"Create API Key"**
4. Dale un nombre (ej: "Claudio Bot")
5. **Copia la API Key**

> **Nota:** Esta key es opcional. Sin ella, Claudio solo podrá hacer lecturas públicas.

---

### 3.5 Tu Telegram User ID (OPCIONAL)

**Tiempo estimado:** 1 minuto

**Pasos:**

1. Abre Telegram y busca **@userinfobot**
2. Envía `/start`
3. **Copia tu ID** (es un número)

**Ejemplo:**
```
Id: 123456789
```

> **Nota:** Necesario solo si quieres restringir el acceso a tu bot.

---

## 4. GUÍA DE INSTALACIÓN PASO A PASO

### MÉTODO 1: Instalador Interactivo (RECOMENDADO)

Este es el método más simple. El instalador te guiará paso a paso.

#### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
```

#### Paso 2: Ejecutar el Instalador

```bash
python3 install.py
```

#### Paso 3: Seguir el Asistente

El instalador te hará las siguientes preguntas:

---

**📋 PASO 0: NOMBRE DEL PROYECTO**

```
→ Nombre del proyecto (sin espacios) [claudio-bot]:
```

**Descripción:** El nombre se usará para:
- Nombre de la carpeta de instalación
- Nombre de los servicios systemd
- Identificación en logs

**Ejemplo:** `claudio-bot`

---

**📋 PASO 1: PROVEEDOR DE IA**

```
→ Selecciona tu Proveedor de IA

    [1] Anthropic (Claude) - Recomendado para n8n (default)
    [2] OpenAI (GPT-4/GPT-3.5) - Alternativa popular
    [3] Ollama - Local y gratuito
    [4] Multi-proveedor - Anthropic + OpenAI

→ Selecciona una opción [1-4]:
```

**Recomendación:** Anthropic (Claude) tiene mejor comprensión técnica para n8n.

---

**Si eliges Anthropic:**

```
→ Ingresa tu API Key de Anthropic (sk-ant-...): ********
→ ¿Qué modelo de Claude deseas usar?

    [1] claude-sonnet-4-20250514 (default)
    [2] claude-3-5-sonnet-20241022
    [3] claude-3-haiku-20240307

→ Selecciona una opción [1-3]:
```

---

**Si eliges OpenAI:**

```
→ Ingresa tu API Key de OpenAI (sk-...): ********
→ ¿Qué modelo de OpenAI deseas usar?

    [1] gpt-4o (default)
    [2] gpt-4-turbo
    [3] gpt-3.5-turbo

→ Selecciona una opción [1-3]:
```

---

**📋 PASO 2: CONFIGURACIÓN DE TELEGRAM**

```
Claudio funciona como un bot de Telegram.
Si no tienes un bot, crea uno ahora:
  1. Abre @BotFather en Telegram
  2. Envía /newbot
  3. Sigue las instrucciones
  4. Copia el token que BotFather te da

→ ¿Ya tienes el Token de tu Bot? (Y/n): y
→ Ingresa el Token de tu Bot de Telegram: ********
```

---

**📋 PASO 3: INTEGRACIÓN CON N8N (OPCIONAL)**

```
Claudio puede conectarse a tu instancia de n8n para:
  • Crear workflows directamente en tu instancia
  • Validar nodos y conexiones
  • Acceder a tus workflows existentes

→ ¿Deseas integrar n8n? (y/N): n
```

**Si respondes "sí":**

```
→ URL de tu instancia n8n [https://n8n.aicorebots.com]: https://n8n.miempresa.com
→ Header Host para proxy/dominio [n8n.miempresa.com]:
→ ¿Tienes API Key de n8n? (y/N): y
→ API Key de n8n: ********
```

---

**📋 PASO 4: CONFIGURACIÓN DEL SERVIDOR**

```
Claudio tiene dos componentes:
  • Servidor: API con IA y herramientas n8n
  • Bot: Interfaz de Telegram que conecta con el servidor

→ ¿Dónde deseas ejecutar Claudio?

    [1] Local - Ejecutar en tu computadora (default)
    [2] VPS - Desplegar en servidor remoto
    [3] Docker - Usar contenedores Docker

→ Selecciona una opción [1-3]:
```

---

**Si eliges LOCAL:**

```
→ Puerto para el servidor local [8001]:
```

---

**Si eliges VPS:**

```
→ IP o dominio de tu VPS [51.222.207.250]:
→ Usuario SSH (root/ubuntu) [root]:
→ Directorio de instalación en la VPS [/opt/claudio-bot]:
```

---

**📋 PASO 5: SEGURIDAD**

```
Por seguridad, puedes restringir el acceso a tu bot.
Solo los usuarios que autorices podrán usar el bot.

Para obtener tu Telegram User ID:
  1. Abre @userinfobot en Telegram
  2. Envía /start
  3. Copia tu ID (un número)

→ ¿Deseas restringir el acceso? (y/N): y
→ Ingresa los User IDs permitidos (separados por coma): 123456789,987654321
```

**Opciones:**
- Dejar vacío o `*` = Acceso público
- `123456789,987654321` = Solo esos usuarios

---

**📋 RESUMEN Y CONFIRMACIÓN**

```
======================================================================
          RESUMEN DE CONFIGURACIÓN
======================================================================

  Nombre del Proyecto:  claudio-bot
  Proveedor IA:         ANTHROPIC
  Modelo IA:            claude-sonnet-4-20250514
  Telegram:             Configurado ✓
  n8n:                  Deshabilitado
  Despliegue:           VPS
  Puerto:               8000
  Directorio:           /opt/claudio-bot
  Seguridad:            Restringido

→ ¿Esta configuración es correcta? ¿Continuar? (Y/n): y
```

---

#### Paso 4: Esperar la Instalación

El instalador creará:
- ✅ Archivo `.env` con tu configuración
- ✅ Entorno virtual Python
- ✅ Dependencias instaladas
- ✅ Scripts de inicio
- ✅ Servicios systemd (si es VPS)
- ✅ Script de prueba

---

### MÉTODO 2: Instalación Manual

Si prefieres configurar todo manualmente:

#### Paso 1: Clonar y Preparar

```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Paso 2: Crear Archivo .env

```bash
cp .env.example .env
nano .env  # o tu editor favorito
```

#### Paso 3: Configurar .env

```bash
# ============================================
# TELEGRAM CONFIG
# ============================================
TELEGRAM_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ============================================
# AI PROVIDER CONFIG
# ============================================

# Para Anthropic (Claude)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# O para OpenAI
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# OPENAI_MODEL=gpt-4o

# ============================================
# N8N CONFIG (OPCIONAL)
# ============================================
N8N_API_KEY=your_n8n_api_key_here
N8N_INSTANCE_URL=https://n8n.yourdomain.com
N8N_HOST_HEADER=n8n.yourdomain.com

# ============================================
# SERVER CONFIG
# ============================================
CLADIO_PORT=8000
CLADIO_SERVER_URL=http://localhost:8000
REQUEST_TIMEOUT=60

# ============================================
# SECURITY
# ============================================
ALLOWED_USERS=*  # o user IDs separados por coma
```

#### Paso 4: Iniciar

```bash
# Terminal 1: Servidor
python claudio_complete.py

# Terminal 2: Bot
python bot_v2.py
```

---

## 5. POST-INSTALACIÓN

### 5.1 Verificar Instalación Local

```bash
# Verificar que los archivos existen
ls -la
# Deberías ver: bot_v2.py, claudio_complete.py, n8n_mcp_tools.py, etc.

# Verificar el .env
cat .env

# Verificar dependencias
source venv/bin/activate
pip list
```

### 5.2 Iniciar Claudio (LOCAL)

**En Linux/Mac:**

```bash
# Terminal 1: Iniciar el servidor
./start_server.sh

# Terminal 2: Iniciar el bot
./start.sh
```

**En Windows:**

1. Doble clic en `start_server.bat`
2. Doble clic en `start.bat`

### 5.3 Desplegar en VPS

#### Opción A: Usar el Script Generado

```bash
bash deploy_vps.sh
```

Este script automáticamente:
1. Se conecta a tu VPS
2. Crea el usuario `claudio`
3. Copia todos los archivos
4. Instala dependencias
5. Crea servicios systemd
6. Habilita los servicios

#### Opción B: Manual

```bash
# 1. Conectar a la VPS
ssh root@tu-vps-ip

# 2. Crear usuario
sudo useradd -m -s /bin/bash claudio

# 3. Crear directorio
sudo mkdir -p /opt/claudio-bot
sudo chown -R claudio:claudio /opt/claudio-bot

# 4. Clonar repositorio
sudo -u claudio git clone https://github.com/LeonardoPS1/bot_n8n.git /opt/claudio-bot
cd /opt/claudio-bot

# 5. Instalar dependencias
sudo -u claudio python3 -m venv venv
sudo -u claudio venv/bin/pip install -r requirements.txt

# 6. Configurar .env
sudo -u claudio cp .env.example .env
sudo -u claudio nano .env

# 7. Crear servicios systemd
sudo nano /etc/systemd/system/claudio-server.service
```

**Contenido de `claudio-server.service`:**

```ini
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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Contenido de `claudio-telegram-bot.service`:**

```ini
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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 8. Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable claudio-server claudio-telegram-bot
sudo systemctl start claudio-server claudio-telegram-bot

# 9. Verificar estado
sudo systemctl status claudio-server claudio-telegram-bot
```

### 5.4 Docker

```bash
# Configurar .env primero
cp .env.example .env
nano .env

# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

## 6. PRUEBA DE FUNCIONAMIENTO

### 6.1 Ejecutar Script de Prueba

El instalador crea un script `test_installation.sh` que verifica:

```bash
bash test_installation.sh
```

**El script verificará:**

| Categoría | Tests |
|-----------|-------|
| **Sistema** | Python, pip, git |
| **Archivos** | .env, claudio_complete.py, bot_v2.py, skills/ |
| **Python** | venv, paquetes instalados |
| **Configuración** | Tokens configurados correctamente |
| **Servicios** | systemd creados y activos |
| **Health** | Servidor respondiendo |

### 6.2 Prueba Manual

#### 1. Verificar Servidor

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{"status": "healthy", "service": "claudio-server"}
```

#### 2. Verificar Logs del Bot

```bash
# En VPS
sudo journalctl -u claudio-telegram-bot -f

# Ver output del bot
# Deberías ver: "Claudio Bot started successfully"
```

#### 3. Probar en Telegram

1. Abre Telegram
2. Busca tu bot por su usuario
3. Inicia chat con `/start`
4. Envía un mensaje de prueba

**Ejemplos de mensajes de prueba:**

```
/start
```

```
Ayuda
```

```
Crea un workflow de webhook que envíe un mensaje a Slack
```

```
Valida esta expresión: {{$json.data.user.email}}
```

---

## 7. SOLUCIÓN DE PROBLEMAS

### 7.1 El Bot No Responde

**Síntoma:** Bot en línea pero no responde mensajes.

**Posibles causas:**

1. **Servidor no iniciado**
```bash
# Verificar estado
sudo systemctl status claudio-server

# Ver logs
sudo journalctl -u claudio-server -n 50

# Solución: Reiniciar
sudo systemctl restart claudio-server
```

2. **Token inválido**
```bash
# Verificar token
cat .env | grep TELEGRAM_TOKEN

# Probar token manualmente
curl https://api.telegram.org/bot<TU_TOKEN>/getMe
```

3. **Puerto bloqueado**
```bash
# Verificar puerto
netstat -tlnp | grep 8000

# Abrir puerto si es necesario
sudo ufw allow 8000
```

### 7.2 Error de API Key

**Síntoma:** Error en logs sobre API key inválida.

**Solución:**

```bash
# Editar .env
nano /opt/claudio-bot/.env

# Verificar formato:
# Anthropic: sk-ant-...
# OpenAI: sk-...

# Reiniciar servicios
sudo systemctl restart claudio-server claudio-telegram-bot
```

### 7.3 Error de Conexión n8n

**Síntoma:** No se puede conectar a n8n.

**Solución:**

```bash
# Verificar configuración
cat .env | grep N8N

# Test de conexión
curl -H "X-N8N-API-KEY: <TU_KEY>" https://n8n.tudominio.com/api/v1/workflows

# Verificar que la URL sea correcta
# Debe incluir https:// y el dominio correcto
```

### 7.4 Error de Dependencias

**Síntoma:** ImportError o ModuleNotFoundError.

**Solución:**

```bash
# Reinstalar dependencias
cd /opt/claudio-bot
sudo -u claudio venv/bin/pip install -r requirements.txt

# Si hay errores específicos
sudo -u claudio venv/bin/pip install --upgrade <paquete>
```

### 7.5 Servicios systemd No Inician

**Síntoma:** systemctl status muestra "failed".

**Solución:**

```bash
# Ver logs detallados
sudo journalctl -u claudio-server -n 100 --no-pager

# Verificar usuario
sudo systemctl cat claudio-server
# Asegúrate que el usuario "claudio" existe

# Verificar permisos
ls -la /opt/claudio-bot
# Debe ser propiedad de claudio:claudio

# Verificar entorno
sudo -u claudio cat /opt/claudio-bot/.env
```

---

## 8. PREGUNTAS FRECUENTES

### P1: ¿Puedo usar múltiples proveedores de IA?

**R:** Sí. Durante la instalación, selecciona "Multi-proveedor". Claudio usará Anthropic como primario y OpenAI como fallback si falla.

### P2: ¿Cuánto cuesta operar Claudio?

**R:** Depende del proveedor:
- **Anthropic Claude:** ~$0.50-5/mes para uso moderado
- **OpenAI GPT-4:** ~$1-10/mes para uso moderado
- **Ollama:** Gratis (requiere VPS con más RAM)

### P3: ¿Puedo restringir el acceso a mi bot?

**R:** Sí. Configura `ALLOWED_USERS` en .env con tus Telegram User IDs separados por coma, o usa `*` para acceso público.

### P4: ¿Claudio guarda mis datos?

**R:** Claudio no guarda datos de conversaciones. Cada solicitud se procesa independientemente. Los logs pueden contener metadatos.

### P5: ¿Puedo usar Claudio sin n8n?

**R:** Sí. Claudio funciona perfectamente sin n8n. Solo que no podrá crear/editar workflows en tu instancia, pero podrá ayudarte a diseñarlos.

### P6: ¿Cómo actualizo Claudio?

**R:**
```bash
cd /opt/claudio-bot
git pull
sudo -u claudio venv/bin/pip install -r requirements.txt
sudo systemctl restart claudio-server claudio-telegram-bot
```

### P7: ¿Qué comandos puedo usar en Telegram?

**R:** Claudio no tiene comandos específicos. Solo escribe en lenguaje natural:
- "Crea un workflow de webhook..."
- "Valida esta expresión..."
- "Busca nodos de Slack..."
- "Ayuda"

### P8: ¿Puedo ejecutar múltiples instancias de Claudio?

**R:** Sí. Solo asegúrate de:
1. Crear diferentes bots en @BotFather
2. Usar puertos diferentes en CLAUDIO_PORT
3. Usar nombres de servicio diferentes en systemd

### P9: ¿Cómo veo los logs en tiempo real?

**R:**
```bash
# Bot logs
sudo journalctl -u claudio-telegram-bot -f

# Server logs
sudo journalctl -u claudio-server -f

# Combinados
sudo journalctl -u claudio-* -f
```

### P10: ¿Claudio soporta otros idiomas?

**R:** Sí. Puedes escribir en español, inglés, portugués, etc. Claudio responderá en el mismo idioma.

---

## 📞 SOPORTE

- **GitHub Issues:** https://github.com/LeonardoPS1/bot_n8n/issues
- **Documentación:** https://github.com/LeonardoPS1/bot_n8n/wiki
- **Telegram:** (próximamente)

---

## 📄 LICENCIA

Este proyecto está licenciado bajo la MIT License - ver el archivo LICENSE para más detalles.

---

**¡Disfruta usando Claudio! 🚀**

---

## CHEAT SHEET RÁPIDO

### Comandos Básicos VPS

```bash
# Ver estado
sudo systemctl status claudio-*

# Reiniciar
sudo systemctl restart claudio-*

# Detener
sudo systemctl stop claudio-*

# Iniciar
sudo systemctl start claudio-*

# Ver logs
sudo journalctl -u claudio-telegram-bot -f

# Health check
curl http://localhost:8000/health
```

### Archivos Importantes

```bash
/opt/claudio-bot/.env              # Configuración
/opt/claudio-bot/bot_v2.py          # Bot
/opt/claudio-bot/claudio_complete.py # Server
/etc/systemd/system/claudio-*.service # Servicios
```

### Obtener Credenciales

| Credencial | Dónde Obtener |
|------------|---------------|
| Telegram Token | @BotFather |
| Anthropic Key | console.anthropic.com |
| OpenAI Key | platform.openai.com |
| n8n Key | Settings → API en n8n |
| Tu User ID | @userinfobot |

---

**Fin de la Guía de Instalación Completa**
