# 🤖 Claudio - Expert n8n Workflow Automation Bot

<div align="center">

**Telegram Bot powered by AI that creates, manages, and automates n8n workflows**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Features](#-features) • [Installation](#-installation) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**Claudio** is an intelligent Telegram bot that serves as your personal n8n workflow expert. It combines the power of multiple AI providers (OpenAI, Anthropic, Ollama) with direct n8n API integration to create, manage, and automate workflows through simple natural language commands.

### 🎯 What Can Claudio Do?

- **🔨 Create Workflows**: Describe what you need and Claudio creates it in your n8n instance
- **🗑️ Delete Workflows**: Remove single or all workflows with one command
- **📋 List Workflows**: See all your workflows with status
- **⚡ Activate/Deactivate**: Control workflow execution
- **🧠 AI-Powered**: Expert advice on n8n best practices, expression syntax, and node configuration
- **🔄 Multi-AI Provider**: Switch between OpenAI, Anthropic, and Ollama dynamically

### 🌟 Key Features

| Feature | Description |
|---------|-------------|
| **Natural Language Processing** | Just describe what you want in plain language |
| **Real n8n API Integration** | Creates actual workflows, not just templates |
| **50+ n8n Nodes** | Comprehensive knowledge of core, community, and AI nodes |
| **Expression Syntax Expert** | Knows `$json`, `$node`, `$now`, and all n8n expressions |
| **Multi-AI Provider** | OpenAI GPT-4, Anthropic Claude, Ollama support |
| **Workflow Validation** | Checks configurations before creating |
| **Telegram Native** | Works where you already chat |
| **VPS Ready** | Deploy on any VPS with Docker or systemd |

---

## ✨ Features in Detail

### Workflow Creation

```
You: "crea un workflow con webhook y airtable"

Claudio:
✅ Workflow creado exitosamente!
🔧 ID: YkZeVAETlINuULJw
📊 Nodos creados: 2
🔗 Ver: https://n8n.aicorebots.com/workflow/YkZeVAETlINuULJw
```

### Workflow Management

```
You: "lista mis workflows"

Claudio:
📋 Tus Workflows (3):
• Webhook to Slack (abc123) - ✅ Activo
• Gmail Parser (def456) - ⏸️ Inactivo
• AI Agent (ghi789) - ⏸️ Inactivo
```

### Delete Operations

```
You: "elimina todos los workflows"

Claudio:
✅ Todos los workflows eliminados
🗑️ Workflows eliminados: 3
```

### Expert Advice

```
You: "cómo accedo a los datos del webhook en n8n?"

Claudio:
Para acceder a los datos del webhook en n8n, usa:
- $json.body - Para el cuerpo del request (CRITICAL)
- $json.body.field - Para un campo específico
- $node["Webhook"].json.body - Para la salida del nodo Webhook

⚠️ IMPORTANTE: Nunca uses $json directamente para webhooks,
siempre usa $json.body
```

---

## 🚀 Installation

### Quick Start (Local)

```bash
# Clone the repository
git clone https://github.com/leonardohh/telegram-claude-bot.git
cd telegram-claude-bot

# Run the interactive installer
python install.py

# Follow the prompts:
# - Select installation type (Local/VPS)
# - Configure AI provider (OpenAI/Anthropic/Ollama)
# - Enter API keys
# - Configure n8n connection
# - Set up Telegram bot

# Start the services
python start.py
```

### VPS Deployment (Ubuntu/Debian)

```bash
# Clone on your VPS
git clone https://github.com/leonardohh/telegram-claude-bot.git
cd telegram-claude-bot

# Run VPS installer
bash install_vps.sh

# The installer will:
# - Install Python 3.10+
# - Install required dependencies
# - Set up systemd services
# - Configure firewall rules
# - Start all services automatically
```

### Docker Deployment

```bash
# Clone repository
git clone https://github.com/leonardohh/telegram-claude-bot.git
cd telegram-claude-bot

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env

# Build and run
docker-compose up -d
```

---

## 📋 Requirements

### Minimum Requirements

- **Python**: 3.10 or higher
- **RAM**: 512MB minimum, 1GB recommended
- **Disk**: 100MB free space
- **OS**: Linux, macOS, or Windows (WSL2 recommended)

### AI Provider Requirements

| Provider | API Key Required | Models Available |
|----------|------------------|------------------|
| **OpenAI** | ✅ Required | GPT-4, GPT-4o, GPT-3.5 |
| **Anthropic** | ✅ Required | Claude 3 Opus, Sonnet, Haiku |
| **Ollama** | ❌ Not required | phi3, llama2, mistral, etc. |

### Optional Services

- **n8n Instance**: For workflow creation and management
- **Telegram Bot Token**: Required for Telegram integration
- **VPS**: For 24/7 operation (recommended)

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Telegram Configuration
TELEGRAM_TOKEN=your_telegram_bot_token
ALLOWED_USERS=123456789,987654321
ALLOWED_ADMIN_USERS=123456789

# AI Provider Configuration
AI_PROVIDER=multi
AUTO_FALLBACK=true
FALLBACK_ORDER=openai,anthropic,ollama

# OpenAI (if using)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o

# Anthropic (if using)
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Ollama (if using)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# n8n Configuration
N8N_API_KEY=your_n8n_api_key
N8N_INSTANCE_URL=https://your-n8n-instance.com
N8N_HOST_HEADER=your-n8n-instance.com

# Server Configuration
CLADIO_PORT=8001
REQUEST_TIMEOUT=60
```

### Getting Your API Keys

#### Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy the API token
4. Set your bot's name and description

#### OpenAI API Key

1. Visit [platform.openai.com](https://platform.openai.com)
2. Go to API Keys section
3. Create a new API key
4. Copy and save it securely

#### Anthropic API Key

1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Go to API Keys
3. Create a new key
4. Copy and save it securely

#### n8n API Key

1. Open your n8n instance
2. Go to Settings → API
3. Create a new API key
4. Copy and configure in `.env`

---

## 📖 Documentation

### User Guide

See [GUIDE.md](GUIDE.md) for detailed usage instructions including:

- All available commands
- Workflow creation examples
- Expression syntax reference
- Troubleshooting guide

### API Documentation

Claudio exposes a REST API for programmatic access:

```python
# Example: Create workflow via API
import requests

response = requests.post('http://localhost:8001/api/chat', json={
    "message": "crea un workflow con webhook y slack",
    "user_id": 123,
    "user_name": "User"
})

workflow_id = response.json()['workflow_id']
```

See [API.md](API.md) for complete API documentation.

### System Architecture

```
┌─────────────┐
│  Telegram   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  bot_v2.py      │  ← Telegram Bot (python-telegram-bot)
│  (Client)       │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────────────────┐
│  claudio_complete.py        │  ← FastAPI Server
│  (Server)                   │
│  ┌──────────────────────┐   │
│  │  DynamicMultiProvider│   │  ← AI Provider Manager
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │  N8NWorkflowCreator  │   │  ← n8n API Client
│  └──────────────────────┘   │
│  ┌──────────────────────┐   │
│  │  N8N_NODES Database  │   │  ← 50+ Nodes Config
│  └──────────────────────┘   │
└──────────┬──────────────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│  n8n Instance       │  ← Your n8n Server
│  /api/v1/workflows  │
└─────────────────────┘
```

---

## 🎓 Usage Examples

### Creating Different Workflows

```bash
# Webhook to Slack
"crea un workflow con webhook y slack"

# Data Processing
"crea un workflow con webhook, set y http request"

# AI Integration
"crea un workflow con webhook, openai y telegram"

# Database Operations
"crea un workflow con schedule trigger, postgres y email"
```

### Managing Workflows

```bash
# List all workflows
"lista mis workflows"
"que workflows tengo"

# Delete specific workflow
"elimina el workflow abc123"

# Delete all workflows
"elimina todos los workflows"
"borra todo"

# Activate workflow
"activa el workflow abc123"
```

### Getting Help

```bash
# Start command
/start  # Shows welcome message and commands

# Help command
/help   # Shows detailed help

# Health check
/health # Shows server status

# Admin commands
/admin  # Shows all admin commands
/status # Shows current AI model
/models # Lists available models
/switch openai  # Switch AI provider
```

---

## 🔒 Security

### Best Practices

1. **API Keys**: Never commit `.env` file to version control
2. **User Permissions**: Use `ALLOWED_USERS` to restrict access
3. **Admin Commands**: Protect sensitive commands with `ALLOWED_ADMIN_USERS`
4. **HTTPS**: Use HTTPS in production (configure reverse proxy)
5. **Firewall**: Only expose necessary ports (8001 for server)

### Rate Limiting

The bot includes built-in rate limiting:
- Telegram API: 30 requests/second
- OpenAI API: 3500 requests/minute
- n8n API: No built-in limit (depends on your plan)

---

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
```bash
# Check services status
sudo systemctl status claudio-server
sudo systemctl status claudio-telegram-bot

# Check logs
sudo journalctl -u claudio-server -n 50
sudo journalctl -u claudio-telegram-bot -n 50
```

**Workflow creation fails:**
- Verify n8n API key is valid
- Check n8n instance is accessible
- Ensure you have permissions to create workflows

**AI provider errors:**
- Check API key is valid
- Verify you have credits/usage available
- Try switching providers with `/switch <provider>`

**Permission denied:**
- Add your Telegram user ID to `ALLOWED_USERS`
- Get your ID from [@userinfobot](https://t.me/userinfobot)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Fork the repository
git clone https://github.com/yourusername/telegram-claude-bot.git
cd telegram-claude-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Start development server
python claudio_complete.py
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Write tests for new features

---

## 📝 Changelog

### Version 5.0 (Current)

- ✅ Complete workflow CRUD operations
- ✅ Multi-AI provider support with dynamic switching
- ✅ Direct n8n API integration
- ✅ 50+ n8n nodes database
- ✅ Expression syntax expert
- ✅ Interactive installer
- ✅ Comprehensive documentation

### Version 4.0

- Initial Telegram bot implementation
- Basic workflow creation
- OpenAI integration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [n8n](https://n8n.io) - Workflow automation platform
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot wrapper
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [OpenAI](https://openai.com/) - GPT models
- [Anthropic](https://www.anthropic.com/) - Claude models

---

## 📞 Support

- 📧 Email: support@claudio-bot.com
- 💬 Telegram: [@ClaudioSupport](https://t.me/ClaudioSupport)
- 📖 Documentation: [Full Guide](GUIDE.md)
- 🐛 Issues: [GitHub Issues](https://github.com/leonardohh/telegram-claude-bot/issues)

---

<div align="center">

**Made with ❤️ by the Claudio team**

[⬆ Back to Top](#-claudio---expert-n8n-workflow-automation-bot)

</div>
