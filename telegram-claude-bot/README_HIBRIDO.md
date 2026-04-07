# 🤖 Bot Híbrido: Gemini + Claudio

Arquitectura híbrida que combina **Gemini** para chat general y **Claude** exclusivamente para expertise de n8n.

## 🎯 Por qué esta arquitectura?

| Servicio | Uso | Ventaja |
|----------|-----|---------|
| **Gemini** | Chat general, conversación | Más económico, rápido |
| **Claude** | n8n workflows, tareas técnicas | Mejor razonamiento técnico, más preciso |

## 💰 Comparación de Costos

| API | Input | Output | Uso típico |
|-----|-------|--------|------------|
| **Gemini 1.5 Flash** | ~$0.075/M tokens | ~$0.15/M tokens | Chat general (80% de mensajes) |
| **Claude Sonnet 4** | ~$3/M tokens | ~$15/M tokens | n8n expertise (20% de mensajes) |

**Ahorro estimado: 70-80%** comparado con usar Claude para todo

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Usuario        │
│  Telegram       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  bot_hibrido.py                 │
│  - Routing inteligente          │
│  - Historial separado           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────┐
│  ¿Es sobre n8n? │     │                  │
│                 │     │                  │
│  SÍ ────────────┼────▶│  CLAUUDIO        │
│                 │     │  (Claude API)    │
│  NO ────────────┼────▶│  para n8n        │
│                 │     └──────────────────┘
│  Gemini         │
│  responde       │
│  directamente   │
└─────────────────┘
```

## 📋 Ejemplos de Routing

| Mensaje | Servicio | Razón |
|---------|----------|-------|
| "hola" | Gemini | Saludo |
| "¿qué puedes hacer?" | Gemini | Pregunta general |
| "crear workflow n8n" | Claude | Tarea técnica n8n |
| "validar expresión" | Claude | Expertise n8n |
| "clima hoy" | Gemini | General |
| "conectar Slack n8n" | Claude | n8n específico |

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements_hibrido.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.hibrido.example .env
nano .env
```

Variables requeridas:
```bash
TELEGRAM_TOKEN=tu_token_bot_father
GEMINI_API_KEY=tu_gemini_key
ANTHROPIC_API_KEY=tu_claude_key  # Para Claudio Server
CLAUDIO_SERVER_URL=http://localhost:8000
```

### 3. Iniciar servicios

```bash
# Terminal 1: Claudio Server (usa Claude para n8n)
python claudio_complete.py

# Terminal 2: Bot Híbrido
python bot_hibrido.py
```

## 🔧 Configuración

### Gemini API Key
1. Ve a https://makersuite.google.com/app/apikey
2. Crea una nueva API key
3. Es GRATIS hasta cierto límite

### Anthropic API Key (para Claudio)
1. Ve a https://console.anthropic.com
2. Crea una API key
3. Solo se usa para n8n workflows

## 📱 Comandos del Bot

| Comando | Descripción |
|---------|-------------|
| `/start` | Mensaje de bienvenida |
| `/help` | Ayuda del bot híbrido |
| `/health` | Estado de Gemini + Claudio |
| `/clear` | Limpiar historial de ambos |

## 💡 Prompt System de Routing

El **system prompt de Gemini** determina si usar Claude:

```python
GEMINI_SYSTEM_PROMPT = """
Eres un asistente que ROUTEA mensajes:

🎯 REGLAS:
- Si es sobre n8n/workflows → USA CLAUDIO
- Si es chat general → RESPONDE DIRECTAMENTE

⚡ FORMATO:
- Para Claudio: **[CLAUUDIO]** mensaje
- Directo: resuelve normalmente
"""
```

## 📊 Métricas de Uso

```
Uso típico por usuario (100 mensajes):
├─ 80 mensajes chat general → Gemini (barato)
└─ 20 mensajes n8n técnico → Claude (caro pero necesario)

Costo estimado:
├─ Gemini: ~$0.01-0.02
└─ Claude: ~$0.05-0.10
└─ Total: ~$0.06-0.12 por 100 mensajes
```

## 🛠️ Troubleshooting

### Gemini no responde
```bash
# Verificar API key
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"ping"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=TU_KEY"
```

### Claudio desconectado
```bash
# Verificar Claudio Server
curl http://localhost:8000/health
```

### Routing incorrecto
Ajusta `GEMINI_SYSTEM_PROMPT` en `bot_hibrido.py`

## 📝 Archivos

- `bot_hibrido.py` - Bot principal con routing
- `claudio_complete.py` - Server con Claude para n8n
- `requirements_hibrido.txt` - Dependencias
- `.env.hibrido.example` - Template de configuración

## 🚢 Despliegue en VPS

```bash
# Actualizar deploy script para bot_hibrido
scp bot_hibrido.py ubuntu@tu-vps:/opt/claudio-bot/
ssh ubuntu@tu-vps 'sudo systemctl restart claudio-telegram-bot'
```

## 📖 Ventajas

1. **Costo reducido** - Gemini maneja el 80% de mensajes
2. **Mejor experiencia** - Gemini es más rápido para chat
3. **Calidad técnica** - Claude solo para n8n (donde brilla)
4. **Historial separado** - Cada API mantiene su contexto
5. **Fallback** - Si uno falla, el otro puede responder

## 🔗 Recursos

- **Gemini API**: https://ai.google.dev/gemini-api
- **Claude API**: https://docs.anthropic.com
- **n8n Docs**: https://docs.n8n.io

---

**Hecho con ❤️ para optimizar costos y calidad**
