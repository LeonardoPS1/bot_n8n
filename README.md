# 🤖 Claudio: Tu Experto Orquestador de n8n

<div align="center">

**Automatiza n8n a través de lenguaje natural. Crea, gestiona y escala tus flujos sin fricción.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![AI Providers](https://img.shields.io/badge/IA-Claude%20%7C%20GPT%20%7C%20DeepSeek%20%7C%20GLM-orange.svg)](#)

[Guía de Instalación](docs/INSTALLATION.md) • [Capacidades Técnicas](docs/CAPABILITIES.md) • [Soporte](#)

</div>

---

## 📖 ¿Qué es Claudio?

**Claudio** es un asistente de IA de élite diseñado para desarrolladores y entusiastas de **n8n**. Al integrar los modelos de lenguaje más avanzados (Claude 3.5, GPT-4o, etc.) con el API de n8n mediante el protocolo MCP (Model Context Protocol), Claudio te permite controlar toda tu infraestructura de automatización desde la palma de tu mano a través de Telegram.

Desde diseñar integraciones complejas hasta buscar entre **más de 10,800 plantillas de la comunidad**, Claudio elimina la barrera técnica de la automatización.

---

## ✨ Características Destacadas

*   **🧠 Inteligencia Multi-IA**: Sistema de redundancia automática que salta entre Anthropic, OpenAI y otros proveedores si uno falla.
*   **🧩 Biblioteca Masiva**: Acceso instantáneo a 2,700 recetas oficiales y 8,100 flujos de la comunidad indexados localmente.
*   **⚡ Lógica Auto-Correctiva**: Claudio entiende las sutiles sintaxis de n8n y te guía para evitar errores de conexión o expresión.
*   **📱 Control Remoto Total**: Gestiona ciclos de vida de flujos (Listar, Activar, Editar, Borrar) directamente desde el chat.
*   **🛠️ Arquitectura Profesional**: Optimizado para despliegue en VPS con servicios de sistema (`systemd`) o Docker.

---

## 🚀 Inicio Rápido en 3 Pasos

### 1. Requisitos
Asegúrate de tener **Python 3.10+** y tu **API Key de n8n**.

### 2. Instalación
```bash
git clone https://github.com/LeonardoPS1/bot_n8n.git
cd bot_n8n
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
cp .env.example .env
```

### 3. Configuración y Ejecución
Edita el archivo `.env` con tus tokens y lanza los servicios:
```bash
# Terminal 1: Servidor de IA
python claudio_complete.py

# Terminal 2: Bot de Telegram
python bot_v2.py
```

*Para un despliegue detallado en un servidor VPS, consulta la [Guía de Instalación](docs/INSTALLATION.md).*

---

## 📁 Estructura del Proyecto

El repositorio ha sido optimizado para ser limpio y escalable:

```text
.
├── claudio_complete.py      # Núcleo de IA y Servidor MCP
├── bot_v2.py                # Cliente de Bot de Telegram
├── n8n_database.py          # Biblioteca de Nodos y Templates
├── n8n_mcp_tools.py         # Proxy de Herramientas y API n8n
├── docs/                    # Guías de Instalación y Capacidades
├── tools/                   # Herramientas de Despliegue e Indexación
├── utils/archive/           # Backups de scripts antiguos
└── skills/                  # Personalidades y habilidades de IA
```

---

## 🤝 Soporte y Contribuciones

- **Documentación Completa**: Explora la carpeta `docs/` para guías profundas.
- **Problemas**: Reporta errores o solicita funciones en [GitHub Issues](https://github.com/LeonardoPS1/bot_n8n/issues).
- **Hecho con ❤️**: Por entusiastas de la automatización para el ecosistema n8n.

---

<p align="center">
  <i>"Automatizando el mundo, mensaje a mensaje."</i>
</p>
