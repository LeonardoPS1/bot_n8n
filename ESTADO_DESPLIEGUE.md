# Estado del Despliegue - Bot Híbrido Gemini + Claudio

 Fecha: 2026-04-07 19:50

## Resumen de Servicios

### Servicio 1: Bot Híbrido de Telegram
- **Archivo**: `bot_hibrido.py`
- **PID**: 1508053
- **Estado**: ✅ ACTIVO
- **Función**: Recibe mensajes de Telegram y enruta a Gemini/Claudio
- **Telegram Token**: 8612455621:AAGuhRawUuqFdzBvWN1hqAhPp7mlvMB09ZU

### Servicio 2: Claudio Server (n8n Expert)
- **Archivo**: `claudio_complete.py`
- **PID**: 1509130
- **Puerto**: 8000
- **Estado**: ✅ ACTIVO
- **Función**: Provee expertise de n8n workflows via API

## Conectividad

```
Telegram Bot API
     ↓
bot_hibrido.py (Puerto 443 polling)
     ↓
[Routing: Gemini para chat general / Claudio para n8n]
     ↓                    ↓
Gemini API          claudio_complete.py:8000
                         ↓
                    Anthropic API (Claude)
```

## Comandos de Gestión

### Ver logs del Bot Híbrido
```bash
ssh ubuntu@51.222.207.250 'tail -f /tmp/bot_hibrido.log'
```

### Ver logs de Claudio Server
```bash
ssh ubuntu@51.222.207.250 'tail -f /tmp/claudio.log'
```

### Ver estado de procesos
```bash
ssh ubuntu@51.222.207.250 'ps aux | grep -E "(bot_hibrido|claudio_complete)" | grep -v grep'
```

### Reiniciar Bot Híbrido
```bash
ssh ubuntu@51.222.207.250 'pkill -f bot_hibrido && cd /opt/claudio-bot && nohup sudo -u claudio venv/bin/python bot_hibrido.py > /tmp/bot_hibrido.log 2>&1 &'
```

### Reiniciar Claudio Server
```bash
ssh ubuntu@51.222.207.250 'pkill -f claudio_complete && cd /opt/claudio-bot && nohup sudo -u claudio venv/bin/python claudio_complete.py > /tmp/claudio.log 2>&1 &'
```

## Comandos Disponibles en Telegram

- `/start` - Mensaje de bienvenida
- `/help` - Ayuda del bot
- `/health` - Estado de servicios
- `/clear` - Limpiar historial

## URL del Bot

https://t.me/claudio_n8n_bot

## Problemas Detectados

### ⚠️ Saldo Insuficiente en Anthropic API
**Error**: "Your credit balance is too low to access the Anthropic API"

**Impacto**:
- El chat general (Gemini) funciona normalmente
- Las consultas de n8n fallarán con mensaje de error
- El bot seguirá respondiendo con Gemini

**Solución**:
1. Ir a https://console.anthropic.com/settings/plans
2. Agregar créditos o actualizar plan
3. Verificar que la API key tiene créditos disponibles

## Archivos en VPS

```
/opt/claudio-bot/
├── bot_hibrido.py          (9,368 bytes)
├── claudio_complete.py     (modificado con dotenv)
├── n8n_database.py         (27,374 bytes)
├── n8n_mcp_tools.py        (12,527 bytes)
├── venv/                   (entorno virtual)
└── .env                    (configuración con API keys)
```

## Variables de Entorno Configuradas

```
TELEGRAM_TOKEN=8612455621:AAGuhRawUuqFdzBvWN1hqAhPp7mlvMB09ZU
GEMINI_API_KEY=AIzaSyCQSTSW0qMIfFmMNQshy2qy-T97G0m0gDE
ANTHROPIC_API_KEY=sk-ant-api03-... (saldo insuficiente)
CLADIO_SERVER_URL=http://localhost:8000
REQUEST_TIMEOUT=60
```

## Logs Recientes (2026-04-07 19:50)

**Bot Híbrido**:
```
2026-04-07 19:50:28 - httpx - HTTP Request: POST https://api.telegram.org/bot.../getUpdates "HTTP/1.1 200 OK"
```

## Próximos Pasos

1. Agregar créditos a cuenta de Anthropic
2. Probar el bot con `/start` en Telegram
3. Probar consulta de n8n: "crear workflow n8n"
4. Probar chat general: "hola"

## Contacto VPS

- Host: 51.222.207.250
- Usuario: ubuntu
- Directorio: /opt/claudio-bot
