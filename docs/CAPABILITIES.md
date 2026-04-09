# 🚀 Claudio Bot - Capabilities & Features

Claudio is not just a bot; it's a complete **AI Orchestrator for n8n**. Below is a detailed list of what Claudio can do and the technology behind it.

## 🧠 Core Intelligence
- **Multi-AI Provider Suite**: Native support for **Anthropic (Claude 3.5 Sonnet)**, **OpenAI (GPT-4o)**, **DeepSeek**, **GLM**, and **Ollama**.
- **Dynamic Failover**: If the primary AI provider (e.g., Anthropic) hits a rate limit or goes down, Claudio automatically switches to the next available provider in your custom fallback list.
- **n8n Expert Logic**: Claudio is trained on n8n best practices, common configuration errors, and complex expression syntax.

## 🛠️ n8n Operations
- **Workflow Synthesis**: Create complex workflows from natural language. Claudio understands 1,300+ nodes and their specific parameters.
- **Full Lifecycle Management**:
    - `List`: View all workflows with their current status.
    - `Get`: Retrieve JSON definitions or detailed summaries.
    - `Update`: Modify existing workflows.
    - `Activate/Deactivate`: Control production workflows from your phone.
    - `Delete`: Clean up individual workflows or bulk-delete everything.

## 📦 Extended Knowledge Base
- **Core Nodes (810+)**: Full knowledge of all native n8n nodes.
- **Community Nodes (580+)**: Deep understanding of popular community-contributed nodes.
- **Workflow Templates (10,800+)**:
    - **2,700+ Core Templates**: Official n8n recipes.
    - **8,100+ Community Templates**: Real-world solutions indexed from the global n8n community.
- **Search Engine**: Use the `get_community_workflow` tool to find proven solutions for any integration (e.g., "Find workflows for Binance and Google Sheets").

## 🔒 Security & Deployment
- **Granular Access Control**: Restrict usage to specific Telegram User IDs (`ALLOWED_USERS`).
- **Admin Commands**: Sensitive operations (like managing models or deleting all workflows) are restricted to `ALLOWED_ADMIN_USERS`.
- **VPS Ready**: Optimized scripts for deploying as a `systemd` service or via **Docker/Docker-Compose**.
- **Environment Isolation**: Uses `.env` for all sensitive keys.

## 🎨 Interactive Experience
- **Model Switching**: `/switch <provider>` to change the AI brain on the fly.
- **Health Monitoring**: `/health` to check if the server and n8n API are responding.
- **Context Awareness**: Remembers recent conversation steps to help you refine a workflow creation.
