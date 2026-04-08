# 🤖 Claudio - Expert n8n Workflow Assistant Bot

> **Tu asistente inteligente de Telegram para automatización de flujos n8n con múltiples proveedores de IA**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.6.1-brightgreen.svg)](https://github.com/LeonardoPS1/bot_n8n)

---

## 🌟 Características Principales

### 🧠 Multi-Proveedor IA
- **Anthropic Claude** (claude-sonnet-4, claude-3.5-sonnet)
- **OpenAI GPT-4** (gpt-4o-mini, gpt-4o, gpt-4-turbo)
- **Google Gemini** (gemini-2.5-pro, gemini-2.5-flash, gemini-3.1-preview)
- **Alibaba Qwen** (qwen-plus, qwen-turbo)
- **DeepSeek** (deepseek-chat, muy económico)
- **Ollama** (local y GRATIS - phi3, llama3, mistral)
- **Modelos Personalizados** (cualquier API compatible con OpenAI/Anthropic)

### 🔄 Auto-Fallback Inteligente
Cambia automáticamente entre proveedores cuando uno falla o se queda sin tokens

### ⚙️ Administración por Telegram
- Cambiar modelos dinámicamente
- Agregar API keys de forma segura
- Verificar estado del sistema
- Probar conexiones

### 📊 Integración Completa con n8n
- Acceso a **1,396 nodos** (812 core + 584 community)
- **2,709+ templates** de workflows
- Crear, modificar y validar workflows
- Generar código para Code nodes
- Validar expresiones de n8n

### 🔒 Seguridad
- Gestión de API keys con enmascaramiento
- Restricción de usuarios por ID
- Modo administrador con permisos

---

## 📸 Inicio Rápido (3 minutos)

```bash
# Clonar el repositorio
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n

# Ejecutar el instalador interactivo
python3 install.py
```

El instalador te guiará paso a paso en:
1. ✅ Selección de proveedor IA
2. ✅ Configuración de Telegram
3. ✅ Integración con n8n (opcional)
4. ✅ Modo de despliegue (Local/VPS/Docker)
5. ✅ Configuración de seguridad
6. ✅ Verificación post-instalación

---

## 📖 Documentación Completa

### 📄 Guías Disponibles

| Guía | Descripción |
|------|-------------|
| **[GUIA_INSTALACION_COMPLETA.md](GUIA_INSTALACION_COMPLETA.md)** | Guía paso a paso detallada |
| **[INSTRUCCIONES_DESPLIEGUE_VPS.md](INSTRUCCIONES_DESPLIEGUE_VPS.md)** | Despliegue en VPS |
| **[.env.example](.env.example)** | Variables de entorno |

---

## 🚀 Modos de Despliegue

### 1️⃣ Modo Local (Desarrollo)
```bash
python3 install.py
# Selecciona "Local" cuando pregunte
python3 bot_v2.py    # Terminal 1: Bot de Telegram
python3 claudio_complete.py    # Terminal 2: Servidor API
```

### 2️⃣ Modo VPS (Producción)
```bash
# Usar el script de despliegue automático
python deploy_vps.py
# O seguir la guía de VPS
```

### 3️⃣ Modo Docker
```bash
docker-compose up -d
```

---

## 🎯 Comandos de Telegram

### Comandos Básicos
| Comando | Descripción |
|---------|-------------|
| `/start` | Iniciar el bot |
| `/help` | Mostrar ayuda |
| `/status` | Ver estado y proveedor actual |
| `/health` | Verificar salud del sistema |

### Comandos de Administración
| Comando | Descripción |
|---------|-------------|
| `/models` | Listar modelos disponibles |
| `/switch <proveedor>` | Cambiar de modelo |
| `/addkey <proveedor>` | Agregar API key (seguro) |
| `/addmodel <custom>` | Agregar modelo personalizado |
| `/test` | Probar conexión |
| `/admin` | Panel de administración |

---

## 🔑 Credenciales Necesarias

### Para Telegram Bot
- **Telegram Bot Token**: Obtener de [@BotFather](https://t.me/BotFather)
- **Tu User ID**: Obtener de [@userinfobot](https://t.me/userinfobot)

### Para Proveedores IA
| Proveedor | Dónde obtener | Costo |
|-----------|---------------|-------|
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com) | $$ |
| **OpenAI** | [platform.openai.com](https://platform.openai.com) | $$ |
| **Gemini** | [ai.google.dev](https://ai.google.dev/) | Gratis tier |
| **Qwen** | [dashscope.aliyun.com](https://dashscope.aliyun.com/) | $ |
| **DeepSeek** | [platform.deepseek.com](https://platform.deepseek.com/) | $ |
| **Ollama** | [ollama.ai](https://ollama.ai/) | **GRATIS** |

### Para n8n (Opcional)
- **API Key**: Configuración → API en tu instancia n8n
- **URL**: Tu instancia de n8n (ej: https://n8n.tudominio.com)

---

## 📊 Estructura del Proyecto

```
telegram-claude-bot/
├── bot_v2.py                    # Bot de Telegram
├── claudio_complete.py          # Servidor API FastAPI
├── n8n_mcp_tools.py            # Herramientas n8n
├── n8n_database.py             # Base de datos de nodos
├── install.py                  # Instalador interactivo
├── requirements.txt            # Dependencias Python
├── .env.example                # Plantilla de configuración
├── skills/                     # Módulos de especialización
│   ├── n8n_expression_syntax.py
│   └── n8n_other_skills.py
└── README.md                   # Este archivo
```

---

## ⚙️ Configuración

### Archivo .env

```bash
# ============================================
# TELEGRAM
# ============================================
TELEGRAM_TOKEN=tu_token_aqui
ALLOWED_USERS=tu_user_id_aqui
ALLOWED_ADMIN_USERS=tu_user_id_aqui

# ============================================
# PROVEEDOR IA
# ============================================
AI_PROVIDER=multi                # multi, anthropic, openai, gemini, qwen, deepseek, ollama
AUTO_FALLBACK=true
FALLBACK_ORDER=openai,ollama,deepseek,gemini,anthropic

# OpenAI (ejemplo)
OPENAI_API_KEY=sk-proj-tu-key-aqui
OPENAI_MODEL=gpt-4o-mini

# Ollama (ejemplo local y gratis)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# ============================================
# N8N (OPCIONAL)
# ============================================
N8N_INSTANCE_URL=https://n8n.tudominio.com
N8N_API_KEY=tu_api_key_aqui
```

---

## 🔄 Auto-Fallback

El sistema cambia automáticamente entre proveedores en este orden:

```
1. openai (gpt-4o-mini - rápido y económico)
2. ollama (phi3:mini - gratis y local)
3. deepseek (deepseek-chat - muy económico)
4. gemini (gemini-2.5-pro - potente)
5. anthropic (claude-sonnet-4 - más capaz)
```

Cuando un proveedor falla o se queda sin tokens, el sistema:
1. Notifica el cambio
2. Cambia al siguiente proveedor
3. Continúa la conversación sin interrupción

---

## 🛠️ Solución de Problemas

### Bot no responde
```bash
# Verificar estado de servicios
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot

# Ver logs
sudo journalctl -u claudio-server -n 50
sudo journalctl -u claudio-telegram-bot -n 50
```

### Error de timeout
- Aumentar `REQUEST_TIMEOUT=120` en `.env`
- Cambiar a proveedor más rápido (OpenAI o Ollama)

### Error de conexión n8n
- Verificar `N8N_INSTANCE_URL` y `N8N_API_KEY`
- Probar acceso: `curl -H "X-N8N-API-KEY: tu_key" tu_n8n_url/api/v1/workflows`

### Ollama no funciona
```bash
# Verificar Ollama está corriendo
sudo systemctl status ollama

# Descargar modelo
ollama pull phi3:mini
```

---

## 📈 Requisitos del Sistema

### Mínimos
- Python 3.9+
- 2GB RAM
- 10GB disco

### Recomendados (VPS)
- Python 3.13+
- 4GB RAM
- 20GB disco
- Ubuntu 22.04+

### Para Ollama
- CPU: 4+ cores recomendado
- RAM: 8GB+ para modelos grandes
- GPU: Opcional, para modelos más grandes

---

## 🤝 Contribuir

Contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para detalles.

---

## 🙋 Soporte

- 📧 Issues: [GitHub Issues](https://github.com/LeonardoPS1/bot_n8n/issues)
- 📖 Documentación: [Wiki del Proyecto](https://github.com/LeonardoPS1/bot_n8n/wiki)
- 💬 Discord: [Servidor de Comunidad](https://discord.gg/claudio-bot)

---

## 🌟 Características Proximas

- [ ] Interfaz web de administración
- [ ] Soporte para más modelos IA
- [ ] Exportación de workflows a código
- [ ] Integración con más plataformas
- [ ] Modo de voz en Telegram

---

**Hecho con ❤️ por la comunidad de n8n**
