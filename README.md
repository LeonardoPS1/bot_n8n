# 🤖 Claudio: The n8n AI Orchestrator

<div align="center">

**Unleash the power of n8n through Natural Language. Create, Manage, and Automate.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI Providers](https://img.shields.io/badge/AI-Claude%20%7C%20GPT%20%7C%20DeepSeek%20%7C%20GLM-orange.svg)](#)

[Deployment Guide](docs/INSTALLATION.md) • [Capabilities](docs/CAPABILITIES.md) • [API Info](#)

</div>

---

## 📖 Overview

**Claudio** is a state-of-the-art AI assistant designed specifically for **n8n developers**. By bridging multiple top-tier AI models (Claude 3.5, GPT-4o, etc.) with a direct n8n-MCP (Model Context Protocol) integration, Claudio allows you to control your automation infrastructure using Telegram.

Whether you need to create a complex Slack integration, activate a dormant workflow, or search through **8,000+ community templates**, Claudio handles the complexity for you.

## ✨ Why Claudio?

- **🧠 Multi-AI Resilience**: Automatic failover between providers (Anthropic, OpenAI, DeepSeek, etc.).
- **🧩 10,800+ Templates**: Massive library of 2,700 core recipes and 8,100 community-indexed workflows.
- **⚡ Proactive Logic**: Understands `$json.body`, connections, and complex expression syntax.
- **📱 Native Telegram**: Manage your entire n8n instance from your chat app.
- **🛠️ Fully Extensible**: Add your own specialized n8n skills and custom node databases.

---

## 🚀 Quick Start

### 1. Requirements
Ensure you have **Python 3.10+** and an **n8n API Key**.

### 2. Setup
```bash
git clone https://github.com/leonardohh/telegram-claude-bot.git
cd telegram-claude-bot
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
```

### 3. Run
```bash
# Start the AI brain
python claudio_complete.py

# Start the Telegram Interface (in a second terminal)
python bot_v2.py
```

*For a full production deployment on VPS, see our [Installation Guide](docs/INSTALLATION.md).*

---

## 📁 Project Structure

```text
.
├── claudio_complete.py      # Core AI Logic & MCP Server
├── bot_v2.py                # Telegram Bot Client
├── n8n_database.py          # n8n Node & Template Library
├── n8n_mcp_tools.py         # Internal Tooling & API Proxy
├── mcp_client.py            # Bridge to n8n-mcp npx
├── docs/                    # Detailed Documentation
├── tools/                   # Deployment & Maintenance Utilities
└── skills/                  # Specialized AI Personality & Skills
```

---

## 🤝 Support & Community

- **Full Documentation**: Check the [docs/](docs/) folder for deep dives.
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/leonardohh/telegram-claude-bot/issues).
- **Made with ❤️**: By automation enthusiasts, for automation enthusiasts.

---

<p align="center">
  <i>"Automating the world, one message at a time."</i>
</p>
