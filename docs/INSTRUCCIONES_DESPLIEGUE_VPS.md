# 🚀 INSTRUCCIONES DE DESPLIEGUE EN VPS

## Sistema Claudio Bot v4.4 - Con Auto-Fallback y Modelos Personalizados

---

## 📋 Resumen de Nuevas Características

### 1. **Sistema de Fallback Automático**
- Cambia automáticamente de modelo cuando se acaba la cuota
- Notificaciones por Telegram de los cambios
- Orden de fallback configurable

### 2. **Modelos Personalizados**
- Agrega cualquier API compatible con OpenAI o Anthropic
- Comando `/addmodel` desde Telegram
- Configuración vía variables de entorno

### 3. **Comandos de Administración**
- `/status` - Ver modelo actual
- `/models` - Listar modelos disponibles
- `/switch <provider>` - Cambiar de proveedor
- `/addmodel` - Agregar modelo personalizado
- `/test` - Probar modelo actual
- `/admin` - Ayuda de administración

---

## 🛠️ PASO 1: Conectar a tu VPS

```bash
# Conéctate a tu VPS (usuario ubuntu)
ssh ubuntu@51.222.207.250
# Usar sudo para comandos que requieren root
```

---

## 🛠️ PASO 2: Actualizar el Repositorio

```bash
# Ir al directorio
cd /opt/claudio-bot

# O clonar si no existe
# git clone https://github.com/LeonardoPS1/bot_n8n.git /opt/claudio-bot
# cd /opt/claudio-bot

# Actualizar desde GitHub
git pull origin master
```

---

## 🛠️ PASO 3: Actualizar Dependencias

```bash
# Activar entorno virtual
source venv/bin/activate

# Actualizar dependencias
pip install -q -r requirements.txt

# Salir del entorno virtual
deactivate
```

---

## 🛠️ PASO 4: Configurar Variables de Entorno

```bash
# Hacer backup del .env actual
cp .env .env.backup.$(date +%Y%m%d)

# Editar .env para agregar nuevas variables
nano .env
```

**Variables a agregar/configurar:**

```bash
# ============================================
# FALLBACK CONFIGURATION
# ============================================
# Enable automatic fallback (true/false)
AUTO_FALLBACK=true

# Order of providers for fallback
FALLBACK_ORDER=anthropic,openai,gemini,qwen,deepseek,ollama

# ============================================
# ADMIN CONFIGURATION
# ============================================
# Comma-separated list of admin user IDs
# Get your ID from @userinfobot on Telegram
ALLOWED_ADMIN_USERS=YOUR_TELEGRAM_USER_ID

# Optional: Custom model (if you have one)
# CUSTOM_MODEL_NAME=my-custom-model
# CUSTOM_MODEL_API_KEY=your_key
# CUSTOM_MODEL_BASE_URL=https://your-api.com/v1
# CUSTOM_MODEL_PROVIDER=openai

# ============================================
# BOT NOTIFICATION
# ============================================
# URL for bot notifications (usually not needed if on same machine)
# BOT_NOTIFICATION_URL=http://localhost:8000/api/notify
```

---

## 🛠️ PASO 5: Actualizar Servicios Systemd

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Reiniciar servicios
sudo systemctl restart claudio-server claudio-telegram-bot

# Verificar estado
sudo systemctl status claudio-server claudio-telegram-bot
```

---

## 🛠️ PASO 6: Verificar Funcionamiento

```bash
# Ver logs del bot
sudo journalctl -u claudio-telegram-bot -f

# En otra terminal, verificar servidor
sudo journalctl -u claudio-server -f

# Ver health check
curl http://localhost:8000/health

# Verificar modelos disponibles
curl http://localhost:8000/api/skills
```

---

## 📱 Prueba los Comandos de Admin

En Telegram, envía estos comandos a tu bot:

```
/status
```
Deberías ver:
```
📊 Model Status

Provider: Anthropic
Model: claude-sonnet-4-20250514
Auto-fallback: ✅ Enabled

*Available Providers:*
• Anthropic
• OpenAI
• ...
```

```
/models
```
Deberías ver la lista de todos los modelos configurados.

```
/admin
```
Muestra todos los comandos disponibles.

---

## ➕ Agregar un Modelo Personalizado (Opcional)

### Opción A: Vía Telegram

```
/addmodel mi-modelo-azure sk-... https://eastus.api.cognitive.microsoft.com/openai/deployments/gpt-35-turbo openai
```

### Opción B: Vía .env

```bash
nano /opt/claudio-bot/.env

# Agregar:
CUSTOM_MODEL_NAME=mi-modelo-azure
CUSTOM_MODEL_API_KEY=sk-...
CUSTOM_MODEL_BASE_URL=https://eastus.api.cognitive.microsoft.com/openai/deployments/gpt-35-turbo
CUSTOM_MODEL_PROVIDER=openai

# Y asegurar que:
AI_PROVIDER=multi

# Guardar y reiniciar
sudo systemctl restart claudio-server
```

---

## ⚙️ Configurar Fallback entre Modelos

Edita `.env`:

```bash
nano /opt/claudio-bot/.env

# Asegurar que esté en modo multi:
AI_PROVIDER=multi

# Configurar orden de fallback (personalizar según tus APIs):
FALLBACK_ORDER=openai,anthropic,gemini,qwen,deepseek,ollama

# Habilitar auto-fallback:
AUTO_FALLBACK=true

# Guardar y reiniciar
sudo systemctl restart claudio-server
```

---

## 🔧 Solución de Problemas

### Los servicios no inician

```bash
# Ver logs detallados
sudo journalctl -u claudio-server -n 50
sudo journalctl -u claudio-telegram-bot -n 50

# Verificar usuario claudio existe
id claudio

# Verificar permisos
ls -la /opt/claudio-bot
```

### Error de dependencias

```bash
cd /opt/claudio-bot
source venv/bin/activate
pip install -r requirements.txt
```

### El bot no responde

```bash
# Verificar bot está corriendo
sudo systemctl status claudio-telegram-bot

# Ver logs en tiempo real
sudo journalctl -u claudio-telegram-bot -f

# Verificar token de Telegram
cat .env | grep TELEGRAM_TOKEN
```

### Error de conexión con el servidor

```bash
# Verificar servidor está corriendo
sudo systemctl status claudio-server

# Probar health endpoint
curl http://localhost:8000/health

# Verificar puerto
netstat -tlnp | grep 8000
```

---

## 🎯 Comandos Rápidos de Referencia

```bash
# Ver estado de servicios
sudo systemctl status claudio-*

# Reiniciar servicios
sudo systemctl restart claudio-server claudio-telegram-bot

# Ver logs en tiempo real (bot)
sudo journalctl -u claudio-telegram-bot -f

# Ver logs en tiempo real (servidor)
sudo journalctl -u claudio-server -f

# Ver logs últimos 50 líneas
sudo journalctl -u claudio-telegram-bot -n 50

# Detener servicios
sudo systemctl stop claudio-server claudio-telegram-bot

# Iniciar servicios
sudo systemctl start claudio-server claudio-telegram-bot

# Verificar health
curl http://localhost:8000/health

# Editar configuración
sudo nano /opt/claudio-bot/.env
```

---

## ✅ Verificación Completa

Una vez desplegado, deberías poder:

1. ✅ Chatear con el bot normalmente
2. ✅ Usar `/status` para ver el modelo actual
3. ✅ Usar `/models` para ver modelos disponibles
4. ✅ Usar `/switch` para cambiar de proveedor (requiere reinicio)
5. ✅ Usar `/addmodel` para agregar modelos custom
6. ✅ Recibir notificaciones cuando un modelo falle
7. ✅ Ver cambio automático de modelo cuando se acaba la cuota

---

## 📞 Soporte

Si tienes problemas durante el despliegue:

1. Verifica los logs: `sudo journalctl -u claudio-telegram-bot -n 50`
2. Revisa la configuración: `cat /opt/claudio-bot/.env`
3. Verifica dependencias: `cd /opt/claudio-bot && source venv/bin/pip list`
4. Consulta la guía completa: `GUIA_INSTALACION_COMPLETA.md`

---

**¡Disfruta tu Claudio Bot con gestión completa de modelos! 🚀**
