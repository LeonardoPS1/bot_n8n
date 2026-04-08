# Claudio - Expert n8n Workflow Assistant Bot

> 🤖 Your intelligent Telegram bot powered by AI for n8n workflow automation

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-4.1-brightgreen.svg)](https://github.com/LeonardoPS1/bot_n8n)

---

## 🌟 Features

- **🧠 AI-Powered**: Powered by Claude AI or GPT-4 with multi-provider support
- **📊 n8n Integration**: Complete access to 1,396 n8n nodes and 2,709+ workflow templates
- **🔧 Workflow Management**: Create, modify, and validate n8n workflows via chat
- **🎯 Expression Validation**: Validate n8n expressions and fix common errors
- **📝 Code Generation**: Generate code for n8n Code nodes (JavaScript/Python)
- **🔒 Secure**: User restriction support and environment-based configuration
- **🚀 Multiple Deployments**: Local, VPS, or Docker deployment options
- **📖 Complete Guide**: Step-by-step installation guide included

---

## 📸 Quick Start (3 minutes)

```bash
# Clone the repository
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n

# Run the interactive installer
python3 install.py
```

The installer will guide you through:
- ✅ Select AI provider (Anthropic Claude, OpenAI GPT-4, Ollama, or multiple)
- ✅ Configure Telegram bot token
- ✅ Set up n8n integration (optional)
- ✅ Choose deployment mode (Local, VPS, or Docker)
- ✅ Configure security settings
- ✅ Run post-installation tests

---

## 📖 Complete Installation Guide

**For detailed installation instructions, troubleshooting, and FAQ:**

### 📄 [GUIA_INSTALACION_COMPLETA.md](GUIA_INSTALACION_COMPLETA.md)

This guide includes:
- Step-by-step installation for all deployment modes
- How to obtain all required credentials
- Complete troubleshooting section
- FAQ with answers to common questions
- Post-installation verification

**Or view it as PDF:** Convert the Markdown file to PDF for offline reading.

---

## 📋 Quick Configuration

### Minimum Required Credentials

| Credential | Where to Get |
|------------|--------------|
| Telegram Bot Token | [@BotFather](https://t.me/BotFather) - `/newbot` |
| Anthropic API Key | [console.anthropic.com](https://console.anthropic.com) - Settings → API Keys |
| OpenAI API Key | [platform.openai.com](https://platform.openai.com) - API Keys |

### Environment Variables (.env)

```bash
# Telegram
TELEGRAM_TOKEN=your_telegram_bot_token_here

# AI Provider (choose one)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Or OpenAI
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4o

# n8n (optional)
N8N_API_KEY=your_n8n_api_key
N8N_INSTANCE_URL=https://n8n.yourdomain.com

# Server
CLADIO_PORT=8000
CLADIO_SERVER_URL=http://localhost:8000

# Security
ALLOWED_USERS=*  # or comma-separated user IDs
```

---

## 🚀 Deployment Options

### Local Development

```bash
# Terminal 1: Start server
python claudio_complete.py

# Terminal 2: Start bot
python bot_v2.py
```

### VPS Deployment

```bash
# After running installer, execute:
bash deploy_vps.sh

# Or manually:
ssh user@your-vps
# Follow manual installation guide in GUIA_INSTALACION_COMPLETA.md
```

### Docker

```bash
# Configure .env first
cp .env.example .env
nano .env

# Start
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 💡 Usage Examples

Once your bot is running, open Telegram and start chatting!

### Create a Workflow

```
You: Create a workflow that sends a Slack message when a webhook is received

Claudio: I'll help you create a webhook-to-Slack workflow:

1. Webhook Trigger - Receives HTTP POST requests
2. Set Node - Extracts message from webhook body
3. Slack Node - Sends message to channel

Configuration for Webhook node:
- Path: slack-webhook
- Method: POST
- Response Mode: lastNode

Would you like me to create this workflow for you?
```

### Validate an Expression

```
You: Validate this expression: {{$json.data.user.email}}

Claudio: The expression syntax is correct ✓

Notes:
- $json accesses the current item's data
- Nested fields use dot notation
- This expression extracts: data.user.email from the JSON
```

### Get Node Information

```
You: Tell me about the Slack node in n8n

Claudio: Here's information about the Slack node:

Node Type: n8n-nodes-base.slack
Description: Send messages to Slack

Key Operations:
- message: Post a message to a channel
- user: Get user information
- channel: Get channel information

Required parameters for message operation:
- channelId: The channel ID
- text: Message text

Would you like me to help you configure a Slack node?
```

---

## 🧩 What Claudio Can Do

| Task | Description |
|------|-------------|
| **Create Workflows** | Design complete n8n workflows from descriptions |
| **Validate Expressions** | Check n8n expressions for syntax errors |
| **Generate Code** | Write JavaScript/Python for Code nodes |
| **Search Nodes** | Find the right n8n nodes for your needs |
| **Debug Issues** | Troubleshoot workflow problems |
| **Explain Concepts** | Teach n8n best practices |
| **Template Access** | Search 2,709+ workflow templates |

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Telegram User  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Telegram Bot   │─────▶│  Claudio Server  │
│   (bot_v2.py)   │      │(claudio_complete)│
└─────────────────┘      └────────┬─────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              ┌─────────┐   ┌─────────┐   ┌─────────┐
              │Anthropic│   │ OpenAI  │   │  Ollama │
              │   API   │   │   API   │   │ (Local) │
              └─────────┘   ┘─────────┘   └─────────┘
                    │
                    ▼
              ┌─────────┐   ┌─────────┐
              │   n8n   │   │  Node   │
              │   API   │   │Database │
              └─────────┘   └─────────┘
```

---

## 🛠️ Development

### Project Structure

```
bot_n8n/
├── bot_v2.py                 # Telegram bot interface
├── claudio_complete.py       # FastAPI server with AI
├── n8n_database.py           # n8n nodes and templates database
├── n8n_mcp_tools.py          # n8n-MCP tools implementation
├── install.py                # Interactive installer ⭐
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── GUIA_INSTALACION_COMPLETA.md  # Complete guide 📖
├── deploy_vps_complete.sh    # VPS deployment script
├── test_installation.sh      # Post-installation test
├── skills/                   # Specialized AI skills
│   ├── __init__.py
│   ├── n8n_expression_syntax.py
│   └── n8n_other_skills.py
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose setup
└── README.md                 # This file
```

---

## 🐛 Troubleshooting

### Bot doesn't respond

```bash
# Check bot logs
sudo journalctl -u claudio-telegram-bot -f  # VPS
# Or check terminal output (local)

# Verify bot token
echo $TELEGRAM_TOKEN

# Test API connection
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### API errors

```bash
# Check server logs
sudo journalctl -u claudio-server -f  # VPS

# Verify API keys
cat .env | grep API_KEY

# Test health endpoint
curl http://localhost:8000/health
```

### For more solutions

See the [Complete Installation Guide](GUIA_INSTALACION_COMPLETA.md#7-solución-de-problemas)

---

## 🔒 Security

- **User Restriction**: Limit bot access to specific Telegram users
- **Environment Variables**: Never commit `.env` file
- **API Key Rotation**: Regularly update your API keys
- **HTTPS**: Use HTTPS for production deployments
- **Rate Limiting**: Consider implementing rate limits for production

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Support

- 📖 [Complete Guide](GUIA_INSTALACION_COMPLETA.md)
- 🐛 [Issue Tracker](https://github.com/LeonardoPS1/bot_n8n/issues)
- 💬 [Discussions](https://github.com/LeonardoPS1/bot_n8n/discussions)

---

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com) for Claude AI
- [OpenAI](https://openai.com) for GPT-4
- [n8n](https://n8n.io) for the workflow automation platform
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the excellent library

---

**Made with ❤️ by LeonardoPS1**

*Star ⭐ this repo if it helped you!*
