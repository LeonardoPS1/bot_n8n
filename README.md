# Claudio - Expert n8n Workflow Assistant Bot

> 🤖 Your intelligent Telegram bot powered by Claude AI for n8n workflow automation

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://t.me/your_bot)

## 🌟 Features

- **🧠 AI-Powered**: Powered by Claude AI (Anthropic) with multi-provider support
- **📊 n8n Integration**: Complete access to 1,396 n8n nodes and 2,709+ workflow templates
- **🔧 Workflow Management**: Create, modify, and validate n8n workflows via chat
- **🎯 Expression Validation**: Validate n8n expressions and fix common errors
- **📝 Code Generation**: Generate code for n8n Code nodes (JavaScript/Python)
- **🔒 Secure**: User restriction support and environment-based configuration
- **🚀 Multiple Deployments**: Local, VPS, or Docker deployment options

## 📸 Quick Start

### Method 1: Interactive Installer (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/claudio-bot.git
cd claudio-bot

# Run the interactive installer
python3 install.py
```

The installer will guide you through:
1. ✅ Select AI provider (Anthropic, OpenAI, Ollama, or multiple)
2. ✅ Configure Telegram bot token
3. ✅ Set up n8n integration (optional)
4. ✅ Choose deployment mode (Local, VPS, or Docker)
5. ✅ Configure security settings

### Method 2: Manual Installation

#### Prerequisites

- Python 3.9+
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Anthropic API Key (get from [console.anthropic.com](https://console.anthropic.com))

#### Installation Steps

```bash
# 1. Clone and navigate
git clone https://github.com/your-username/claudio-bot.git
cd claudio-bot

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 5. Start the bot
python bot_v2.py
```

In another terminal, start the server:

```bash
python claudio_complete.py
```

## 📋 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# ============================================
# TELEGRAM CONFIG
# ============================================
TELEGRAM_TOKEN=your_telegram_bot_token_here

# ============================================
# AI PROVIDER CONFIG
# ============================================

# Option 1: Anthropic (Claude) - Recommended
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# Option 2: OpenAI
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-your-key-here
# OPENAI_MODEL=gpt-4o

# Option 3: Ollama (Local)
# AI_PROVIDER=ollama
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3

# Option 4: Multiple providers
# AI_PROVIDER=multi
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_API_KEY=sk-your-openai-key-here

# ============================================
# N8N CONFIG (Optional)
# ============================================
N8N_API_KEY=your_n8n_api_key
N8N_INSTANCE_URL=https://n8n.yourdomain.com
N8N_HOST_HEADER=n8n.yourdomain.com

# ============================================
# SERVER CONFIG
# ============================================
CLADIO_PORT=8000
CLADIO_SERVER_URL=http://localhost:8000
REQUEST_TIMEOUT=60

# ============================================
# SECURITY
# ============================================
# Restrict to specific Telegram users (comma-separated)
# Get your ID from @userinfobot on Telegram
# Use '*' for public access
ALLOWED_USERS=123456789,987654321
```

### Getting Your Credentials

#### Telegram Bot Token

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow the instructions to create your bot
4. Copy the token provided

#### Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy the key (starts with `sk-ant-`)

#### n8n API Key (Optional)

1. Access your n8n instance
2. Go to Settings → API → Create API Key
3. Copy the generated key

## 🚀 Deployment Options

### Option 1: Local Development

```bash
# Start the server
python claudio_complete.py

# In another terminal, start the bot
python bot_v2.py
```

### Option 2: VPS Deployment

#### Automated Deployment

```bash
# After running the installer, use the generated script
bash deploy_vps.sh
```

#### Manual VPS Setup

```bash
# 1. Connect to your VPS
ssh ubuntu@your-vps-ip

# 2. Install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# 3. Create user and directories
sudo useradd -m -s /bin/bash claudio
sudo mkdir -p /opt/claudio-bot
sudo chown -R claudio:claudio /opt/claudio-bot

# 4. Clone repository
sudo -u claudio git clone https://github.com/your-username/claudio-bot.git /opt/claudio-bot
cd /opt/claudio-bot

# 5. Setup Python environment
sudo -u claudio python3 -m venv venv
sudo -u claudio venv/bin/pip install -r requirements.txt

# 6. Configure environment
sudo -u claudio cp .env.example .env
sudo -u claudio nano .env  # Edit with your credentials

# 7. Create systemd services
sudo tee /etc/systemd/system/claudio-server.service > /dev/null <<EOF
[Unit]
Description=Claudio Server
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null <<EOF
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory=/opt/claudio-bot
EnvironmentFile=/opt/claudio-bot/.env
ExecStart=/opt/claudio-bot/venv/bin/python bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 8. Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable claudio-server claudio-telegram-bot
sudo systemctl start claudio-server claudio-telegram-bot

# 9. Check status
sudo systemctl status claudio-server claudio-telegram-bot
```

### Option 3: Docker Deployment

```bash
# Build and start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📖 Usage

### Starting a Conversation

Once your bot is running, simply open Telegram and start chatting!

**Example conversations:**

```
You: Help me create a workflow that sends a Slack message when a webhook is received

Claudio: I'll help you create a webhook-to-Slack workflow. Here's the setup:

1. **Webhook Trigger** - Receives HTTP POST requests
2. **Set Node** - Extracts message from webhook body
3. **Slack Node** - Sends message to channel

Configuration for Webhook node:
- Path: slack-webhook
- Method: POST
- Response Mode: lastNode

Would you like me to create this workflow for you?
```

### What Claudio Can Do

1. **Create Workflows**: Design complete n8n workflows from descriptions
2. **Validate Expressions**: Check n8n expressions for errors
3. **Generate Code**: Write JavaScript/Python for Code nodes
4. **Search Nodes**: Find the right n8n nodes for your needs
5. **Debug Issues**: Troubleshoot workflow problems
6. **Explain Concepts**: Teach n8n best practices

## 🧩 Architecture

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
              └─────────┘   └─────────┘   └─────────┘
                    │
                    ▼
              ┌─────────┐   ┌─────────┐
              │   n8n   │   │  Node   │
              │   API   │   │Database │
              └─────────┘   └─────────┘
```

## 🛠️ Development

### Project Structure

```
claudio-bot/
├── bot_v2.py              # Telegram bot interface
├── claudio_complete.py    # FastAPI server with AI
├── n8n_database.py        # n8n nodes and templates database
├── n8n_mcp_tools.py       # n8n-MCP tools implementation
├── install.py             # Interactive installer
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
├── skills/                # Specialized AI skills
│   ├── __init__.py
│   ├── n8n_expression_syntax.py
│   └── n8n_other_skills.py
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── README.md              # This file
```

### Adding New Features

1. **New AI Provider**: Add support in `claudio_complete.py`
2. **New Skill**: Add to `skills/` directory and import in `skills/__init__.py`
3. **New API Endpoint**: Add route in `claudio_complete.py`

## 🐛 Troubleshooting

### Common Issues

**Issue: Bot doesn't respond**

```bash
# Check bot logs
journalctl -u claudio-telegram-bot -f

# Verify bot token
echo $TELEGRAM_TOKEN

# Test API connection
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

**Issue: API errors**

```bash
# Check server logs
journalctl -u claudio-server -f

# Verify API keys
cat .env | grep API_KEY

# Test health endpoint
curl http://localhost:8000/health
```

**Issue: n8n connection failed**

```bash
# Test n8n connection
curl -H "X-N8N-API-KEY: <YOUR_KEY>" https://n8n.yourdomain.com/api/v1/workflows

# Check .env configuration
cat .env | grep N8N
```

## 🔒 Security

- **User Restriction**: Limit bot access to specific Telegram users
- **Environment Variables**: Never commit `.env` file
- **API Key Rotation**: Regularly update your API keys
- **HTTPS**: Use HTTPS for production deployments

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📧 Support

- 📖 [Documentation](https://github.com/your-username/claudio-bot/wiki)
- 💬 [Telegram Community](https://t.me/claudio_community)
- 🐛 [Issue Tracker](https://github.com/your-username/claudio-bot/issues)

## 🙏 Acknowledgments

- [Anthropic](https://www.anthropic.com) for Claude AI
- [n8n](https://n8n.io) for the workflow automation platform
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the excellent library

---

**Made with ❤️ by the Claudio team**

*Star ⭐ this repo if it helped you!*
