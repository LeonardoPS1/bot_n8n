#!/usr/bin/env python3
"""
Bot Híbrido: Gemini para Telegram + Claude para n8n
- Gemini: Chat general y comunicación con usuarios
- Claude (Claudio): Expertise exclusivo de n8n workflows
"""

import os
import logging
import httpx
import re
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot_hibrido.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
CLADIO_SERVER_URL = os.getenv('CLADIO_SERVER_URL', 'http://localhost:8000')
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))

# System prompt para Gemini
GEMINI_SYSTEM_PROMPT = """Eres un asistente que ROUTEA mensajes:

🎯 REGLAS:
- Si la pregunta es sobre n8n, workflows, automatización → USA CLAUUDIO
- Si es chat general, saludos, o preguntas no técnicas → RESPONDE DIRECTAMENTE

⚡ FORMATO:
- Para usar Claudio: empieza con **[CLAUUDIO]**
- Para responder directamente: resuelve normalmente

Ejemplos:
- "Crear workflow n8n" → **[CLAUUDIO]** Ayuda a crear workflow
- "hola" → ¡Hola! Soy tu asistente...
- "conectar Slack con n8n" → **[CLAUUDIO]** Explicar conexión Slack

Responde de forma amigable y concisa.
"""


def check_permission(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    if not ALLOWED_USERS:
        return True
    return str(user_id) in ALLOWED_USERS


async def ask_gemini(message: str, user_id: int) -> str:
    """Ask Gemini for routing/response (using requests)"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

        full_prompt = f"{GEMINI_SYSTEM_PROMPT}\n\nUsuario: {message}"
        response = model.generate_content(full_prompt)
        return response.text.strip()

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        # Fallback: simple keyword matching
        message_lower = message.lower()
        n8n_keywords = ['n8n', 'workflow', 'nodo', 'node', 'webhook', 'automation', 'automatizar', 'slack', 'integracion', 'api', 'expresion']

        if any(keyword in message_lower for keyword in n8n_keywords):
            return f"**[CLAUUDIO]** El usuario pregunta sobre n8n: {message}"
        else:
            return f"Hola, soy tu asistente. Puedo ayudarte con n8n workflows o responder preguntas generales. ¿En qué te ayudo?"


async def call_claudio(message: str, user_id: int) -> str:
    """Call Claudio Server for n8n expertise"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "user_name": "TelegramUser",
                    "clear_history": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response from Claudio")
    except Exception as e:
        logger.error(f"Claudio error: {e}")
        return f"❌ Error conectando con Claudio: {str(e)}"


async def process_message(user_message: str, user_id: int) -> str:
    """Process message through Gemini -> decide if need Claudio"""
    gemini_response = await ask_gemini(user_message, user_id)

    if "**[CLAUUDIO]**" in gemini_response or "[CLAUUDIO]" in gemini_response:
        claudio_query = gemini_response.split("[CLAUUDIO]")[-1].strip()
        if not claudio_query or claudio_query == user_message:
            claudio_query = user_message

        logger.info(f"Routing to Claudio: {claudio_query[:100]}...")
        claudio_response = await call_claudio(claudio_query, user_id)
        return f"🤖 **CLAUUDIO (n8n Expert)**\n\n{claudio_response}"
    else:
        return gemini_response


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    if not check_permission(update.effective_user.id):
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return

    welcome_message = (
        "🤖 *Bot Híbrido: Gemini + Claudio*\n\n"
        "🧠 **Gemini** - Chat general\n"
        "⚡ **Claudio** - Expert en n8n workflows\n\n"
        "*Funciones:*\n"
        "• Preguntas técnicas de n8n → Claudio responde\n"
        "• Chat casual → Gemini responde\n"
        "• 1,396 nodos n8n documentados\n\n"
        "*Commands:*\n"
        "/start - Este mensaje\n"
        "/clear - Limpiar historial\n"
        "/health - Estado de servicios\n\n"
        "💡 *Ejemplos:*\n"
        "• \"hola\" → Gemini responde\n"
        "• \"crear workflow n8n\" → Claudio crea\n"
        "• \"conectar Slack\" → Claudio explica"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 *Ayuda del Bot Híbrido*\n\n"
        "🧠 **Gemini:** Chat general\n"
        "⚡ **Claudio:** n8n workflows\n\n"
        "*Ejemplos:*\n"
        "• \"Hola\" → Gemini\n"
        "• \"Workflow webhook\" → Claudio\n"
        "• \"Validar expresion\" → Claudio"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check both services health"""
    health_report = "🏥 *Estado de Servicios*\n\n"

    # Check Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("ping")
        health_report += "🧠 **Gemini**: ✅ Online\n"
    except Exception as e:
        health_report += f"🧠 **Gemini**: ❌ Error\n"

    # Check Claudio
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{CLAUDIO_SERVER_URL}/health")
            response.raise_for_status()
            data = response.json()
            health_report += f"⚡ **Claudio**: ✅ Online\n"
    except Exception as e:
        health_report += f"⚡ **Claudio**: ❌ Offline\n"

    await update.message.reply_text(health_report, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.delete(f"{CLAUDIO_SERVER_URL}/api/history/{update.effective_user.id}")
    except:
        pass
    await update.message.reply_text("🧹 Historial eliminado")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages with hybrid routing"""
    user_id = update.effective_user.id
    user_message = update.message.text

    if not user_message:
        return

    if not check_permission(user_id):
        await update.message.reply_text("⛔ No tienes permiso.")
        return

    await update.message.chat.send_action('typing')

    try:
        logger.info(f"User {user_id}: {user_message}")
        response_text = await process_message(user_message, user_id)

        max_length = 4096
        if len(response_text) <= max_length:
            await update.message.reply_text(response_text, parse_mode='Markdown')
        else:
            chunks = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')

        logger.info(f"Response: {response_text[:100]}...")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


def main() -> None:
    """Start the hybrid bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN no configurado")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY no configurado")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Bot Híbrido iniciando...")
    logger.info(f"🧠 Gemini OK")
    logger.info(f"⚡ Claudio Server: {CLADIO_SERVER_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
