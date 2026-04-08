# 🤖 Claudio - Expert n8n Workflow Assistant Bot v4.6.1

> **Tu asistente inteligente de Telegram para automatización de flujos n8n con múltiples proveedores de IA**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.6.1-brightgreen.svg)](https://github.com/LeonardoPS1/bot_n8n)

---

## 🎯 ¿Qué es Claudio?

**Claudio** es un bot de Telegram especializado en **n8n** que combina:

- **🧠 Multi-Proveedor IA**: Anthropic Claude, OpenAI GPT-4, Google Gemini, DeepSeek, Ollama (gratis)
- **🔄 Auto-Fallback**: Cambia automáticamente entre proveedores cuando uno falla
- **🔐 Gestión Segura**: Administra API keys mediante Telegram con enmascaramiento
- **📊 n8n Integrado**: Acceso a 1,396 nodos y 2,709+ templates de workflows
- **⚙️ Administración**: Cambia modelos dinámicamente sin reiniciar el servidor
- **🎯 Toll-Free**: Ollama local y gratis para uso sin límites

---

## 🌟 Características Principales

### 🧠 Proveedores IA Soportados

| Proveedor | Modelo | Costo | Estado |
|-----------|-------|-------|--------|
| **OpenAI** | gpt-4o-mini | ~$0.15/1M tokens | ✅ Rápido y económico |
| **Ollama** | phi3:mini | **GRATIS** | ✅ Local y eficiente |
| **DeepSeek** | deepseek-chat | Muy económico | ✅ Más barato |
| **Gemini** | gemini-2.5-pro | Gratis tier | ✅ Potente |
| **Anthropic** | claude-sonnet-4 | Premium | ✅ Más capaz |

### 🔄 Auto-Fallback Inteligente

```
Orden por defecto: openai → ollama → deepseek → gemini → anthropic
```

Cuando un proveedor falla:
1. **Detecta** automáticamente el error (quota, rate limit, conexión)
2. **Notifica** al usuario vía Telegram
3. **Cambia** al siguiente proveedor disponible
4. **Continúa** la conversación sin interrupción

### ⚙️ Comandos de Telegram

| Comando | Descripción | Admin |
|---------|-------------|-------|
| `/start` | Iniciar el bot | ❌ |
| `/status` | Ver estado y proveedor actual | ❌ |
| `/models` | Listar todos los modelos disponibles | ❌ |
| `/switch <proveedor>` | Cambiar de modelo dinámicamente | ✅ |
| `/addkey <proveedor>` | Agregar API key (seguro) | ✅ |
| `/listkeys` | Ver API keys configuradas (enmascaradas) | ✅ |
| `/test` | Probar conexión actual | ✅ |
| `/admin` | Panel de administración | ✅ |
| `/health` | Verificar salud del sistema | ❌ |

### 📊 Integración con n8n

Claudio tiene **acceso completo** a tu instancia de n8n:

- **Listar workflows**: Ve todos tus flujos de trabajo
- **Ver detalles**: Obtiene información de nodos y conexiones
- **Buscar nodos**: Encuentra los 1,396 nodos disponibles
- **Validar expresiones**: Verifica sintaxis de expresiones n8n
- **Generar código**: Crea código para Code nodes
- **Crear workflows**: Diseña flujos desde cero

---

## 🚀 Instalación Rápida (5 minutos)

### Opción 1: Instalador Automático

```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
python3 install_v2.py
```

El instalador te preguntará:
1. ✅ Token de Telegram
2. ✅ Tu User ID de Telegram
3. ✅ Selección de proveedor IA
4. ✅ API keys (si aplica)
5. ✅ Integración con n8n (opcional)

### Opción 2: Ollama GRATIS (Recomendado)

```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n

# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo
ollama pull phi3:mini

# Configurar
cp .env.example .env
nano .env  # Editar TELEGRAM_TOKEN y tu User ID

# Instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Iniciar
python3 claudio_complete.py  # Terminal 1
python3 bot_v2.py            # Terminal 2
```

---

## 📖 Guías de Instalación

| Guía | Descripción |
|------|-------------|
| **[GUIA_INSTALACION_COMPLETA.md](GUIA_INSTALACION_COMPLETA.md)** | Guía paso a paso detallada |
| **[QUICKSTART.md](QUICKSTART.md)** | Inicio rápido en 5 minutos |
| **[INSTRUCCIONES_DESPLIEGUE_VPS.md](INSTRUCCIONES_DESPLIEGUE_VPS.md)** | Despliegue en VPS |

---

## 🔑 Credenciales Necesarias

### Para el Bot

| Credencial | Dónde obtener |
|-----------|---------------|
| **Telegram Bot Token** | [@BotFather](https://t.me/BotFather) → `/newbot` |
| **Tu User ID** | [@userinfobot](https://t.me/userinfobot) → `/start` |

### Para Proveedores IA

| Proveedor | Dónde obtener | Costo |
|-----------|---------------|-------|
| **OpenAI** | [platform.openai.com](https://platform.openai.com) | ~$0.15/1M tokens |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | $$ |
| **Gemini** | [ai.google.dev](https://ai.google.dev/) | Gratis tier |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com/) | Muy barato |
| **Ollama** | [ollama.ai](https://ollama.ai/) | **GRATIS** (local) |

### Para n8n (Opcional)

| Credencial | Dónde obtener |
|-----------|---------------|
| **API Key** | Tu instancia n8n → Settings → API |
| **URL** | Tu instancia n8n (ej: `https://n8n.tudominio.com`) |

---

## ⚙️ Configuración Mínima

```bash
# ============================================
# TELEGRAM
# ============================================
TELEGRAM_TOKEN=tu_token_aqui
ALLOWED_USERS=tu_user_id
ALLOWED_ADMIN_USERS=tu_user_id

# ============================================
# PROVEEDOR IA
# ============================================
AI_PROVIDER=multi                # Multi-proveedor con auto-fallback
FALLBACK_ORDER=openai,ollama,deepseek,gemini,anthric

# OpenAI (ejemplo rápido)
OPENAI_API_KEY=sk-proj-tu-key-aqui
OPENAI_MODEL=gpt-4o-mini

# Ollama (ejemplo gratis)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# ============================================
# N8N (OPCIONAL)
# ============================================
N8N_INSTANCE_URL=https://n8n.tudominio.com
N8N_API_KEY=tu_api_key_aqui
```

---

## 🚀 Modos de Despliegue

### Local (Desarrollo)

```bash
# Terminal 1
python3 claudio_complete.py

# Terminal 2
python3 bot_v2.py
```

### VPS (Producción)

```bash
# Usar el script automático
python3 deploy_vps.py

# O manualmente
ssh user@vps
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
python3 install_v2.py
```

### Docker

```bash
docker-compose up -d
```

---

## 🛠️ Solución de Problemas

### Bot no responde

```bash
# Verificar estado
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot

# Ver logs
sudo journalctl -u claudio-server -n 50
sudo journalctl -u claudio-telegram-bot -n 50
```

### Error de timeout

```bash
# Aumentar timeout en .env
REQUEST_TIMEOUT=120

# Cambiar a proveedor más rápido
/switch openai
```

### Error de conexión n8n

```bash
# Verificar API key
grep N8N_API_KEY .env

# Probar conexión
curl -H "X-N8N-API-KEY: tu_key" https://n8n.tu-url.com/api/v1/workflows
```

### Ollama no funciona

```bash
# Verificar que Ollama esté corriendo
sudo systemctl status ollama

# Descargar modelo
ollama pull phi3:mini
```

---

## 📁 Estructura del Proyecto

```
telegram-claude-bot/
├── bot_v2.py                    # Bot de Telegram
├── claudio_complete.py          # Servidor API FastAPI
├── n8n_mcp_tools.py            # Cliente n8n
├── n8n_database.py             # Base de datos de nodos
├── install_v2.py                # Instalador interactivo
├── deploy_vps.py                # Script de despliegue VPS
├── requirements.txt            # Dependencias Python
├── .env.example                # Plantilla de configuración
├── utils/                     # Utilidades compartidas
│   ├── __init__.py
│   ├── api_keys.py            # Validación de API keys
│   ├── permissions.py          # Verificación de permisos
│   ├── http_client.py         # Cliente HTTP persistente
│   └── env_manager.py          # Manejo de .env
├── skills/                    # Módulos de especialización
│   ├── n8n_expression_syntax.py
│   └── n8n_other_skills.py
├── GUIA_INSTALACION_COMPLETA.md  # Guía de instalación
├── QUICKSTART.md                # Inicio rápido
├── README.md                   # Este archivo
└── .git/                       # Repositorio Git
```

---

## 🎯 Casos de Uso

### Crear un Workflow con Webhook

```
Tú: Crea un workflow que reciba webhook y envíe a Slack

Claudio: Voy a crear un workflow webhook-to-Slack:

1. **Webhook Trigger** - Recibe POST requests
   - Path: slack-webhook
   - Método: POST
   - Response Mode: lastNode

2. **Set Node** - Extrae el mensaje
   - Expresión: {{$json.body.message}}

3. **Slack Node** - Envía mensaje
   - Canal: #general
   - Texto: {{$json.message}}

¿Quieres que cree este workflow?
```

### Validar Expresión n8n

```
Tú: Valida esta expresión: {{$json.data.items[0].name}}

Claudio: ✅ La expresión es válida

Análisis:
- $json accede al datos del ítem actual
- data.items[0] accede al primer elemento
- .name obtiene el campo 'name'
```

### Buscar Nodo Específico

```
Tú: Busca el nodo de Gmail en n8n

Claudio: Aquí está la información del nodo Gmail:

**n8n-nodes-base.gmail**
- Descripción: Envía mensajes a Slack
- Operaciones: message, post, file
- Requiere: canal ID o thread ID para archivos
```

---

## 🔄 Actualizaciones Recientes

### v4.6.1 (Actual)

- ✅ Multi-proveedor IA con 5 opciones
- ✅ Auto-fallback inteligente
- ✅ Gestión segura de API keys vía Telegram
- ✅ Cambio dinámico de modelos
- ✅ Optimización de código (utils compartidas)
- ✅ Ollama integrado (gratis y local)
- ✅ Documentación completa en español

### Próximamente

- [ ] Interfaz web de administración
- [ ] Soporte para más modelos IA
- [ ] Exportación de workflows a código
- [ ] Modo de voz en Telegram

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/AmazingFeature`
3. Commit tus cambios: `git commit -m 'Add some AmazingFeature'`
4. Push a la rama: `git push origin feature/AmazingFeature`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

---

## 🙋 Soporte

- 📧 **Issues**: [GitHub Issues](https://github.com/LeonardoPS1/bot_n8n/issues)
- 📖 **Wiki**: [Wiki del Proyecto](https://github.com/LeonardoPS1/bot_n8n/wiki)
- 📚 **Documentación**: [GUIA_INSTALACION_COMPLETA.md](GUIA_INSTALACION_COMPLETA.md)

---

## ⭐ Star si te ayuda!

Si este bot te ha sido útil, por favor considera:
- Dar una ⭐ en GitHub
- Compartir con otros usuarios de n8n
- Reportar bugs o sugerir mejoras

**Hecho con ❤️ por la comunidad de n8n**
