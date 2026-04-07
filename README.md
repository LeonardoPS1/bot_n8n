# 🤖 Bot n8n - Asistente Experto de n8n en Telegram

Bot de Telegram potenciado por **Claude AI** con acceso completo a **n8n-MCP**, experto en automatización de workflows con 1,396 nodos y 2,709+ plantillas.

## 🌟 Características

- ✅ **Claudio** - Asistente experto en n8n con Claude AI
- ✅ **1,396 nodos n8n** - Base de datos completa de nodos core y community
- ✅ **2,709+ plantillas** - Acceso a templates de workflows
- ✅ **7 skills especializadas** - Experto en expresiones, validación, patrones
- ✅ **API n8n real** - Crear y modificar workflows directamente
- ✅ **24/7 disponible** - Despliegue en VPS con systemd

## 🚀 Quick Start

### 1. Clonar Repositorio
```bash
git clone https://github.com/leonardospedaletti/bot_n8n.git
cd bot_n8n/telegram-claude-bot
```

### 2. Instalar Dependencias
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
```bash
cp .env.example .env
nano .env
```

### 4. Ejecutar Localmente
```bash
# Terminal 1: Servidor Claudio
python claudio_complete.py

# Terminal 2: Bot de Telegram
python bot_v2.py
```

### 5. Desplegar en VPS
```bash
chmod +x deploy_complete.sh
./deploy_complete.sh
```

## 📖 Documentación Completa

Consulta [docs/TUTORIAL_COMPLETO_CLAUDIO_N8N.md](docs/TUTORIAL_COMPLETO_CLAUDIO_N8N.md)

## 📁 Estructura del Proyecto

```
bot_n8n/
├── telegram-claude-bot/         # Código principal
│   ├── claudio_complete.py      # Servidor principal
│   ├── bot_v2.py                # Bot de Telegram
│   ├── n8n_mcp_tools.py         # Cliente n8n API
│   ├── n8n_database.py          # BD de nodos y templates
│   └── skills/                  # Skills especializadas
├── .skills/                     # Documentación de skills
├── docs/                        # Documentación completa
└── README.md                    # Este archivo
```

## 📊 Estadísticas

- **1,396** nodos n8n documentados
- **2,709+** plantillas de workflows
- **7** skills especializadas
- **812** nodos core
- **584** nodos community

## 📝 Licencia

MIT License - Ver archivo LICENSE para detalles.

## 👨‍💻 Autor

**Leonardo Pablo Spedaletti**

---

**Hecho con ❤️ y mucho ☕**
