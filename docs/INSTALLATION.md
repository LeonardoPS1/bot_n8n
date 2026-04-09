# 🛠️ Claudio Bot - Installation Guide

This guide will walk you through the process of deploying Claudio Bot on a local machine or a Linux VPS.

## 📋 Prerequisites
- **Python**: 3.10 or higher.
- **Git** installed.
- **n8n Instance**: An active n8n instance with API access.
- **Telegram Bot**: A bot token from [@BotFather](https://t.me/botfather).
- **AI API Keys**: At least one key from Anthropic, OpenAI, DeepSeek, or GLM.

---

## 🚀 Standard Installation (Local/VPS)

### 1. Clone the Repository
```bash
git clone https://github.com/leonardohh/telegram-claude-bot.git
cd telegram-claude-bot
```

### 2. Environment Setup
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuration
Copy the example environment file and fill in your credentials:
```bash
cp .env.example .env
nano .env  # Or use your favorite editor
```

**Required Variables**:
- `TELEGRAM_TOKEN`: Your bot token.
- `ALLOWED_USERS`: Your Telegram User ID (comma separated).
- `N8N_API_KEY`: Found in n8n settings.
- `N8N_INSTANCE_URL`: Your full n8n URL (e.g., `https://n8n.example.com`).
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.

### 4. Community Workflow Indexing (Optional but Recommended)
To enable Claudio to search over 8,000+ community templates:
```bash
# On Linux:
bash tools/run_index.sh
# Or manually:
python tools/index_community_workflows.py
```

### 5. Start the Project
You need to run TWO services: the AI Server and the Telegram Bot.
```bash
# Service 1: AI Server (Port 8001)
python claudio_complete.py

# Service 2: Telegram Bot (New terminal)
python bot_v2.py
```

---

## 🌐 Production VPS Deployment (Ubuntu/Debian)

For 24/7 operation, we recommend using `systemd`.

### 1. Automated Setup script
We've included a robust update/install helper for Windows-to-VPS sync:
```powershell
./tools/actualizar_vps.ps1
```

### 2. Manual Systemd Configuration
Create a service file for the server: `/etc/systemd/system/claudio-server.service`
```ini
[Unit]
Description=Claudio AI Server
After=network.target

[Service]
User=your-user
WorkingDirectory=/opt/claudio-bot
ExecStart=/opt/claudio-bot/venv/bin/python claudio_complete.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Repeat for the bot: `/etc/systemd/system/claudio-bot.service` using `bot_v2.py`.

### 3. Management
```bash
sudo systemctl daemon-reload
sudo systemctl enable claudio-server claudio-bot
sudo systemctl start claudio-server claudio-bot
```

---

## 🐳 Docker Deployment
```bash
docker-compose up -d
```
*Note: Ensure your `.env` is configured before running docker-compose.*
