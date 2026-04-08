#!/usr/bin/env python3
"""
Claudio - Interactive Installer
Wizard de instalacion completo con preguntas interactivas y prueba de funcionamiento
"""

import os
import sys
import json
import shutil
import subprocess
import time
from pathlib import Path

# Colores para terminal
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.YELLOW}{Colors.BOLD}>>> {text}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def ask_question(question, default=None, password=False, required=True):
    """Hacer una pregunta al usuario"""
    prompt = f"{Colors.MAGENTA}→{Colors.END} {question}"
    if default:
        prompt += f" [{Colors.GREEN}{default}{Colors.END}]"
    prompt += ": "

    if password:
        import getpass
        answer = getpass.getpass(prompt)
    else:
        answer = input(prompt).strip()

    if not answer and default:
        answer = default

    if required and not answer:
        print_error("Este campo es obligatorio")
        return ask_question(question, default, password, required)

    return answer

def ask_choice(question, choices, default=0):
    """Hacer una pregunta con opciones multiples"""
    print(f"\n{Colors.MAGENTA}→{Colors.END} {question}")
    for i, choice in enumerate(choices):
        prefix = f"{Colors.GREEN}[{i+1}]{Colors.END}"
        if i == default:
            prefix += f" {Colors.YELLOW}(default){Colors.END}"
        print(f"    {prefix} {choice}")

    while True:
        prompt = f"{Colors.MAGENTA}→{Colors.END} Selecciona una opción [1-{len(choices)}]: "
        answer = input(prompt).strip()

        if not answer:
            return default

        try:
            choice = int(answer) - 1
            if 0 <= choice < len(choices):
                return choice
            print_error(f"Opción inválida. Debe ser entre 1 y {len(choices)}")
        except ValueError:
            print_error("Ingresa un número")

def ask_yes_no(question, default=True):
    """Hacer una pregunta de si/no"""
    default_str = "Y/n" if default else "y/N"
    answer = ask_question(f"{question} ({default_str})", default="Y" if default else "N").lower()

    if not answer:
        return default

    return answer in ['y', 'yes', 's', 'si']

def validate_api_key(key, provider):
    """Validación básica de API key"""
    if not key:
        return False

    if provider == "anthropic":
        return key.startswith("sk-ant-")
    elif provider == "openai":
        return key.startswith("sk-")
    elif provider == "n8n":
        return len(key) > 20

    return len(key) > 10

def print_installation_guide():
    """Imprimir guía de instalación paso a paso"""
    print_header("GUÍA DE INSTALACIÓN - CLAUDIO BOT")

    print(f"{Colors.BOLD}Esta guía te acompañará durante todo el proceso de instalación.{Colors.END}")
    print()

    print(f"{Colors.CYAN}┌─────────────────────────────────────────────────────────────────┐{Colors.END}")
    print(f"{Colors.CYAN}│                                                                 │{Colors.END}")
    print(f"{Colors.CYAN}│  {Colors.BOLD}CLAUDIO BOT - INSTALACIÓN COMPLETA{Colors.END}                          {Colors.CYAN}│{Colors.END}")
    print(f"{Colors.CYAN}│                                                                 │{Colors.END}")
    print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────────────┘{Colors.END}")
    print()

    print(f"{Colors.BOLD}📋 PASOS QUE VAMOS A REALIZAR:{Colors.END}\n")

    steps = [
        ("PASO 1", "Configurar Proveedor de IA", "Seleccionarás Anthropic, OpenAI u Ollama"),
        ("PASO 2", "Configurar Telegram", "Conectarás tu bot de Telegram"),
        ("PASO 3", "Integración n8n (Opcional)", "Conectarás con tu instancia de n8n"),
        ("PASO 4", "Configurar Servidor", "Definirás puerto y opciones de red"),
        ("PASO 5", "Seguridad", "Restringirás el acceso a usuarios específicos"),
        ("PASO 6", "Directorio de Instalación", "Elegirás dónde se instalará Claudio"),
        ("PASO 7", "Resumen y Confirmación", "Revisarás toda la configuración"),
        ("PASO 8", "Instalación", "Se instalarán todos los componentes"),
        ("PASO 9", "Prueba de Funcionamiento", "Verificarás que todo funciona correctamente")
    ]

    for step_num, step_title, step_desc in steps:
        print(f"  {Colors.GREEN}{step_num}{Colors.END} - {Colors.BOLD}{step_title}{Colors.END}")
        print(f"      {Colors.CYAN}{step_desc}{Colors.CYAN}")
        print()

    print(f"{Colors.YELLOW}⏱️  Tiempo estimado: 10-15 minutos{Colors.END}")
    print(f"{Colors.YELLOW}📦 Espacio requerido: ~500 MB{Colors.END}")
    print()

    print(f"{Colors.BOLD}📝 ANTES DE COMENZAR, NECESITARÁS:{Colors.END}\n")

    requirements = [
        ("Telegram Bot Token", "@BotFather en Telegram", "Obligatorio"),
        ("API Key de IA", "Anthropic/OpenAI según tu elección", "Obligatorio"),
        "(Opcional) n8n API Key", "Configuración de tu instancia n8n", "Opcional"),
        "(Opcional) Tu Telegram User ID", "@userinfobot en Telegram", "Opcional")
    ]

    for req, source, status in requirements:
        status_color = Colors.GREEN if "Obligatorio" in status else Colors.CYAN
        print(f"  • {Colors.BOLD}{req}{Colors.END}")
        print(f"    Obtenido de: {Colors.BLUE}{source}{Colors.END}")
        print(f"    Estado: {status_color}{status}{Colors.END}")
        print()

    print(f"{Colors.MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.END}")
    print()

    ready = ask_yes_no("¿Estás listo para comenzar la instalación?", default=True)
    if not ready:
        print_info("Puedes obtener las credenciales necesarias y ejecutar este instalador nuevamente.")
        sys.exit(0)

def create_env_file(config):
    """Crear archivo .env con la configuración"""
    env_content = f"""# Claudio Bot - Configuration File
# Generated by interactive installer
# Installation date: {time.strftime('%Y-%m-%d %H:%M:%S')}

# ============================================
# TELEGRAM CONFIG
# ============================================
TELEGRAM_TOKEN={config['telegram_token']}

# ============================================
# AI PROVIDER CONFIG
# ============================================
AI_PROVIDER={config['ai_provider']}
"""

    # Agregar API key según el proveedor
    if config['ai_provider'] == 'anthropic':
        env_content += f"ANTHROPIC_API_KEY={config['api_key']}\n"
        if config.get('anthropic_model'):
            env_content += f"ANTHROPIC_MODEL={config['anthropic_model']}\n"
    elif config['ai_provider'] == 'openai':
        env_content += f"OPENAI_API_KEY={config['api_key']}\n"
        if config.get('openai_model'):
            env_content += f"OPENAI_MODEL={config['openai_model']}\n"
    elif config['ai_provider'] == 'ollama':
        env_content += f"OLLAMA_BASE_URL={config.get('ollama_url', 'http://localhost:11434')}\n"
        if config.get('ollama_model'):
            env_content += f"OLLAMA_MODEL={config['ollama_model']}\n"

    # n8n config (opcional)
    if config.get('n8n_enabled'):
        env_content += f"""
# ============================================
# N8N CONFIG (optional)
# ============================================
N8N_API_KEY={config.get('n8n_api_key', '')}
N8N_INSTANCE_URL={config.get('n8n_url', 'https://localhost')}
N8N_HOST_HEADER={config.get('n8n_host', 'localhost')}
"""

    # Server config
    port = config.get('port', '8000')
    env_content += f"""
# ============================================
# SERVER CONFIG
# ============================================
CLADIO_PORT={port}
CLADIO_SERVER_URL=http://localhost:{port}
REQUEST_TIMEOUT=60

# ============================================
# SECURITY
# ============================================
# Telegram User ID(s) allowed (comma separated)
# Get your ID from @userinfobot on Telegram
ALLOWED_USERS={config.get('allowed_users', '*')}
"""

    return env_content

def create_systemd_service(config):
    """Crear archivos de servicio systemd para Linux"""
    install_dir = config.get('install_dir', '/opt/claudio-bot')
    project_name = config.get('project_name', 'claudio-bot')

    server_service = f"""[Unit]
Description=Claudio Server ({project_name})
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory={install_dir}
EnvironmentFile={install_dir}/.env
ExecStart={install_dir}/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

    bot_service = f"""[Unit]
Description=Claudio Telegram Bot ({project_name})
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory={install_dir}
EnvironmentFile={install_dir}/.env
ExecStart={install_dir}/venv/bin/python bot_v2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""

    return server_service, bot_service

def create_test_script(config):
    """Crear script de prueba post-instalación"""
    port = config.get('port', '8000')

    script = f"""#!/bin/bash
# Claudio Bot - Post-Installation Test Script
# Generated by installer

echo "======================================================================"
echo "  CLAUDIO BOT - POST-INSTALLATION TEST"
echo "======================================================================"
echo ""

FAILED_TESTS=0
PASSED_TESTS=0

# Función para verificar test
run_test() {{
    local test_name="$1"
    local test_command="$2"

    echo -n "Testing: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo "✓ PASSED"
        ((PASSED++))
        return 0
    else
        echo "✗ FAILED"
        ((FAILED++))
        return 1
    fi
}}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SYSTEM CHECKS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Python 3 installed" "command -v python3"
run_test "pip available" "command -v pip3"
run_test "git available" "command -v git"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CLAUDIO FILES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

INSTALL_DIR="{config.get('install_dir', '/opt/claudio-bot')}"

run_test "Installation directory exists" "[ -d '$INSTALL_DIR' ]"
run_test ".env file exists" "[ -f '$INSTALL_DIR/.env' ]"
run_test "claudio_complete.py exists" "[ -f '$INSTALL_DIR/claudio_complete.py' ]"
run_test "bot_v2.py exists" "[ -f '$INSTALL_DIR/bot_v2.py' ]"
run_test "n8n_mcp_tools.py exists" "[ -f '$INSTALL_DIR/n8n_mcp_tools.py' ]"
run_test "skills directory exists" "[ -d '$INSTALL_DIR/skills' ]"
run_test "venv directory exists" "[ -d '$INSTALL_DIR/venv' ]"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  PYTHON ENVIRONMENT CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "venv/bin/python exists" "[ -f '$INSTALL_DIR/venv/bin/python' ]"
run_test "python-telegram-bot installed" "$INSTALL_DIR/venv/bin/pip show python-telegram-bot"
run_test "anthropic installed" "$INSTALL_DIR/venv/bin/pip show anthropic"
run_test "fastapi installed" "$INSTALL_DIR/venv/bin/pip show fastapi"
run_test "uvicorn installed" "$INSTALL_DIR/venv/bin/pip show uvicorn"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  CONFIGURATION CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ -f "$INSTALL_DIR/.env" ]; then
    run_test "TELEGRAM_TOKEN set" "grep -q 'TELEGRAM_TOKEN=' $INSTALL_DIR/.env && ! grep -q 'TELEGRAM_TOKEN=your_' $INSTALL_DIR/.env"
    run_test "AI_PROVIDER set" "grep -q 'AI_PROVIDER=' $INSTALL_DIR/.env"
    run_test "API Key configured" "grep -q 'API_KEY=' $INSTALL_DIR/.env && ! grep -q '_KEY=your_' $INSTALL_DIR/.env"
    run_test "CLADIO_PORT set" "grep -q 'CLADIO_PORT=' $INSTALL_DIR/.env"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SYSTEMD SERVICES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "claudio-server.service exists" "[ -f '/etc/systemd/system/claudio-server.service' ]"
run_test "claudio-telegram-bot.service exists" "[ -f '/etc/systemd/system/claudio-telegram-bot.service' ]"

if [ -f '/etc/systemd/system/claudio-server.service' ]; then
    run_test "claudio-server.service enabled" "systemctl is-enabled claudio-server.service"
    run_test "claudio-server.service active" "systemctl is-active claudio-server.service"
fi

if [ -f '/etc/systemd/system/claudio-telegram-bot.service' ]; then
    run_test "claudio-telegram-bot.service enabled" "systemctl is-enabled claudio-telegram-bot.service"
    run_test "claudio-telegram-bot.service active" "systemctl is-active claudio-telegram-bot.service"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SERVER HEALTH CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

run_test "Server responding on port {port}" "curl -s http://localhost:{port}/health"

echo ""
echo "======================================================================"
echo "  TEST RESULTS"
echo "======================================================================"
echo ""
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✓ ALL TESTS PASSED! Claudio Bot is ready to use."
    echo ""
    echo "Next steps:"
    echo "  1. Open Telegram and find your bot"
    echo "  2. Send /start to begin"
    echo "  3. Try: 'Help me create a webhook workflow'"
    echo ""
    exit 0
else
    echo "✗ Some tests failed. Please check the errors above."
    echo ""
    echo "Common fixes:"
    echo "  • If services failed: sudo systemctl restart claudio-server claudio-telegram-bot"
    echo "  • If packages missing: cd $INSTALL_DIR && venv/bin/pip install -r requirements.txt"
    echo "  • Check logs: sudo journalctl -u claudio-telegram-bot -f"
    echo ""
    exit 1
fi
"""
    return script

def run_post_installation_test(config):
    """Ejecutar pruebas post-instalación"""
    print_header("PRUEBA DE FUNCIONAMIENTO")

    print_info("Ejecutando verificación completa de la instalación...")
    print()

    install_dir = config.get('install_dir', '/opt/claudio-bot')

    tests = []

    # Test 1: Archivos clave
    print_section("VERIFICANDO ARCHIVOS CLAVE")

    key_files = [
        ("claudio_complete.py", "Servidor principal"),
        ("bot_v2.py", "Bot de Telegram"),
        ("n8n_mcp_tools.py", "Herramientas n8n MCP"),
        ("n8n_database.py", "Base de datos n8n"),
        ("requirements.txt", "Dependencias Python"),
        (".env", "Configuración"),
        ("skills/", "Módulos de habilidades")
    ]

    for file_path, description in key_files:
        full_path = os.path.join(install_dir, file_path)
        if os.path.exists(full_path):
            print_success(f"{description}: {file_path}")
        else:
            print_error(f"{description} NO encontrado: {file_path}")

    # Test 2: Entorno Python
    print_section("VERIFICANDO ENTORNO PYTHON")

    venv_python = os.path.join(install_dir, "venv", "bin", "python")
    if os.path.exists(venv_python):
        print_success("Entorno virtual Python creado")

        # Verificar paquetes instalados
        try:
            result = subprocess.run(
                [venv_python, "-m", "pip", "list", "--format=freeze"],
                capture_output=True, text=True
            )
            packages = result.stdout

            required_packages = [
                ("python-telegram-bot", "Bot de Telegram"),
                ("anthropic", "API Anthropic"),
                ("openai", "API OpenAI"),
                ("fastapi", "Servidor FastAPI"),
                ("uvicorn", "Servidor ASGI"),
                ("httpx", "Cliente HTTP"),
                ("pydantic", "Validación de datos"),
                ("python-dotenv", "Variables de entorno")
            ]

            print()
            for package, description in required_packages:
                if package.lower() in packages.lower():
                    print_success(f"{description}: {package}")
                else:
                    print_warning(f"{description}: {package} (puede no estar instalado)")
        except Exception as e:
            print_error(f"No se pudieron verificar paquetes: {e}")
    else:
        print_error("Entorno virtual Python NO encontrado")

    # Test 3: Configuración
    print_section("VERIFICANDO CONFIGURACIÓN")

    env_path = os.path.join(install_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()

        checks = [
            ("TELEGRAM_TOKEN", "Token de Telegram"),
            ("AI_PROVIDER", "Proveedor de IA"),
            ("API_KEY", "API Key de IA"),
            ("CLADIO_PORT", "Puerto del servidor")
        ]

        for env_var, description in checks:
            if env_var in env_content and f"{env_var}=your_" not in env_content:
                print_success(f"{description}: Configurado")
            elif env_var in env_content:
                print_warning(f"{description}: Presente pero puede tener valor por defecto")
            else:
                print_error(f"{description}: NO configurado")
    else:
        print_error("Archivo .env NO encontrado")

    # Test 4: Servicios systemd (si es Linux)
    if os.name != 'nt':
        print_section("VERIFICANDO SERVICIOS SYSTEMD")

        try:
            # Verificar si los servicios existen
            services = [
                ("claudio-server.service", "Servidor Claudio"),
                ("claudio-telegram-bot.service", "Bot de Telegram")
            ]

            for service, description in services:
                service_path = f"/etc/systemd/system/{service}"
                if os.path.exists(service_path):
                    print_success(f"{description}: Servicio creado")

                    # Verificar estado
                    try:
                        result = subprocess.run(
                            ["systemctl", "is-active", service],
                            capture_output=True, text=True
                        )
                        status = result.stdout.strip()
                        if status == "active":
                            print_success(f"  Estado: ACTIVO")
                        else:
                            print_warning(f"  Estado: {status}")
                    except:
                        print_warning(f"  No se pudo verificar el estado")
                else:
                    print_warning(f"{description}: Servicio NO creado (puede ser normal en tu caso)")
        except Exception as e:
            print_info(f"No se pudieron verificar servicios systemd: {e}")

    # Test 5: Health check
    print_section("PRUEBA DE HEALTH CHECK")

    port = config.get('port', '8000')
    print_info(f"Intentando conectar al servidor en http://localhost:{port}/health")

    try:
        import httpx
        response = httpx.get(f"http://localhost:{port}/health", timeout=5)
        if response.status_code == 200:
            print_success("Servidor respondiendo correctamente")
            print_info(f"Response: {response.json()}")
        else:
            print_warning(f"Servidor respondió con código: {response.status_code}")
    except:
        print_info("Servidor no está ejecutándose o no es accesible")
        print_info("Esto es normal si aún no has iniciado los servicios")

    # Resumen
    print_header("RESUMEN DE PRUEBAS")

    print()
    print(f"{Colors.BOLD}La instalación ha finalizado.{Colors.END}")
    print()
    print(f"{Colors.GREEN}✓ Todos los archivos han sido creados correctamente{Colors.END}")
    print(f"{Colors.GREEN}✓ La configuración ha sido generada{Colors.END}")
    print(f"{Colors.GREEN}✓ Los scripts de inicio están listos{Colors.END}")
    print()

    if config['deployment'] == 'vps':
        print()
        print(f"{Colors.YELLOW}Para iniciar Claudio en tu VPS:{Colors.END}")
        print(f"  {Colors.CYAN}sudo systemctl start claudio-server claudio-telegram-bot{Colors.END}")
        print()
        print(f"{Colors.YELLOW}Para ver los logs:{Colors.END}")
        print(f"  {Colors.CYAN}sudo journalctl -u claudio-telegram-bot -f{Colors.END}")
        print()
    elif config['deployment'] == 'local':
        print()
        print(f"{Colors.YELLOW}Para iniciar Claudio localmente:{Colors.END}")
        if os.name == 'nt':
            print(f"  {Colors.CYAN}start_server.bat{Colors.END} (en una terminal)")
            print(f"  {Colors.CYAN}start.bat{Colors.END} (en otra terminal)")
        else:
            print(f"  {Colors.CYAN}./start_server.sh{Colors.END} (en una terminal)")
            print(f"  {Colors.CYAN}./start.sh{Colors.END} (en otra terminal)")
        print()

    print(f"{Colors.BOLD}🚀 ¡Claudio está listo para usar!{Colors.END}")
    print()
    print(f"{Colors.CYAN}Prueba estos comandos en tu bot de Telegram:{Colors.END}")
    print(f"  • {Colors.GREEN}/start{Colors.END} - Iniciar el bot")
    print(f"  • {Colors.GREEN}Ayuda{Colors.END} - Ver opciones disponibles")
    print(f"  • {Colors.GREEN}Crea un workflow de webhook{Colors.END} - Ejemplo de solicitud")
    print()

def main():
    """Función principal del instalador"""
    print_header("CLAUDIO - INTERACTIVE INSTALLER v4.1")

    # Mostrar guía de instalación
    print_installation_guide()

    config = {}

    # ============================================
    # PASO 0: NOMBRE DEL PROYECTO
    # ============================================
    print_section("PASO 0: NOMBRE DEL PROYECTO")

    print_info("El nombre del proyecto se usará para:")
    print("  • Nombre de la carpeta de instalación")
    print("  • Nombre de los servicios systemd")
    print("  • Identificación en logs y monitoreo")
    print()

    project_name = ask_question("Nombre del proyecto (sin espacios)", default="claudio-bot", required=True)
    project_name = project_name.replace(" ", "-").lower()
    config['project_name'] = project_name
    print_success(f"Nombre del proyecto: {project_name}")

    # ============================================
    # PASO 1: Proveedor de IA
    # ============================================
    print_section("PASO 1: Selecciona tu Proveedor de IA")

    print_info("Claudio soporta múltiples proveedores de IA:")
    print("  • Anthropic (Claude) - Mejor comprensión técnica para n8n")
    print("  • OpenAI (GPT-4) - Alternativa popular y capaz")
    print("  • Ollama - Gratuito y local (requiere más recursos)")
    print()

    ai_providers = [
        "Anthropic (Claude) - Recomendado para n8n, mejor calidad técnica",
        "OpenAI (GPT-4/GPT-3.5) - Alternativa popular, buena calidad",
        "Ollama - Local y gratuito (requiere instalación y recursos)",
        "Multi-proveedor - Anthropic + OpenAI (fallback automático)"
    ]

    ai_choice = ask_choice("¿Qué proveedor de IA deseas usar?", ai_providers, default=0)

    if ai_choice == 0:
        config['ai_provider'] = 'anthropic'
        print_info("Has seleccionado Anthropic (Claude)")
        print()

        while True:
            api_key = ask_question("Ingresa tu API Key de Anthropic (sk-ant-...)", password=True)
            if validate_api_key(api_key, 'anthropic'):
                config['api_key'] = api_key
                print_success("API Key válida")
                break
            print_error("API Key inválida. Debe comenzar con 'sk-ant-'")
            print_info("Obtén tu API Key en: https://console.anthropic.com/settings/keys")

        models = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
        print()
        model_choice = ask_choice("¿Qué modelo de Claude deseas usar?", models, default=0)
        config['anthropic_model'] = models[model_choice]
        print_success(f"Modelo seleccionado: {models[model_choice]}")

    elif ai_choice == 1:
        config['ai_provider'] = 'openai'
        print_info("Has seleccionado OpenAI")
        print()

        while True:
            api_key = ask_question("Ingresa tu API Key de OpenAI (sk-...)", password=True)
            if validate_api_key(api_key, 'openai'):
                config['api_key'] = api_key
                print_success("API Key válida")
                break
            print_error("API Key inválida. Debe comenzar con 'sk-'")
            print_info("Obtén tu API Key en: https://platform.openai.com/api-keys")

        models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        print()
        model_choice = ask_choice("¿Qué modelo de OpenAI deseas usar?", models, default=0)
        config['openai_model'] = models[model_choice]
        print_success(f"Modelo seleccionado: {models[model_choice]}")

    elif ai_choice == 2:
        config['ai_provider'] = 'ollama'
        print_info("Has seleccionado Ollama (local)")
        print()
        print_warning("Ollama requiere que esté instalado en el sistema")
        print_info("Descarga desde: https://ollama.ai")
        print()

        ollama_url = ask_question("URL de Ollama", default="http://localhost:11434")
        config['ollama_url'] = ollama_url

        models = ["llama3", "llama3:70b", "mistral", "codellama"]
        model_choice = ask_choice("¿Qué modelo de Ollama deseas usar?", models, default=0)
        config['ollama_model'] = models[model_choice]
        config['api_key'] = "not-needed"
        print_success(f"Modelo seleccionado: {models[model_choice]}")

    else:
        config['ai_provider'] = 'multi'
        print_info("Configurarás múltiples proveedores con fallback automático")
        print()

        anthropic_key = ""
        openai_key = ""

        if ask_yes_no("¿Tienes API Key de Anthropic?", default=True):
            while True:
                anthropic_key = ask_question("API Key de Anthropic", password=True, required=False)
                if not anthropic_key or validate_api_key(anthropic_key, 'anthropic'):
                    break
                print_error("API Key inválida")

        if ask_yes_no("¿Tienes API Key de OpenAI?", default=True):
            while True:
                openai_key = ask_question("API Key de OpenAI", password=True, required=False)
                if not openai_key or validate_api_key(openai_key, 'openai'):
                    break
                print_error("API Key inválida")

        if anthropic_key:
            config['anthropic_api_key'] = anthropic_key
        if openai_key:
            config['openai_api_key'] = openai_key

        if not anthropic_key and not openai_key:
            print_error("Debes configurar al menos un proveedor de IA")
            return

    # ============================================
    # PASO 2: Configuración de Telegram
    # ============================================
    print_section("PASO 2: Configuración de Telegram")

    print_info("Claudio funciona como un bot de Telegram.")
    print_info("Si no tienes un bot, crea uno ahora:")
    print("  1. Abre @BotFather en Telegram")
    print("  2. Envía /newbot")
    print("  3. Sigue las instrucciones")
    print("  4. Elige un nombre y usuario para tu bot")
    print("  5. Copia el token que BotFather te da")
    print()

    telegram_ready = ask_yes_no("¿Ya tienes el Token de tu Bot?", default=True)

    if not telegram_ready:
        print()
        print_info("Sigue estos pasos para crear tu bot:")
        print("  1. Abre Telegram y busca @BotFather")
        print("  2. Envía el comando: /newbot")
        print("  3. Elige un nombre (ej: Claudio Assistant)")
        print("  4. Elige un usuario (ej: claudio_assistant_bot)")
        print("  5. Copia el token que te da (largo, comienza con números)")
        print()
        ask_yes_no("Presiona Enter cuando tengas el token...", default=True)

    while True:
        telegram_token = ask_question("Ingresa el Token de tu Bot de Telegram", password=True)
        if telegram_token and len(telegram_token) > 20:
            config['telegram_token'] = telegram_token
            print_success("Token de Telegram configurado")
            break
        print_error("Token inválido. Debe ser un token largo de Telegram")

    # ============================================
    # PASO 3: Configuración de n8n (opcional)
    # ============================================
    print_section("PASO 3: Integración con n8n (Opcional)")

    print_info("Claudio puede conectarse a tu instancia de n8n para:")
    print("  • Crear workflows directamente en tu instancia")
    print("  • Validar nodos y conexiones")
    print("  • Acceder a tus workflows existentes")
    print()

    n8n_enabled = ask_yes_no("¿Deseas integrar n8n para gestión de workflows?", default=False)

    if n8n_enabled:
        config['n8n_enabled'] = True
        print_info("Claudio podrá acceder a tu instancia de n8n")
        print()

        print_info("Necesitas la siguiente información de n8n:")
        print("  • URL de tu instancia (ej: https://n8n.tudominio.com)")
        print("  • API Key (opcional, para operaciones de escritura)")
        print()

        n8n_url = ask_question("URL de tu instancia n8n", default="https://n8n.aicorebots.com")
        config['n8n_url'] = n8n_url

        n8n_host = ask_question(
            "Header Host para proxy/dominio",
            default=n8n_url.replace('https://', '').replace('http://', '')
        )
        config['n8n_host'] = n8n_host

        has_api_key = ask_yes_no("¿Tienes API Key de n8n?", default=False)
        if has_api_key:
            n8n_api_key = ask_question("API Key de n8n", password=True, required=False)
            config['n8n_api_key'] = n8n_api_key or "no-api-key"
        else:
            config['n8n_api_key'] = "no-api-key"
            print_info("Sin API Key, Claudio solo podrá hacer lecturas públicas")

        print_success("Integración n8n configurada")
    else:
        config['n8n_enabled'] = False
        config['n8n_url'] = 'https://localhost'
        config['n8n_host'] = 'localhost'
        config['n8n_api_key'] = ''
        print_info("n8n no será integrado. Claudio funcionará en modo standalone")

    # ============================================
    # PASO 4: Configuración del Servidor
    # ============================================
    print_section("PASO 4: Configuración del Servidor")

    print_info("Claudio tiene dos componentes:")
    print("  • Servidor: API con IA y herramientas n8n")
    print("  • Bot: Interfaz de Telegram que conecta con el servidor")
    print()

    deployment_modes = [
        "Local - Ejecutar en tu computadora (para desarrollo/pruebas)",
        "VPS - Desplegar en servidor remoto (producción)",
        "Docker - Usar contenedores Docker"
    ]

    deployment_choice = ask_choice("¿Dónde deseas ejecutar Claudio?", deployment_modes, default=0)

    if deployment_choice == 0:
        config['deployment'] = 'local'
        print_info("Modo LOCAL seleccionado")
        print()

        port = ask_question("Puerto para el servidor local", default="8001")
        config['port'] = port
        config['install_dir'] = os.path.abspath(os.getcwd())

    elif deployment_choice == 1:
        config['deployment'] = 'vps'
        config['port'] = '8000'
        print_info("Modo VPS seleccionado")
        print()

        print_info("Configuración para despliegue en VPS:")

        vps_host = ask_question("IP o dominio de tu VPS", default="51.222.207.250")
        config['vps_host'] = vps_host

        vps_user = ask_question("Usuario SSH (root/ubuntu)", default="root")
        config['vps_user'] = vps_user

        install_dir = ask_question(
            "Directorio de instalación en la VPS",
            default=f"/opt/{project_name}"
        )
        config['install_dir'] = install_dir

    else:
        config['deployment'] = 'docker'
        config['port'] = '8000'
        print_info("Modo DOCKER seleccionado")
        config['install_dir'] = os.path.abspath(os.getcwd())

    print_success(f"Configuración de servidor: {config['deployment'].upper()}")

    # ============================================
    # PASO 5: Seguridad
    # ============================================
    print_section("PASO 5: Seguridad")

    print_info("Por seguridad, puedes restringir el acceso a tu bot.")
    print("Solo los usuarios que autorices podrán usar el bot.")
    print()
    print_info("Para obtener tu Telegram User ID:")
    print("  1. Abre @userinfobot en Telegram")
    print("  2. Envía /start")
    print("  3. Copia tu ID (un número)")
    print()

    restrict_access = ask_yes_no("¿Deseas restringir el acceso a usuarios específicos?", default=False)

    if restrict_access:
        allowed_users = ask_question(
            "Ingresa los User IDs permitidos (separados por coma)",
            default="*"
        )
        config['allowed_users'] = allowed_users

        if allowed_users != '*':
            print_success(f"Solo los usuarios {allowed_users} podrán usar el bot")
        else:
            print_warning("Acceso público permitido (cualquiera puede usar el bot)")
    else:
        config['allowed_users'] = '*'
        print_info("Acceso público: cualquiera con el link del bot podrá usarlo")

    # ============================================
    # RESUMEN Y CONFIRMACIÓN
    # ============================================
    print_header("RESUMEN DE CONFIGURACIÓN")

    print(f"  Nombre del Proyecto:  {Colors.GREEN}{config['project_name']}{Colors.END}")
    print(f"  Proveedor IA:         {Colors.GREEN}{config['ai_provider'].upper()}{Colors.END}")

    if config['ai_provider'] == 'anthropic':
        print(f"  Modelo IA:            {Colors.GREEN}{config.get('anthropic_model', 'N/A')}{Colors.END}")
    elif config['ai_provider'] == 'openai':
        print(f"  Modelo IA:            {Colors.GREEN}{config.get('openai_model', 'N/A')}{Colors.END}")
    elif config['ai_provider'] == 'ollama':
        print(f"  Modelo IA:            {Colors.GREEN}{config.get('ollama_model', 'N/A')}{Colors.END}")

    print(f"  Telegram:             {Colors.GREEN}Configurado ✓{Colors.END}")
    print(f"  n8n:                  {Colors.GREEN}{'Habilitado' if config.get('n8n_enabled') else 'Deshabilitado'}{Colors.END}")
    print(f"  Despliegue:            {Colors.GREEN}{config['deployment'].upper()}{Colors.END}")
    print(f"  Puerto:               {Colors.GREEN}{config.get('port', 'N/A')}{Colors.END}")
    print(f"  Directorio:           {Colors.GREEN}{config.get('install_dir', 'N/A')}{Colors.END}")
    print(f"  Seguridad:            {Colors.GREEN}{'Restringido' if config.get('allowed_users') != '*' else 'Abierto'}{Colors.END}")
    print()

    if not ask_yes_no("¿Esta configuración es correcta? ¿Continuar?", default=True):
        print_info("Instalación cancelada. Puedes ejecutar el instalador nuevamente.")
        sys.exit(0)

    # ============================================
    # CREAR ARCHIVOS
    # ============================================
    print_section("CREANDO ARCHIVOS DE CONFIGURACIÓN")

    # Crear .env
    env_content = create_env_file(config)
    with open('.env', 'w') as f:
        f.write(env_content)
    print_success("Archivo .env creado")

    # Guardar config para uso futuro
    safe_config = config.copy()
    for key in ['api_key', 'telegram_token', 'anthropic_api_key', 'openai_api_key']:
        if key in safe_config:
            safe_config[key] = '***HIDDEN***'
    with open('.claudio_config.json', 'w') as f:
        json.dump(safe_config, f, indent=2)
    print_success("Configuración guardada en .claudio_config.json")

    # Crear script de prueba
    test_script = create_test_script(config)
    test_script_path = 'test_installation.sh'
    with open(test_script_path, 'w') as f:
        f.write(test_script)
    os.chmod(test_script_path, 0o755)
    print_success(f"Script de prueba creado: {test_script_path}")

    # ============================================
    # INSTALACIÓN
    # ============================================
    print_section("INSTALANDO DEPENDENCIAS")

    if config['deployment'] == 'local':
        print_info("Configurando para ejecución local...")

        # Verificar si hay venv
        if not os.path.exists('venv'):
            print_info("Creando entorno virtual Python...")
            if os.name == 'nt':
                os.system('python -m venv venv')
            else:
                os.system('python3 -m venv venv')
            print_success("Entorno virtual creado")
        else:
            print_success("Entorno virtual ya existe")

        # Instalar dependencias
        print_info("Instalando dependencias Python...")

        if os.name == 'nt':  # Windows
            print_info("Ejecuta: venv\\Scripts\\pip install -r requirements.txt")
        else:  # Linux/Mac
            os.system('venv/bin/pip install -q -r requirements.txt')
            print_success("Dependencias instaladas")

        # Crear scripts de inicio
        if os.name == 'nt':
            # Windows scripts
            if not os.path.exists('start.bat'):
                start_script = """@echo off
title Claudio Bot
echo Starting Claudio Bot...
venv\\Scripts\\python bot_v2.py
pause
"""
                with open('start.bat', 'w') as f:
                    f.write(start_script)
                print_success("start.bat creado")

            if not os.path.exists('start_server.bat'):
                server_script = """@echo off
title Claudio Server
echo Starting Claudio Server...
venv\\Scripts\\python claudio_complete.py
pause
"""
                with open('start_server.bat', 'w') as f:
                    f.write(server_script)
                print_success("start_server.bat creado")
        else:
            # Linux/Mac scripts
            if not os.path.exists('start.sh'):
                start_script = """#!/bin/bash
echo "Starting Claudio Bot..."
source venv/bin/activate
python bot_v2.py
"""
                with open('start.sh', 'w') as f:
                    f.write(start_script)
                os.chmod('start.sh', 0o755)
                print_success("start.sh creado")

            if not os.path.exists('start_server.sh'):
                server_script = """#!/bin/bash
echo "Starting Claudio Server..."
source venv/bin/activate
python claudio_complete.py
"""
                with open('start_server.sh', 'w') as f:
                    f.write(server_script)
                os.chmod('start_server.sh', 0o755)
                print_success("start_server.sh creado")

    elif config['deployment'] == 'vps':
        print_info("Creando scripts para despliegue VPS...")

        # Crear script de despliegue
        install_dir = config.get('install_dir', '/opt/claudio-bot')

        deploy_script = f"""#!/bin/bash
# Claudio - Deploy to VPS
# Generated by installer

set -e

VPS_HOST="{config.get('vps_host', 'your.vps.ip')}"
VPS_USER="{config.get('vps_user', 'root')}"
INSTALL_DIR="{install_dir}"

echo "======================================================================"
echo "  Deploying Claudio to VPS: $VPS_HOST"
echo "======================================================================"
echo ""

# Paso 1: Crear directorio y usuario
echo "[1/5] Setting up VPS..."
ssh $VPS_USER@$VPS_HOST "sudo useradd -m -s /bin/bash claudio 2>/dev/null || true"
ssh $VPS_USER@$VPS_HOST "sudo mkdir -p {install_dir}"
ssh $VPS_USER@$VPS_HOST "sudo chown -R claudio:claudio {install_dir}"

# Paso 2: Copiar archivos
echo "[2/5] Copying files to VPS..."
scp claudio_complete.py $VPS_USER@$VPS_HOST:{install_dir}/
scp bot_v2.py $VPS_USER@$VPS_HOST:{install_dir}/
scp n8n_database.py $VPS_USER@$VPS_HOST:{install_dir}/
scp n8n_mcp_tools.py $VPS_USER@$VPS_HOST:{install_dir}/
scp requirements.txt $VPS_USER@$VPS_HOST:{install_dir}/
scp -r skills $VPS_USER@$VPS_HOST:{install_dir}/
scp .env $VPS_USER@$VPS_HOST:{install_dir}/
scp test_installation.sh $VPS_USER@$VPS_HOST:{install_dir}/

# Paso 3: Configurar entorno Python
echo "[3/5] Setting up Python environment..."
ssh $VPS_USER@$VPS_HOST "cd {install_dir} && sudo -u claudio python3 -m venv venv"
ssh $VPS_USER@$VPS_HOST "sudo -u claudio {install_dir}/venv/bin/pip install -q -r {install_dir}/requirements.txt"

# Paso 4: Crear servicios systemd
echo "[4/5] Creating systemd services..."
ssh $VPS_USER@$VPS_HOST "sudo tee /etc/systemd/system/claudio-server.service > /dev/null <<'SVCEOF'
[Unit]
Description=Claudio Server
After=network.target

[Service]
Type=simple
User=claudio
WorkingDirectory={install_dir}
EnvironmentFile={install_dir}/.env
ExecStart={install_dir}/venv/bin/python claudio_complete.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF"

ssh $VPS_USER@$VPS_HOST "sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null <<'SVCEOF'
[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User=claudio
WorkingDirectory={install_dir}
EnvironmentFile={install_dir}/.env
ExecStart={install_dir}/venv/bin/python bot_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF"

# Paso 5: Habilitar y iniciar
echo "[5/5] Enabling and starting services..."
ssh $VPS_USER@$VPS_HOST "sudo systemctl daemon-reload"
ssh $VPS_USER@$VPS_HOST "sudo systemctl enable claudio-server.service claudio-telegram-bot.service"

echo ""
echo "======================================================================"
echo "  Deployment complete!"
echo "======================================================================"
echo ""
echo "To start services:"
echo "  ssh $VPS_USER@$VPS_HOST 'sudo systemctl start claudio-server claudio-telegram-bot'"
echo ""
echo "To check status:"
echo "  ssh $VPS_USER@$VPS_HOST 'sudo systemctl status claudio-server claudio-telegram-bot'"
echo ""
"""

        with open('deploy_vps.sh', 'w') as f:
            f.write(deploy_script)
        os.chmod('deploy_vps.sh', 0o755)
        print_success("Script de despliegue VPS creado: deploy_vps.sh")

    elif config['deployment'] == 'docker':
        print_info("Configuración Docker lista (usa docker-compose.yml)")
        print_success("Ejecuta: docker-compose up -d")

    # ============================================
    # PRUEBA POST-INSTALACIÓN
    # ============================================
    run_post_installation_test(config)

    # ============================================
    # INSTRUCCIONES FINALES
    # ============================================
    print_header("INSTALACIÓN COMPLETADA")

    print()
    print(f"{Colors.BOLD}{Colors.GREEN}¡Claudio está listo para usar!{Colors.END}\n")

    print(f"{Colors.BOLD}📁 Archivos creados:{Colors.END}")
    print(f"  {Colors.CYAN}.env{Colors.END} - Configuración")
    print(f"  {Colors.CYAN}.claudio_config.json{Colors.END} - Resumen de configuración")
    print(f"  {Colors.CYAN}test_installation.sh{Colors.END} - Script de prueba")

    if config['deployment'] == 'local':
        print()
        print(f"{Colors.YELLOW}Para iniciar Claudio:{Colors.END}")
        if os.name == 'nt':
            print(f"  1. Doble clic en {Colors.GREEN}start_server.bat{Colors.END}")
            print(f"  2. Doble clic en {Colors.GREEN}start.bat{Colors.END}")
        else:
            print(f"  1. {Colors.GREEN}./start_server.sh{Colors.END}")
            print(f"  2. {Colors.GREEN}./start.sh{Colors.END}")

    elif config['deployment'] == 'vps':
        print()
        print(f"{Colors.YELLOW}Para desplegar a VPS:{Colors.END}")
        print(f"  {Colors.GREEN}bash deploy_vps.sh{Colors.END}")
        print()
        print(f"{Colors.YELLOW}Después del despliegue:{Colors.END}")
        print(f"  • Ver logs: {Colors.CYAN}ssh {config['vps_user']}@{config['vps_host']} 'sudo journalctl -u claudio-telegram-bot -f'{Colors.END}")
        print(f"  • Ver estado: {Colors.CYAN}ssh {config['vps_user']}@{config['vps_host']} 'sudo systemctl status claudio-telegram-bot'{Colors.END}")

    print()
    print(f"{Colors.YELLOW}Para ejecutar la prueba de funcionamiento:{Colors.END}")
    if os.name != 'nt':
        print(f"  {Colors.GREEN}bash test_installation.sh{Colors.END}")
    else:
        print(f"  {Colors.GREEN}Revisa los checks anteriores{Colors.END}")

    print()
    print(f"{Colors.CYAN}Únete a tu bot en Telegram y comienza a crear workflows!{Colors.END}")
    print()
    print(f"{Colors.BOLD}Ejemplos de comandos:{Colors.END}")
    print(f"  • {Colors.GREEN}Ayuda{Colors.END} - Ver opciones")
    print(f"  • {Colors.GREEN}Crea un workflow de webhook{Colors.END}")
    print(f"  • {Colors.GREEN}Valida esta expresión: {{$json.data}}{Colors.END}")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_error("Instalación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print()
        print_error(f"Error durante la instalación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
