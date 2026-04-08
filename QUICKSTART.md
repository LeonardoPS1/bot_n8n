# 🚀 Inicio Rápido - Claudio Bot

> **Configura tu bot en 5 minutos**

---

## Opción 1: Instalación Automática ⭐

```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
python3 install.py
```

Responde las preguntas y listo.

---

## Opción 2: Configuración Rápida Manual

### 1. Instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar `.env`
```bash
cp .env.example .env
nano .env
```

Mínimo necesario:
```bash
TELEGRAM_TOKEN=tu_token_de_botfather
ALLOWED_USERS=tu_user_id
AI_PROVIDER=openai
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4o-mini
```

### 3. Iniciar
```bash
# Terminal 1
python3 claudio_complete.py

# Terminal 2
python3 bot_v2.py
```

### 4. Usar en Telegram
```
/start
/hola
/cuantos workflows tengo?
```

---

## Opción 3: Ollama GRATIS

```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelo
ollama pull phi3:mini

# Configurar .env
TELEGRAM_TOKEN=tu_token
ALLOWED_USERS=tu_id
AI_PROVIDER=ollama
OLLAMA_MODEL=phi3:mini
```

---

## 🔑 Obtener Credenciales

| Credencial | Dónde obtener |
|------------|---------------|
| Telegram Token | [@BotFather](https://t.me/BotFather) → `/newbot` |
| Tu User ID | [@userinfobot](https://t.me/userinfobot) → `/start` |
| OpenAI Key | [platform.openai.com](https://platform.openai.com) |
| Anthropic Key | [console.anthropic.com](https://console.anthropic.com) |
| Gemini Key | [ai.google.dev](https://ai.google.dev/) |

---

## ❓ Problemas Comunes

**Bot no responde:**
```bash
# Verificar token
grep TELEGRAM_TOKEN .env

# Reiniciar
python3 bot_v2.py
```

**Error de API:**
```bash
# Verificar API key
grep OPENAI_API_KEY .env

# Cambiar proveedor
/switch ollama
```

---

## 📖 Más Información

- [Guía Completa](GUIA_INSTALACION_ACTUALIZADA.md)
- [README Principal](README.md)
- [Despliegue VPS](INSTRUCCIONES_DESPLIEGUE_VPS.md)

---

**¡Listo en 5 minutos!** 🎉
