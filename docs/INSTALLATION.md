# 🛠️ Claudio Bot - Guía Maestra de Instalación Paso a Paso

Esta guía detallada te llevará desde cero hasta tener a Claudio operando al 100% en tu máquina local o en un servidor VPS.

---

## 📋 Fase 1: Requisitos Previos

Antes de comenzar, asegúrate de tener lo siguiente:

1.  **Python 3.10+**: El lenguaje base del proyecto.
2.  **Tokens Esenciales**:
    *   **Telegram Bot Token**: Obtenido a través de [@BotFather](https://t.me/botfather).
    *   **n8n API Key**: Generada en `Settings > API` dentro de tu instancia de n8n.
    *   **AI API Keys**: Al menos una de las siguientes: Anthropic (Claude), OpenAI (GPT), DeepSeek o GLM.

---

## 💻 Fase 2: Instalación Local (Windows/macOS/Linux)

Ideal para pruebas de desarrollo o uso personal.

### 1. Clonar el repositorio
```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
```

### 2. Configurar el entorno virtual
```bash
python -m venv venv
# Activar en Windows:
venv\Scripts\activate
# Activar en Linux/macOS:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configuración del entorno
Copia el archivo de ejemplo y edítalo con tus credenciales:
```bash
cp .env.example .env
```
> [!IMPORTANT]
> Edita el archivo `.env` y asegúrate de añadir tu **ID de usuario de Telegram** en `ALLOWED_USERS` para que Claudio te reconozca.

---

## 🌐 Fase 3: Despliegue Profesional en VPS (Ubuntu/Debian)

Sigue estos pasos para una operación 24/7 estable.

### 1. Preparación del Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv git -y
```

### 2. Despliegue Automatizado
Hemos optimizado el proceso para que puedas sincronizar desde tu PC local al VPS usando nuestra herramienta en PowerShell:
```powershell
# Ejecuta esto en tu PC local (requiere acceso SSH configurado)
./tools/actualizar_vps.ps1
```

### 3. Configuración de Servicios (Systemd)
Para que Claudio se inicie automáticamente y se reinicie en caso de error, configuramos dos servicios:

**A. Claudio Server (El Cerebro):** `/etc/systemd/system/claudio-server.service`
```ini
[Unit]
Description=Claudio AI Server
After=network.target

[Service]
User=tu-usuario
WorkingDirectory=/opt/claudio-bot
ExecStart=/opt/claudio-bot/venv/bin/python claudio_complete.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**B. Claudio Bot (La Interfaz):** `/etc/systemd/system/claudio-bot.service`
```ini
[Unit]
Description=Claudio Telegram Bot
After=claudio-server.service

[Service]
User=tu-usuario
WorkingDirectory=/opt/claudio-bot
ExecStart=/opt/claudio-bot/venv/bin/python bot_v2.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Activación
```bash
sudo systemctl daemon-reload
sudo systemctl enable claudio-server claudio-bot
sudo systemctl start claudio-server claudio-bot
```

---

## 📚 Mantenimiento y Actualizaciones

*   **Actualizar Código**: Usa `git pull` y reinicia los servicios con `sudo systemctl restart claudio-bot claudio-server`.
*   **Ver Logs**: `sudo journalctl -u claudio-bot -f`
*   **Herramientas**: Explora la carpeta `tools/` para scripts de indexación y diagnóstico.
