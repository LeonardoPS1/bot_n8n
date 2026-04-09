#!/usr/bin/env python3
"""
Claudio Bot - Interactive Installer
Installs and configures Claudio Bot with user prompts
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{bcolors.ENDC}\n")

def print_step(text):
    print(f"\n{bcolors.OKCYAN}➜ {text}{bcolors.ENDC}")

def print_success(text):
    print(f"{bcolors.OKGREEN}✓ {text}{bcolors.ENDC}")

def print_warning(text):
    print(f"{bcolors.WARNING}⚠ {text}{bcolors.ENDC}")

def print_error(text):
    print(f"{bcolors.FAIL}✗ {text}{bcolors.ENDC}")

def ask_yes_no(question, default=True):
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        response = input(f"{bcolors.OKBLUE}?{bcolors.ENDC} {question}{suffix}").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes', 'sí', 'si']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Por favor responde 'y' o 'n'")

def ask_choice(question, choices, default=0):
    print(f"{bcolors.OKBLUE}?{bcolors.ENDC} {question}")
    for i, choice in enumerate(choices):
        marker = f"{bcolors.OKGREEN}→{bcolors.ENDC}" if i == default else " "
        print(f"  {marker} {i+1}. {choice}")
    while True:
        response = input(f"Selecciona [1-{len(choices)}]: ").strip()
        if not response and default is not None:
            return default
        try:
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return idx
        except ValueError:
            pass
        print(f"Por favor ingresa un número entre 1 y {len(choices)}")

def ask_input(question, default="", required=False, password=False):
    prompt = f"{bcolors.OKBLUE}?{bcolors.ENDC} {question}"
    if default:
        prompt += f" [{default}]: "
    else:
        prompt += ": "
    while True:
        if password:
            import getpass
            response = getpass.getpass(prompt)
        else:
            response = input(prompt).strip()
        if not response and default:
            return default
        if required and not response:
            print("Este campo es requerido")
            continue
        return response

def check_python_version():
    print_step("Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error("Python 3.10+ es requerido")
        print(f"Versión actual: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print_success(f"Python {version.major}.{version.minor}.{version.micro} encontrado")

def check_pip():
    print_step("Verificando pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                      capture_output=True, check=True)
        print_success("pip disponible")
    except subprocess.CalledProcessError:
        print_error("pip no encontrado")
        sys.exit(1)

def install_dependencies():
    print_step("Instalando dependencias de Python...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)
        print_success("Dependencias instaladas")
    except subprocess.CalledProcessError:
        print_error("Error instalando dependencias")
        sys.exit(1)

def create_venv():
    print_step("Creando entorno virtual...")
    venv_path = Path("venv")
    if venv_path.exists():
        if not ask_yes_no("El entorno virtual ya existe. ¿Recrear?", False):
            print_success("Usando entorno virtual existente")
            return
        shutil.rmtree(venv_path)

    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print_success("Entorno virtual creado")

def setup_telegram():
    print_header("CONFIGURACIÓN DE TELEGRAM")

    print("\n📱 Para configurar el bot de Telegram necesitas:")
    print("   1. Un token de @BotFather")
    print("   2. Tu ID de usuario de Telegram")

    print("\n🔹 Obtén tu token:")
    print("   1. Abre Telegram y busca @BotFather")
    print("   2. Envía /newbot")
    print("   3. Sigue las instrucciones")
    print("   4. Copia el token que te dan")

    telegram_token = ask_input("Token de Telegram", required=True, password=True)

    print("\n🔹 Obtén tu ID de usuario:")
    print("   1. Abre Telegram y busca @userinfobot")
    print("   2. Envía cualquier mensaje")
    print("   3. Copia tu ID (número)")

    user_id = ask_input("Tu ID de usuario de Telegram", required=True)

    allowed_users = ask_input("IDs de usuarios permitidos (separados por coma)", default=user_id)

    return {
        "TELEGRAM_TOKEN": telegram_token,
        "ALLOWED_USERS": allowed_users,
        "ALLOWED_ADMIN_USERS": user_id
    }

def setup_ai_provider():
    print_header("CONFIGURACIÓN DE PROVEEDOR DE IA")

    providers = [
        "OpenAI (GPT-4, GPT-4o)",
        "Anthropic (Claude)",
        "Ollama (Local, gratuito)",
        "Multi-proveedor (con fallback automático)"
    ]

    choice = ask_choice("Selecciona el proveedor de IA principal:", providers)

    ai_configs = {}

    if choice == 0:  # OpenAI
        print("\n📘 OpenAI - Configuración")
        print("   1. Ve a https://platform.openai.com/api-keys")
        print("   2. Crea una nueva API key")
        print("   3. Copia la key")

        api_key = ask_input("API Key de OpenAI", required=True, password=True)
        model = ask_input("Modelo", default="gpt-4o")

        ai_configs = {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": api_key,
            "OPENAI_MODEL": model
        }

    elif choice == 1:  # Anthropic
        print("\n📘 Anthropic - Configuración")
        print("   1. Ve a https://console.anthropic.com/")
        print("   2. Ve a API Keys")
        print("   3. Crea una nueva key")

        api_key = ask_input("API Key de Anthropic", required=True, password=True)
        model = ask_input("Modelo", default="claude-sonnet-4-20250514")

        ai_configs = {
            "AI_PROVIDER": "anthropic",
            "ANTHROPIC_API_KEY": api_key,
            "ANTHROPIC_MODEL": model
        }

    elif choice == 2:  # Ollama
        print("\n📘 Ollama - Configuración")
        print("   Ollama ejecuta modelos localmente (gratis)")
        print("   Asegúrate de tener Ollama instalado")

        base_url = ask_input("URL de Ollama", default="http://localhost:11434")
        model = ask_input("Modelo", default="phi3:mini")

        ai_configs = {
            "AI_PROVIDER": "ollama",
            "OLLAMA_BASE_URL": base_url,
            "OLLAMA_MODEL": model
        }

    else:  # Multi
        print("\n📘 Multi-proveedor - Configuración")
        print("   Configura múltiples proveedores con fallback automático")

        primary = ask_choice("Proveedor primario:", providers[:3])
        fallback_order = []

        for i in range(3):
            if i != primary:
                if ask_yes_no(f"¿Añadir {providers[i]} como fallback?", i == (primary + 1) % 3):
                    fallback_order.append(['openai', 'anthropic', 'ollama'][i])

        ai_configs["AI_PROVIDER"] = "multi"
        ai_configs["AUTO_FALLBACK"] = "true"
        ai_configs["FALLBACK_ORDER"] = ",".join(['openai', 'anthropic', 'ollama'][i] for i in [primary] + fallback_order)

        # Ask for keys for selected providers
        if primary == 0 or 0 in fallback_order:
            api_key = ask_input("API Key de OpenAI (dejar vacío para omitir)", password=True)
            if api_key:
                ai_configs["OPENAI_API_KEY"] = api_key
                ai_configs["OPENAI_MODEL"] = ask_input("Modelo OpenAI", default="gpt-4o")

        if primary == 1 or 1 in fallback_order:
            api_key = ask_input("API Key de Anthropic (dejar vacío para omitir)", password=True)
            if api_key:
                ai_configs["ANTHROPIC_API_KEY"] = api_key
                ai_configs["ANTHROPIC_MODEL"] = ask_input("Modelo Anthropic", default="claude-sonnet-4-20250514")

        if primary == 2 or 2 in fallback_order:
            base_url = ask_input("URL de Ollama", default="http://localhost:11434")
            ai_configs["OLLAMA_BASE_URL"] = base_url
            ai_configs["OLLAMA_MODEL"] = ask_input("Modelo Ollama", default="phi3:mini")

    return ai_configs

def setup_n8n():
    print_header("CONFIGURACIÓN DE N8N")

    if not ask_yes_no("¿Tienes una instancia de n8n configurada?", True):
        print_warning("Sin n8n, el bot solo podrá responder preguntas pero no crear workflows")
        return {}

    print("\n📘 n8n - Configuración")
    print("   1. Abre tu instancia de n8n")
    print("   2. Ve a Settings → API")
    print("   3. Crea una nueva API key")
    print("   4. Copia la key y la URL de tu instancia")

    api_key = ask_input("API Key de n8n", required=True, password=True)
    instance_url = ask_input("URL de tu instancia n8n", default="https://n8n.example.com")

    # Extract host header from URL
    from urllib.parse import urlparse
    parsed = urlparse(instance_url)
    host_header = parsed.netloc

    return {
        "N8N_API_KEY": api_key,
        "N8N_INSTANCE_URL": instance_url,
        "N8N_HOST_HEADER": host_header
    }

def setup_server():
    print_header("CONFIGURACIÓN DEL SERVIDOR")

    port = ask_input("Puerto del servidor Claudio", default="8001")
    timeout = ask_input("Timeout para requests (segundos)", default="60")

    return {
        "CLADIO_PORT": port,
        "CLADIO_SERVER_URL": f"http://localhost:{port}",
        "REQUEST_TIMEOUT": timeout
    }

def create_env_file(config):
    print_step("Creando archivo .env...")

    env_content = "# Claudio Bot - Environment Configuration\n"
    env_content += "# Generated by install.py\n\n"

    for key, value in config.items():
        if value is None:
            continue
        env_content += f"{key}={value}\n"

    with open(".env", "w") as f:
        f.write(env_content)

    print_success("Archivo .env creado")

def create_systemd_service():
    print_step("Creando servicios systemd...")

    user = os.getenv("USER", "ubuntu")
    project_dir = os.path.abspath(".")

    # Claudio Server service
    server_service = f"""[Unit]
Description=Claudio AI Server
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={project_dir}
Environment="PATH={project_dir}/venv/bin"
ExecStart={project_dir}/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    # Telegram Bot service
    bot_service = f"""[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User={user}
WorkingDirectory={project_dir}
Environment="PATH={project_dir}/venv/bin"
ExecStart={project_dir}/venv/bin/python bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    with open("claudio-server.service", "w") as f:
        f.write(server_service)
    with open("claudio-telegram-bot.service", "w") as f:
        f.write(bot_service)

    print_success("Archivos de servicio creados")

    print_warning("Para instalar los servicios systemd, ejecuta:")
    print("   sudo cp claudio-*.service /etc/systemd/system/")
    print("   sudo systemctl daemon-reload")
    print("   sudo systemctl enable claudio-server claudio-telegram-bot")
    print("   sudo systemctl start claudio-server claudio-telegram-bot")

def print_next_steps():
    print_header("PRÓXIMOS PASOS")

    print(f"\n{bcolors.OKGREEN}¡Instalación completada!{bcolors.ENDC}\n")

    print("📋 Para iniciar el bot:")
    print("   Local: python start.py")
    print("   VPS: sudo systemctl start claudio-telegram-bot")

    print("\n📱 En Telegram:")
    print("   1. Abre tu bot")
    print("   2. Envía /start")
    print("   3. Explora los comandos disponibles")

    print("\n📖 Documentación:")
    print("   README.md - Visión general")
    print("   GUIDE.md - Guía de usuario completa")
    print("   API.md - Documentación de la API")

    print("\n🐛 ¿Problemas?")
    print("   Revisa la sección de Solución de Problemas en GUIDE.md")
    print("   Reporta issues en GitHub")

def main():
    print_header("🤖 CLAUDIO BOT - INSTALADOR INTERACTIVO")
    print("Este instalador te guiará paso a paso en la configuración")
    print("de Claudio Bot, tu asistente experto de n8n en Telegram.\n")

    # Check Python version
    check_python_version()
    check_pip()

    # Create virtual environment
    if ask_yes_no("¿Crear entorno virtual?", True):
        create_venv()
        # Use venv python
        venv_python = Path("venv/bin/python")
        if venv_python.exists():
            print_success("Usando entorno virtual")
            print_warning("Reinicia el instalador con el entorno virtual activo:")
            print("   source venv/bin/activate  # Linux/Mac")
            print("   venv\\Scripts\\activate   # Windows")
            return

    # Install dependencies
    install_dependencies()

    # Setup configurations
    config = {}

    # Telegram
    telegram_config = setup_telegram()
    config.update(telegram_config)

    # AI Provider
    ai_config = setup_ai_provider()
    config.update(ai_config)

    # n8n
    n8n_config = setup_n8n()
    config.update(n8n_config)

    # Server
    server_config = setup_server()
    config.update(server_config)

    # Create .env file
    create_env_file(config)

    # Create systemd services (optional)
    if ask_yes_no("\n¿Crear servicios systemd?", False):
        create_systemd_service()

    # Print next steps
    print_next_steps()

    print(f"\n{bcolors.OKGREEN}¡Claudio Bot está listo para usar!{bcolors.ENDC}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{bcolors.WARNING}Instalación cancelada por el usuario{bcolors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{bcolors.FAIL}Error: {e}{bcolors.ENDC}")
        sys.exit(1)
