# 🛠️ Solución de Timeout - Claudio Bot

## Problema Identificado

El bot tenía problemas para:
1. **Eliminar workflows** - Faltaba la función `delete_workflow()` en el servidor
2. **Timeout en operaciones largas** - El timeout era de solo 60 segundos
3. **Operaciones masivas** - No podía procesar múltiples workflows a la vez

## Cambios Realizados (v4.6.2)

### 1. Agregada función `delete_workflow()`
```python
async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
    """Delete workflow from n8n"""
    # Implementación completa en claudio_complete.py
```

### 2. Detección de comandos de eliminación
```python
if any(word in message_lower for word in ["eliminar", "borrar", "delete"]):
    # Detecta "eliminar todos los workflows" y los elimina uno por uno
```

### 3. Aumentado timeout de 60s → 180s (3 minutos)
- `REQUEST_TIMEOUT = 180` en bot_v2.py
- `uvicorn timeout_keep_alive=300` en claudio_complete.py

## Cómo Actualizar el VPS

### Opción 1: Script Automático (Recomendado)

```bash
# En Windows, ejecutar:
actualizar_vps.bat

# O en Linux/Mac:
bash sync_vps_from_repo.sh
```

### Opción 2: Manualmente vía SSH

```bash
# Conectar al VPS
ssh ubuntu@51.222.207.250
# Contraseña: Cool220479..@

# Actualizar repositorio
cd /opt/claudio-bot
git fetch origin master
git reset --hard origin/master
git pull origin master

# Reiniciar servicios
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot

# Verificar estado
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot
```

## Comandos de Telegram Soportados

Ahora el bot puede:

| Comando | Acción |
|---------|--------|
| `PUEDES ELIMINAR TODOS LOS WORKFLOWS?` | Elimina todos los workflows uno por uno |
| `LISTA LOS WORKFLOWS` | Muestra todos los workflows existentes |
| `CREA UN WORKFLOW CON WEBHOOK Y AIRTABLE` | Busca templates y crea workflow |
| `/status` | Muestra estado del bot y proveedor IA actual |
| `/switch openai` | Cambia a proveedor OpenAI |
| `/health` | Verifica salud del servidor |

## Si el Bot Sigue Sin Responder

### 1. Verificar que el servidor esté corriendo
```bash
ssh ubuntu@51.222.207.250
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot
```

### 2. Verificar logs del servidor
```bash
# Logs del servidor
sudo journalctl -u claudio-server -n 50 -f

# Logs del bot
sudo journalctl -u claudio-telegram-bot -n 50 -f
```

### 3. Reiniciar servicios manualmente
```bash
sudo systemctl restart claudio-server
sudo systemctl restart claudio-telegram-bot
```

### 4. Verificar conexión con n8n
```bash
# Probar API key de n8n
curl -H "X-N8N-API-KEY: tu_api_key" https://n8n.aicorebots.com/api/v1/workflows
```

## Timeout Persistente

Si el timeout persiste después de la actualización:

1. **Verificar el proveedor IA actual** - Ollama puede ser más lento
2. **Cambiar a OpenAI** - `/switch openai`
3. **Verificar conexión n8n** - Si n8n está lento, aumente el timeout más

## Logs Útiles

```bash
# Ver errores recientes
sudo journalctl -u claudio-server --since "5 minutes ago" | grep -i error

# Ver timeouts
sudo journalctl -u claudio-server --since "5 minutes ago" | grep -i timeout
```

## Versión Actual

- **Versión**: v4.6.2
- **Commit**: 8f51457
- **Fecha**: 2026-04-08

## Pruebas Después de Actualizar

1. Enviar mensaje: `HOLA` - Debería responder rápido
2. Enviar: `/status` - Debería mostrar el proveedor actual
3. Enviar: `/health` - Debería mostrar salud del sistema
4. Enviar: `LISTA LOS WORKFLOWS` - Debería listar workflows
5. Enviar: `PUEDES CREAR UN WORKFLOW SIMPLE?` - Debería intentar crear uno

---

Si el problema persiste después de actualizar, revisar los logs para identificar el error específico.
