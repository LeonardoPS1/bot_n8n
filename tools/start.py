#!/usr/bin/env python3
"""
Claudio Bot - Start Script
Inicia el servidor de Claudio y el bot de Telegram
"""

import os
import sys
import subprocess
import time
import signal
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

def print_header(text):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{bcolors.ENDC}\n")

def print_success(text):
    print(f"{bcolors.OKGREEN}✓ {text}{bcolors.ENDC}")

def print_error(text):
    print(f"{bcolors.FAIL}✗ {text}{bcolors.ENDC}")

def print_info(text):
    print(f"{bcolors.OKCYAN}➜ {text}{bcolors.ENDC}")

def check_env_file():
    """Verifica que el archivo .env exista"""
    if not Path(".env").exists():
        print_error("Archivo .env no encontrado")
        print_info("Ejecuta 'python install.py' primero")
        return False
    return True

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print_info("Verificando dependencias...")
    try:
        import fastapi
        import uvicorn
        import telegram
        import openai
        print_success("Dependencias OK")
        return True
    except ImportError as e:
        print_error(f"Falta dependencia: {e}")
        print_info("Ejecuta: pip install -r requirements.txt")
        return False

def start_server():
    """Inicia el servidor de Claudio"""
    print_info("Iniciando servidor de Claudio...")
    try:
        # Start server in background
        server_process = subprocess.Popen(
            [sys.executable, "claudio_complete.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait a bit for server to start
        time.sleep(3)

        # Check if process is still running
        if server_process.poll() is None:
            print_success("Servidor iniciado (PID: %d)" % server_process.pid)
            return server_process
        else:
            print_error("El servidor falló al iniciar")
            return None
    except Exception as e:
        print_error(f"Error iniciando servidor: {e}")
        return None

def start_bot():
    """Inicia el bot de Telegram"""
    print_info("Iniciando bot de Telegram...")
    try:
        bot_process = subprocess.Popen(
            [sys.executable, "bot_v2.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        time.sleep(2)

        if bot_process.poll() is None:
            print_success("Bot iniciado (PID: %d)" % bot_process.pid)
            return bot_process
        else:
            print_error("El bot falló al iniciar")
            return None
    except Exception as e:
        print_error(f"Error iniciando bot: {e}")
        return None

def main():
    print_header("🤖 CLAUDIO BOT - INICIANDO SERVICIOS")

    # Check environment
    if not check_env_file():
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Start server
    server_process = start_server()
    if not server_process:
        sys.exit(1)

    # Start bot
    bot_process = start_bot()
    if not bot_process:
        server_process.terminate()
        sys.exit(1)

    print_header("🚀 CLAUDIO BOT EJECUTÁNDOSE")
    print(f"\n{bcolors.OKGREEN}Servidor PID:{bcolors.ENDC} {server_process.pid}")
    print(f"{bcolors.OKGREEN}Bot PID:{bcolors.ENDC} {bot_process.pid}")
    print(f"\n{bcolors.OKCYAN}Presiona Ctrl+C para detener{bcolors.ENDC}\n")

    # Wait for processes
    processes = [server_process, bot_process]

    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print(f"\n{bcolors.WARNING}Deteniendo servicios...{bcolors.ENDC}")
        for process in processes:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print_success("Servicios detenidos")

if __name__ == "__main__":
    main()
