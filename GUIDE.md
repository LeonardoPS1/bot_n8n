# 📖 Claudio - Guía de Usuario Completa

## Table of Contents

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Comandos Disponibles](#comandos-disponibles)
4. [Creación de Workflows](#creación-de-workflows)
5. [Gestión de Workflows](#gestión-de-workflows)
6. [Sintaxis de Expresiones n8n](#sintaxis-de-expresiones-n8n)
7. [Proveedores de IA](#proveedores-de-ia)
8. [Solución de Problemas](#solución-de-problemas)
9. [Ejemplos Prácticos](#ejemplos-prácticos)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

**Claudio** es tu asistente experto en n8n que funciona a través de Telegram. Puedes crear, gestionar y automatizar workflows simplemente describiendo lo que necesitas en lenguaje natural.

### ¿Qué puedes hacer con Claudio?

- ✅ Crear workflows completos con descripciones simples
- ✅ Listar y ver todos tus workflows
- ✅ Eliminar workflows individuales o todos a la vez
- ✅ Activar/desactivar workflows
- ✅ Obtener consejos expertos sobre n8n
- ✅ Cambiar entre diferentes proveedores de IA
- ✅ Aprender sobre sintaxis de expresiones n8n

---

## Primeros Pasos

### 1. Obtén tu Token de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando `/newbot`
3. Sigue las instrucciones para crear tu bot
4. Copia el token que te proporciona

### 2. Obtén tu ID de Usuario de Telegram

1. Abre Telegram y busca **@userinfobot**
2. Envía cualquier mensaje
3. Copia tu ID de usuario (número)

### 3. Configura las Variables de Entorno

Crea un archivo `.env` en el directorio del proyecto:

```bash
# Telegram
TELEGRAM_TOKEN=tu_token_aqui
ALLOWED_USERS=tu_id_aqui

# AI Provider (mínimo)
OPENAI_API_KEY=tu_api_key_aqui
AI_PROVIDER=openai

# n8n (opcional pero recomendado)
N8N_API_KEY=tu_api_key_n8n
N8N_INSTANCE_URL=https://tu-n8n.com
```

### 4. Inicia el Bot

```bash
# Local
python start.py

# VPS
sudo systemctl start claudio-telegram-bot
```

### 5. Prueba tu Bot

En Telegram, envía a tu bot:
```
/start
```

Deberías recibir un mensaje de bienvenida.

---

## Comandos Disponibles

### Comandos Básicos

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/start` | Muestra mensaje de bienvenida | `/start` |
| `/help` | Muestra ayuda detallada | `/help` |
| `/health` | Verifica estado del servidor | `/health` |
| `/clear` | Limpia historial de conversación | `/clear` |

### Comandos de Administración

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `/admin` | Muestra todos los comandos de admin | `/admin` |
| `/status` | Estado actual del modelo de IA | `/status` |
| `/models` | Lista todos los modelos disponibles | `/models` |
| `/switch <provider>` | Cambia proveedor de IA | `/switch openai` |
| `/listkeys` | Lista API keys configuradas (enmascaradas) | `/listkeys` |

### Comandos de Workflows (Lenguaje Natural)

| Acción | Comandos Posibles |
|--------|------------------|
| **Crear workflow** | "crea un workflow con X y Y", "necesito un flujo con X, Y y Z" |
| **Listar workflows** | "lista mis workflows", "que workflows tengo", "ver workflows" |
| **Eliminar todos** | "elimina todos los workflows", "borra todo" |
| **Eliminar uno** | "elimina el workflow ABC123", "borra el flujo XYZ" |
| **Activar** | "activa el workflow ABC123" |
| **Desactivar** | "desactiva el workflow ABC123" |

---

## Creación de Workflows

### Sintaxis Básica

Para crear un workflow, simplemente describe los nodos que necesitas:

```
crea un workflow con [nodo1] y [nodo2]
```

### Ejemplos de Creación

#### Webhook a Slack

```
crea un workflow con webhook y slack
```

**Resultado:**
- ✅ Workflow creado en n8n
- 🔗 Webhook configurado
- 📨 Notificación a Slack lista

#### Procesamiento de Datos

```
necesito un flujo con webhook, set, y http request
```

**Resultado:**
- ✅ Workflow de 3 nodos
- 📥 Webhook para recibir datos
- ⚙️ Set para transformar datos
- 🌐 HTTP Request para enviar a API

#### Integración con IA

```
crea un workflow con webhook, openai y telegram
```

**Resultado:**
- ✅ Workflow con IA integrada
- 📥 Webhook → OpenAI → Telegram
- 🤖 Procesamiento inteligente de mensajes

#### Base de Datos

```
crea un workflow con schedule trigger, postgres y email
```

**Resultado:**
- ✅ Workflow programado
- ⏰ Trigger horario configurado
- 💾 Consulta a PostgreSQL
- 📧 Envío de resultados por email

### Nodos Disponibles

#### Triggers (Disparadores)
- `webhook` - Recibe HTTP requests
- `manual trigger` - Ejecución manual
- `schedule trigger` - Ejecución programada

#### Core (Núcleo)
- `set` - Establece valores
- `if` - Condicionales
- `switch` - Múltiples rutas
- `merge` - Combina datos
- `code` - Código JavaScript
- `http request` - Llamadas HTTP

#### Communication (Comunicación)
- `slack` - Mensajes a Slack
- `telegram` - Mensajes a Telegram
- `send email` - Envío de emails

#### Database (Base de Datos)
- `postgres` - PostgreSQL
- `mysql` - MySQL
- `mongodb` - MongoDB
- `airtable` - Airtable

#### AI (Inteligencia Artificial)
- `openai` - GPT-4, GPT-3.5
- `anthropic` - Claude
- `ai agent` - Agente con herramientas

#### File (Archivos)
- `google sheets` - Hojas de cálculo
- `google drive` - Archivos Drive
- `aws s3` - Almacenamiento S3

---

## Gestión de Workflows

### Listar Workflows

```
lista mis workflows
```

**Respuesta de ejemplo:**
```
📋 Tus Workflows (3):

• Webhook a Gmail (abc123) - ⏸️ Inactivo
• AI Support Bot (def456) - ✅ Activo
• Daily Report (ghi789) - ⏸️ Inactivo
```

### Eliminar Workflows

#### Eliminar Todos

```
elimina todos los workflows
```

**Respuesta:**
```
✅ Todos los workflows eliminados
🗑️ Workflows eliminados: 3
```

#### Eliminar Uno Específico

```
elimina el workflow abc123
```

**Respuesta:**
```
✅ Workflow abc123 eliminado
```

### Activar/Desactivar Workflows

```
activa el workflow abc123
desactiva el workflow abc123
```

---

## Sintaxis de Expresiones n8n

### Variables Principales

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `$json` | Datos del item actual | `{{ $json.name }}` |
| `$json.body` | Cuerpo del webhook | `{{ $json.body.email }}` |
| `$node["Name"]` | Salida de nodo específico | `{{ $node["Webhook"].json.body }}` |
| `$now` | Timestamp actual | `{{ $now }}` |
| `$env` | Variables de entorno | `{{ $env.API_KEY }}` |

### ⚠️ Regla Crítica: Webhooks

**ERRÓNEO:**
```javascript
{{ $json.email }}  // ❌ NO funciona con webhooks
```

**CORRECTO:**
```javascript
{{ $json.body.email }}  // ✅ SIEMPRE usa .body
```

### Acceso a Datos Anidados

```javascript
// Objeto anidado
{{ $json.body.data.user.email }}

// Array
{{ $json.body.items[0].name }}

// Nodo específico
{{ $node["HTTP Request"].json.result.data }}
```

### Expresiones en Nodos Code

```javascript
// En nodo Code, NO usas {{ }}
const email = $input.item.json.body.email;
return [{json: {processed: email}}];
```

---

## Proveedores de IA

### OpenAI

**Modelos disponibles:**
- GPT-4o (recomendado)
- GPT-4
- GPT-3.5 Turbo

**Configuración:**
```bash
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o
```

**Usar:**
```
/switch openai
```

### Anthropic Claude

**Modelos disponibles:**
- Claude 3.5 Sonnet (recomendado)
- Claude 3 Opus
- Claude 3 Haiku

**Configuración:**
```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

**Usar:**
```
/switch anthropic
```

### Ollama (Local)

**Modelos disponibles:**
- phi3:mini (recomendado, rápido)
- llama2
- mistral
- codellama

**Configuración:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

**Usar:**
```
/switch ollama
```

### Multi-Proveedor con Fallback

**Configuración:**
```bash
AI_PROVIDER=multi
AUTO_FALLBACK=true
FALLBACK_ORDER=openai,ollama
```

**Comportamiento:**
- Intenta OpenAI primero
- Si falla, cambia a Ollama automáticamente
- Sin interrupciones en el servicio

---

## Solución de Problemas

### Bot No Responde

**Síntoma:** Envías un mensaje y no hay respuesta.

**Soluciones:**
1. Verifica que el servicio está corriendo:
```bash
sudo systemctl status claudio-telegram-bot
```

2. Revisa los logs:
```bash
sudo journalctl -u claudio-telegram-bot -n 50
```

3. Verifica tu API key de Telegram:
```bash
# En .env
TELEGRAM_TOKEN=correcto_aqui
```

4. Confirma que tu ID está en ALLOWED_USERS

### Workflow No Se Crea

**Síntoma:** El bot dice que creó el workflow pero no aparece en n8n.

**Soluciones:**
1. Verifica API key de n8n:
```bash
# Test
curl -H "X-N8N-API-KEY: tu_key" https://tu-n8n.com/api/v1/workflows
```

2. Confirma URL de n8n:
```bash
N8N_INSTANCE_URL=https://correcto.com
```

3. Verifica permisos en n8n

### Error de API Key de IA

**Síntoma:** "Error: API key invalid"

**Soluciones:**
1. Verifica la API key:
```
/listkeys
```

2. Añade una nueva key:
```
/addkey openai
[Pegar nueva key]
```

3. Prueba otro proveedor:
```
/switch ollama
```

### Servidor Caído

**Síntoma:** `/health` retorna error

**Soluciones:**
1. Reinicia el servidor:
```bash
sudo systemctl restart claudio-server
```

2. Verifica logs del servidor:
```bash
sudo journalctl -u claudio-server -n 50
```

3. Verifica puerto disponible:
```bash
netstat -tlnp | grep 8001
```

---

## Ejemplos Prácticos

### Ejemplo 1: Webhook a Discord

**Necesito:** Un endpoint que reciba datos y los envíe a Discord

**Mensaje a Claudio:**
```
crea un workflow con webhook y http request para discord
```

**Configuración adicional requerida:**
1. Configurar credenciales de Discord
2. Ajustar URL del webhook de Discord
3. Formatear el mensaje

### Ejemplo 2: Backup Automático de Base de Datos

**Necesito:** Backup diario de PostgreSQL a Google Sheets

**Mensaje a Claudio:**
```
crea un workflow con schedule trigger, postgres y google sheets
```

**Configuración adicional:**
1. Configurar credenciales PostgreSQL
2. Configurar acceso a Google Sheets
3. Ajustar query SQL
4. Configurar frecuencia (diario)

### Ejemplo 3: Bot de Soporte con IA

**Necesito:** Un bot que responda preguntas usando IA

**Mensaje a Claudio:**
```
crea un workflow con webhook, openai y respond to webhook
```

**Configuración adicional:**
1. Configurar API key de OpenAI
2. Ajustar prompt del sistema
3. Formatear respuesta

### Ejemplo 4: Sincronización Airtable a Slack

**Necesito:** Cuando se añade registro en Airtable, notificar en Slack

**Mensaje a Claudio:**
```
crea un workflow con airtable trigger y slack
```

**Configuración adicional:**
1. Configurar credenciales Airtable
2. Seleccionar tabla y vista
3. Configurar canal de Slack
4. Formatear mensaje

---

## Preguntas Frecuentes

### ¿Puedo crear workflows con múltiples nodos?

Sí, simplemente enuméralos:
```
crea un workflow con webhook, set, if, merge y email
```

### ¿Puedo editar un workflow existente?

Actualmente, Claudio crea nuevos workflows. Para editar, abre el workflow en n8n y haz cambios manuales.

### ¿Cómo funciona el cambio entre proveedores de IA?

Usa el comando `/switch <provider>` para cambiar instantáneamente sin reiniciar.

### ¿Puedo restringir quién usa el bot?

Sí, añade los IDs de usuario permitidos en `ALLOWED_USERS`:
```bash
ALLOWED_USERS=123456789,987654321
```

### ¿Qué pasa si un workflow falla al crearse?

Claudio te informará del error específico. Problemas comunes:
- API key inválida
- n8n no accesible
- Permisos insuficientes

### ¿Puedo usar Claudio sin n8n?

Sí, puedes hacer preguntas sobre n8n, sintaxis, y mejores prácticas. Solo las funciones de creación/gestión requieren n8n.

### ¿Cómo obtengo soporte?

- 📖 Lee esta guía
- 🐛 Reporta issues en GitHub
- 💬 Únete al grupo de Telegram

---

## Tips Avanzados

### 1. Nombres de Workflows Descriptivos

Claudio asigna nombres automáticos, pero puedes editarlos en n8n:
```
"Webhook to Slack" → "Customer Support Notifications"
```

### 2. Validación Antes de Crear

Antes de crear múltiples workflows, valida:
- API keys correctas
- Permisos en n8n
- Credenciales configuradas

### 3. Organización por Carpetas

Crea workflows relacionados y organízalos en carpetas en n8n.

### 4. Testing de Workflows

1. Crea workflow de prueba
2. Valída que funcione
3. Crea workflows similares basados en el plantilla

### 5. Monitoreo

Usa `/health` regularmente para verificar estado del sistema.

---

## Glosario

| Término | Definición |
|---------|------------|
| **Workflow** | Secuencia de automatización en n8n |
| **Node** | Cada bloque individual en un workflow |
| **Trigger** | Nodo que inicia un workflow |
| **Expression** | Sintaxis para acceder a datos en n8n |
| **Webhook** | Endpoint HTTP que recibe datos |
| **Provider** | Servicio de IA (OpenAI, Anthropic, etc.) |

---

## Recursos Adicionales

- [Documentación oficial de n8n](https://docs.n8n.io)
- [n8n Community](https://community.n8n.io)
- [Expresiones n8n](https://docs.n8n.io/expressions)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)

---

**¿Necesitas más ayuda?**

Contacta al equipo de soporte o consulta nuestra comunidad en Telegram.

¡Feliz automatización! 🚀
