#!/usr/bin/env python3
"""
Claudio Bot - Interactive Installer v4.6.1
Guided installation with all provider options and configurations
"""

import os
import sys
import subprocess
from pathlib import Path

# Colors for terminal output
class Colors:
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.END}\n")

def print_question(text):
    print(f"{Colors.YELLOW}{text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def get_input(prompt, default=None):
    if default:
        full_prompt = f"{Colors.BOLD}{prompt} [{default}/{Colors.END}]: "
    else:
        full_prompt = f"{Colors.BOLD}{prompt}: {Colors.END}"

    value = input(full_prompt).strip()
    return value if value else default

def select_option(question, options):
    """Display options and get user selection"""
    print_question(question)
    for i, option in enumerate(options, 1):
        print(f"  {Colors.BOLD}[{i}]{Colors.END} {option}")

    while True:
        choice = get_input("Select option")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
        print_error("Invalid option. Please try again.")

def yes_no(question, default=False):
    """Ask yes/no question"""
    default_str = "Y/n" if default else "y/N"
    response = get_input(f"{question} [{default_str}").lower()
    if not response:
        return default
    return response.startswith('y')

# ============================================
# CONFIGURATION STEPS
# ============================================

def step_telegram_config():
    """Step 1: Configure Telegram Bot"""
    print_header("CONFIGURACIÓN DE TELEGRAM")

    print_info("Instrucciones:")
    print("  1. Abre Telegram y busca @BotFather")
    print("  2. Envía /newbot")
    print("  3. Sigue las instrucciones")
    print("  4. Copia el token que te da BotFather")

    telegram_token = get_input("\nTu Token de Telegram")
    if not telegram_token or len(telegram_token) < 20:
        print_error("Token inválido. Debe tener al menos 20 caracteres.")
        return None

    print_info("\nInstrucciones para obtener tu User ID:")
    print("  1. Abre Telegram y busca @userinfobot")
    print("  2. Envía /start")
    print("  3. Copia tu ID numérico")

    user_id = get_input("\nTu User ID de Telegram")

    admin_id = get_input("User ID de Admin (opcional, presiona Enter para omitir)", user_id)

    return {
        'TELEGRAM_TOKEN': telegram_token,
        'ALLOWED_USERS': user_id,
        'ALLOWED_ADMIN_USERS': admin_id
    }

def step_ai_provider():
    """Step 2: Configure AI Provider(s)"""
    print_header("CONFIGURACIÓN DE PROVEEDOR IA")

    providers = [
        "Multi-Proveedor (auto-fallback) ⭐ RECOMENDADO",
        "Anthropic Claude (claude-sonnet-4)",
        "OpenAI GPT-4 (gpt-4o-mini)",
        "Google Gemini (gemini-2.5-pro)",
        "Alibaba Qwen (qwen-plus)",
        "DeepSeek (deepseek-chat)",
        "Ollama (Local y GRATIS) - phi3:mini",
        "Modelo Personalizado"
    ]

    choice = select_option("Selecciona tu proveedor IA principal:", providers)

    config = {}

    if choice == 0:  # Multi-provider
        config['AI_PROVIDER'] = 'multi'
        config['AUTO_FALLBACK'] = 'true'
        config['FALLBACK_ORDER'] = 'openai,ollama,deepseek,gemini,anthropic'

        print_info("\nConfiguraremos los proveedores en orden de prioridad:")

        # OpenAI
        if yes_no("\n¿Tienes API key de OpenAI?", False):
            config['OPENAI_API_KEY'] = get_input("  API Key de OpenAI (sk-proj-...)")
            config['OPENAI_MODEL'] = get_input("  Modelo (default: gpt-4o-mini)", "gpt-4o-mini")

        # Ollama
        if yes_no("\n¿Quieres usar Ollama (GRATIS y local)?", True):
            config['OLLAMA_BASE_URL'] = 'http://localhost:11434'
            config['OLLAMA_MODEL'] = get_input("  Modelo Ollama (default: phi3:mini)", "phi3:mini")

            if yes_no("¿Quieres instalar Ollama ahora?", True):
                install_ollama()

        # DeepSeek
        if yes_no("\n¿Tienes API key de DeepSeek?", False):
            config['DEEPSEEK_API_KEY'] = get_input("  API Key de DeepSeek")
            config['DEEPSEEK_MODEL'] = 'deepseek-chat'
            config['DEEPSEEK_BASE_URL'] = 'https://api.deepseek.com'

        # Gemini
        if yes_no("\n¿Tienes API key de Gemini?", False):
            config['GEMINI_API_KEY'] = get_input("  API Key de Gemini")
            config['GEMINI_MODEL'] = get_input("  Modelo (default: gemini-2.5-pro)", "gemini-2.5-pro")

        # Anthropic
        if yes_no("\n¿Tienes API key de Anthropic?", False):
            config['ANTHROPIC_API_KEY'] = get_input("  API Key de Anthropic")
            config['ANTHROPIC_MODEL'] = get_input("  Modelo (default: claude-sonnet-4-20250514)", "claude-sonnet-4-20250514")

    elif choice == 6:  # Ollama
        config['AI_PROVIDER'] = 'ollama'
        config['OLLAMA_BASE_URL'] = 'http://localhost:11434'
        config['OLLAMA_MODEL'] = get_input("Modelo (default: phi3:mini)", "phi3:mini")

        if yes_no("¿Quieres instalar Ollama ahora?", True):
            install_ollama()

    elif choice == 7:  # Custom
        print_info("\nPara modelo personalizado, necesitas:")
        print("  - URL base de la API (ej: https://api.example.com/v1)")
        print("  - API Key")
        print("  - Tipo de proveedor (openai o anthropic)")

        config['AI_PROVIDER'] = 'custom'
        config['CUSTOM_MODEL_NAME'] = get_input("Nombre del modelo")
        config['CUSTOM_MODEL_API_KEY'] = get_input("API Key")
        config['CUSTOM_MODEL_BASE_URL'] = get_input("URL base de la API")
        config['CUSTOM_MODEL_PROVIDER'] = get_input("Tipo (openai/anthropic)", "openai")

    else:
        # Single providers
        provider_names = ['anthropic', 'openai', 'gemini', 'qwen', 'deepseek']
        provider = provider_names[choice]
        config['AI_PROVIDER'] = provider

        if provider == 'anthropic':
            config['ANTHROPIC_API_KEY'] = get_input("API Key de Anthropic")
            config['ANTHROPIC_MODEL'] = get_input("Modelo (default: claude-sonnet-4-20250514)", "claude-sonnet-4-20250514")

        elif provider == 'openai':
            config['OPENAI_API_KEY'] = get_input("API Key de OpenAI")
            config['OPENAI_MODEL'] = get_input("Modelo (default: gpt-4o-mini)", "gpt-4o-mini")

        elif provider == 'gemini':
            config['GEMINI_API_KEY'] = get_input("API Key de Gemini")
            config['GEMINI_MODEL'] = get_input("Modelo (default: gemini-2.5-pro)", "gemini-2.5-pro")

        elif provider == 'qwen':
            config['QWEN_API_KEY'] = get_input("API Key de Qwen")
            config['QWEN_MODEL'] = get_input("Modelo (default: qwen-plus)", "qwen-plus")
            config['QWEN_BASE_URL'] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

        elif provider == 'deepseek':
            config['DEEPSEEK_API_KEY'] = get_input("API Key de DeepSeek")
            config['DEEPSEEK_MODEL'] = 'deepseek-chat'
            config['DEEPSEEK_BASE_URL'] = 'https://api.deepseek.com'

    return config

def step_n8n_config():
    """Step 3: Configure n8n Integration (Optional)"""
    print_header("INTEGRACIÓN CON N8N (OPCIONAL)")

    if not yes_no("¿Quieres integrar con n8n?", False):
        return {
            'N8N_INSTANCE_URL': 'https://n8n.yourdomain.com',
            'N8N_API_KEY': 'your_n8n_api_key_here',
            'N8N_HOST_HEADER': ''
        }

    print_info("\nInstrucciones:")
    print("  1. Entra a tu instancia n8n")
    print("  2. Ve a Settings → API")
    print("  3. Haz clic en Create API Key")

    instance_url = get_input("\nURL de tu instancia n8n", "https://n8n.yourdomain.com")
    api_key = get_input("API Key de n8n")
    host_header = get_input("Host Header (opcional, para Traefik)", "")

    return {
        'N8N_INSTANCE_URL': instance_url,
        'N8N_API_KEY': api_key,
        'N8N_HOST_HEADER': host_header
    }

def step_deployment_mode():
    """Step 4: Select Deployment Mode"""
    print_header("MODO DE DESPLIEGUE")

    modes = [
        "Local (Desarrollo)",
        "VPS (Producción) ⭐ RECOMENDADO",
        "Docker"
    ]

    choice = select_option("Selecciona el modo de despliegue:", modes)

    if choice == 0:  # Local
        return {'deployment': 'local'}

    elif choice == 1:  # VPS
        print_info("\nConfiguración de VPS:")
        vps_host = get_input("  IP o dominio del VPS", "51.222.207.250")
        vps_user = get_input("  Usuario SSH", "ubuntu")

        return {
            'deployment': 'vps',
            'VPS_HOST': vps_host,
            'VPS_USER': vps_user
        }

    else:  # Docker
        return {'deployment': 'docker'}

def step_install_dependencies():
    """Step 5: Install Dependencies"""
    print_header("INSTALANDO DEPENDENCIAS")

    print_info("Creando entorno virtual...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    print_info("Activando entorno virtual...")
    if os.name == 'nt':  # Windows
        activate_cmd = Path("venv/Scripts/activate")
    else:
        activate_cmd = Path("venv/bin/activate")

    print_info("Instalando dependencias...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"], check=True)

    print_success("Dependencias instaladas correctamente")
    return True

def step_create_env_file(config):
    """Step 6: Create .env file"""
    print_header("CREANDO ARCHIVO .ENV")

    env_content = f"""# Claudio Bot Configuration - Generated by installer
# Generated at: {subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S']).decode().strip()}

# ============================================
# TELEGRAM
# ============================================
TELEGRAM_TOKEN={config.get('TELEGRAM_TOKEN', '')}
ALLOWED_USERS={config.get('ALLOWED_USERS', '')}
ALLOWED_ADMIN_USERS={config.get('ALLOWED_ADMIN_USERS', '')}

# ============================================
# AI PROVIDER
# ============================================
AI_PROVIDER={config.get('AI_PROVIDER', 'multi')}
AUTO_FALLBACK={config.get('AUTO_FALLBACK', 'true')}
FALLBACK_ORDER={config.get('FALLBACK_ORDER', 'openai,ollama,deepseek,gemini,anthropic')}
"""

    # Add provider-specific configs
    if 'ANTHROPIC_API_KEY' in config:
        env_content += f"\nANTHROPIC_API_KEY={config['ANTHROPIC_API_KEY']}"
        env_content += f"\nANTHROPIC_MODEL={config.get('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')}"

    if 'OPENAI_API_KEY' in config:
        env_content += f"\nOPENAI_API_KEY={config['OPENAI_API_KEY']}"
        env_content += f"\nOPENAI_MODEL={config.get('OPENAI_MODEL', 'gpt-4o-mini')}"

    if 'GEMINI_API_KEY' in config:
        env_content += f"\nGEMINI_API_KEY={config['GEMINI_API_KEY']}"
        env_content += f"\nGEMINI_MODEL={config.get('GEMINI_MODEL', 'gemini-2.5-pro')}"

    if 'DEEPSEEK_API_KEY' in config:
        env_content += f"\nDEEPSEEK_API_KEY={config['DEEPSEEK_API_KEY']}"
        env_content += f"\nDEEPSEEK_MODEL={config.get('DEEPSEEK_MODEL', 'deepseek-chat')}"
        env_content += f"\nDEEPSEEK_BASE_URL={config.get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')}"

    if 'OLLAMA_BASE_URL' in config:
        env_content += f"\nOLLAMA_BASE_URL={config['OLLAMA_BASE_URL']}"
        env_content += f"\nOLLAMA_MODEL={config.get('OLLAMA_MODEL', 'phi3:mini')}"

    # n8n config
    env_content += f"\n# ============================================\n"
    env_content += f"# N8N INTEGRATION (Optional)\n"
    env_content += f"# ============================================\n"
    env_content += f"N8N_INSTANCE_URL={config.get('N8N_INSTANCE_URL', 'https://n8n.yourdomain.com')}\n"
    env_content += f"N8N_API_KEY={config.get('N8N_API_KEY', 'your_n8n_api_key_here')}\n"
    if config.get('N8N_HOST_HEADER'):
        env_content += f"N8N_HOST_HEADER={config['N8N_HOST_HEADER']}\n"

    # Server config
    env_content += f"\n# ============================================\n"
    env_content += f"# SERVER CONFIG\n"
    env_content += f"# ============================================\n"
    env_content += f"CLADIO_PORT=8000\n"
    env_content += f"CLADIO_SERVER_URL=http://localhost:8000\n"
    env_content += f"REQUEST_TIMEOUT=120\n"

    with open('.env', 'w') as f:
        f.write(env_content)

    print_success("Archivo .env creado")
    return True

def install_ollama():
    """Install Ollama for local AI"""
    print_info("Instalando Ollama...")

    try:
        if os.name != 'nt':  # Unix-like
            subprocess.run(['curl', '-fsSL', 'https://ollama.com/install.sh', '|', 'sh'], check=True, shell=True)
        else:
            print_error("Ollama no está disponible en Windows. Usa WSL o instala manualmente.")
            return False

        # Pull model
        model = get_input("Modelo a descargar (default: phi3:mini)", "phi3:mini")
        print_info(f"Descargando modelo {model}...")
        subprocess.run(['ollama', 'pull', model], check=True)

        print_success(f"Ollama instalado con modelo {model}")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Error instalando Ollama: {e}")
        return False

def show_summary(config):
    """Show installation summary"""
    print_header("RESUMEN DE CONFIGURACIÓN")

    print(f"{Colors.BOLD}Proveedor IA:{Colors.END} {config.get('AI_PROVIDER', 'multi')}")
    print(f"{Colors.BOLD}Telegram:{Colors.END} ✓ Configurado")
    print(f"{Colors.BOLD}n8n:{Colors.END} {'✓ Integrado' if 'N8N_API_KEY' in config else '⊝ Omitido'}")
    print(f"{Colors.BOLD}Modo:{Colors.END} {config.get('deployment', 'local')}")

    print(f"\n{Colors.BOLD}{Colors.GREEN}¡Instalación completada!{Colors.END}\n")

    print_info("Comandos disponibles:")
    print("  python3 bot_v2.py           # Iniciar bot de Telegram")
    print("  python3 claudio_complete.py # Iniciar servidor API")

    print_info("\nComandos de Telegram:")
    print("  /start  - Iniciar el bot")
    print("  /status - Ver estado actual")
    print("  /models - Listar modelos")
    print("  /switch <provider> - Cambiar modelo")
    print("  /admin  - Ver comandos de admin")

# ============================================
# MAIN INSTALLATION
# ============================================

def main():
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔─────────────────────────────────────────────────────╗
│                                                       │
│     {Colors.YELLOW}Claudio Bot{Colors.CYAN} - Instalador Interactivo        │
│     {Colors.GREEN}v4.6.1{Colors.CYAN} - Multi-Proveedor IA                │
│                                                       │
╚─────────────────────────────────────────────────────╝
{Colors.END}
""")

    print_info("Este instalador te guiará paso a paso en la configuración.")
    print_info("Presiona Ctrl+C en cualquier momento para cancelar.\n")

    try:
        # Step 1: Telegram
        telegram_config = step_telegram_config()
        if not telegram_config:
            print_error("Configuración de Telegram falló. Saliendo...")
            return 1

        # Step 2: AI Provider
        ai_config = step_ai_provider()

        # Step 3: n8n (Optional)
        n8n_config = step_n8n_config()

        # Step 4: Deployment Mode
        deploy_config = step_deployment_mode()

        # Step 5: Install Dependencies
        if not yes_no("¿Instalar dependencias Python ahora?", True):
            print_info("Puedes instalarlas manualmente con: pip install -r requirements.txt")
        else:
            step_install_dependencies()

        # Step 6: Create .env
        config = {**telegram_config, **ai_config, **n8n_config, **deploy_config}
        step_create_env_file(config)

        # Show summary
        show_summary(config)

        return 0

    except KeyboardInterrupt:
        print_error("\n\nInstalación cancelada por el usuario.")
        return 1
    except Exception as e:
        print_error(f"Error durante la instalación: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
