#!/usr/bin/env python3
"""
Bot Híbrido: Gemini para Telegram + Claude para n8n
- Gemini: Chat general y comunicación con usuarios
- Claude (Claudio): Expertise exclusivo de n8n workflows
"""

import os
import logging
import httpx
import json
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
import google.generativeai as genai

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

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Conversation history for Gemini
gemini_history: dict = {}

# System prompt para Gemini - ENFOCADO EN ROUTING
GEMINI_SYSTEM_PROMPT = """Eres un asistente de Telegram amigable. TU FUNCIÓN PRINCIPAL es determinar si el usuario necesita ayuda con n8n.

🎯 REGLA DE ROUTING:
- Si la pregunta es sobre n8n, workflows, automatización, nodos, expresiones → USA CLAUDIO
- Si es chat general, saludos, o preguntas no técnicas → RESPONDE DIRECTAMENTE

📋 Indicadores para usar CLAUDIO:
- Palabras clave: n8n, workflow, nodo, node, webhook, automation, automatizar, integración
- Preguntas sobre: crear workflows, conectar servicios, API, expresiones, error en n8n
- Solicitud de: templates, ejemplos, validación, troubleshooting de n8n

💬 Responde directamente para:
- Saludos ("hola", "buenos días")
- Preguntas generales ("¿qué puedes hacer?", "quién eres")
- Temas no técnicos
- Conversación casual

⚡ FORMATO DE RESPUESTA:
- Para usar Claudio: empieza con **[CLAUUDIO]** y luego describe lo que necesitas pedirle
- Para responder directamente: resuelve normally

Ejemplos:
- "Crear workflow n8n" → **[CLAUUDIO]** El usuario quiere crear un workflow de n8n. Ayúdalo.
- "hola" → ¡Hola! Soy tu asistente. Puedo ayudarte con n8n workflows...
- "¿cómo conecto Slack con n8n?" → **[CLAUUDIO]** El usuario necesita conectar Slack en n8n.
"""

# System prompt para Claude - ESPECIALISTA EN N8N
CLAUUDIO_SYSTEM_PROMPT = """Eres CLAUUDIO, el EXPERTO EN N8N. Tu única función es ayudar con n8n workflows.

🎯 TU ESPECIALIDAD:
- 1,396 nodos n8n (core + community)
- n8n-MCP tools completos
- 2,709+ workflow templates
- Expressions syntax: $json, $node, $now, $env
- Validación de workflows
- Patrones arquitectónicos

⚠️ REGLAS CRÍTICAS:
1. NEVER TRUST DEFAULTS - Siempre configura todos los parámetros explícitamente
2. Webhook data = $json.body (no $json)
3. IF node usa branch="true" o branch="false"
4. HTTP POST requiere sendBody=true

Responde de forma directa y práctica. Sin saludos, sin small talk.
Solo n8n, solo workflows, solo soluciones técnicas."""


def check_permission(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    if not ALLOWED_USERS:
        return True
    return str(user_id) in ALLOWED_USERS


async def ask_gemini(message: str, user_id: int) -> str:
    """Ask Gemini for routing/response"""
    try:
        # Get or create chat history
        if user_id not in gemini_history:
            gemini_history[user_id] = []

        # Create chat with system prompt
        chat = gemini_model.start_chat(
            history=gemini_history[user_id],
        )

        # Add system instruction
        full_message = f"{GEMINI_SYSTEM_PROMPT}\n\nUsuario: {message}"

        response = chat.send_message(full_message)
        response_text = response.text.strip()

        # Update history
        gemini_history[user_id].append(
            {"role": "user", "parts": [message]}
        )
        gemini_history[user_id].append(
            {"role": "model", "parts": [response_text]}
        )

        # Keep last 20 messages
        if len(gemini_history[user_id]) > 20:
            gemini_history[user_id] = gemini_history[user_id][-20:]

        return response_text

    except Exception as e:
        logger.error(f"Gemini error: {e}")
        return f"Error con Gemini: {str(e)}"


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

    # Step 1: Ask Gemini to route
    gemini_response = await ask_gemini(user_message, user_id)

    # Step 2: Check if Gemini wants to use Claudio
    if "**[CLAUUDIO]**" in gemini_response or "[CLAUUDIO]" in gemini_response:

        # Extract the actual query for Claudio
        claudio_query = gemini_response.split("[CLAUUDIO]")[-1].strip()

        # If Gemini just forwarded without context, use original message
        if not claudio_query or claudio_query == user_message:
            claudio_query = user_message

        # Call Claudio with n8n expertise
        logger.info(f"Routing to Claudio: {claudio_query[:100]}...")
        claudio_response = await call_claudio(claudio_query, user_id)

        # Format response
        return f"🤖 **CLAUUDIO (n8n Expert)**\n\n{claudio_response}"

    else:
        # Gemini handled it directly
        return gemini_response


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    if not check_permission(update.effective_user.id):
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return

    welcome_message = (
        "🤖 *Bot Híbrido: Gemini + Claudio*\n\n"
        "🧠 **Gemini** - Chat general y conversación\n"
        "⚡ **Claudio** - Expert en n8n workflows\n\n"
        "*Funciones:*\n"
        "• Chat casual con Gemini\n"
        "• Preguntas técnicas de n8n → Claudio las responde\n"
        "• 1,396 nodos n8n documentados\n"
        "• 2,709+ plantillas de workflows\n\n"
        "*Commands:*\n"
        "/start - Este mensaje\n"
        "/clear - Limpiar historial\n"
        "/health - Estado de Claudio\n"
        "/help - Ayuda\n\n"
        "💡 *Ejemplos:*\n"
        "• \"hola\" → Gemini responde\n"
        "• \"crear workflow n8n\" → Claudio responde\n"
        "• \"¿cómo conecto Slack?\" → Claudio responde"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 *Ayuda del Bot Híbrido*\n\n"
        "🧠 **Gemini se encarga de:**\n"
        "• Saludos y conversación casual\n"
        "• Preguntas generales\n"
        "• Routing inteligente\n\n"
        "⚡ **Claudio se encarga de:**\n"
        "• Crear y validar workflows n8n\n"
        "• Buscar nodos y templates\n"
        "• Expresiones y sintaxis n8n\n"
        "• Troubleshooting técnico\n\n"
        "*Ejemplos de uso:*\n"
        "• \"Hola\" → Gemini te saluda\n"
        "• \"Workflow webhook a Slack\" → Claudio crea\n"
        "• "¿Cómo está el clima?" → Gemini responde\n"
        "• \"Validar expresión n8n\" → Claudio valida"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check both services health"""
    health_report = "🏥 *Estado de Servicios*\n\n"

    # Check Gemini
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("ping")
        health_report += "🧠 **Gemini**: ✅ Online\n"
    except Exception as e:
        health_report += f"🧠 **Gemini**: ❌ Error\n"

    # Check Claudio
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{CLADIO_SERVER_URL}/health")
            response.raise_for_status()
            data = response.json()
            n8n_status = "✅" if data.get("n8n", {}).get("connected") else "⚠️"
            health_report += f"⚡ **Claudio**: ✅ Online\n"
            health_report += f"   └─ n8n: {n8n_status}\n"
    except Exception as e:
        health_report += f"⚡ **Claudio**: ❌ Offline\n"

    await update.message.reply_text(health_report, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    user_id = update.effective_user.id

    # Clear Gemini history
    if user_id in gemini_history:
        del gemini_history[user_id]

    # Clear Claudio history
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.delete(f"{CLAUDIO_SERVER_URL}/api/history/{user_id}")
    except:
        pass

    await update.message.reply_text("🧹 Historial eliminado (Gemini + Claudio)")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages with hybrid routing"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    user_message = update.message.text

    if not user_message:
        return

    if not check_permission(user_id):
        await update.message.reply_text("⛔ No tienes permiso para usar este bot.")
        return

    # Send typing indicator
    await update.message.chat.send_action('typing')

    try:
        logger.info(f"User {user_id} ({user_name}): {user_message}")

        # Process through hybrid system
        response_text = await process_message(user_message, user_id)

        # Send response (handle Telegram length limit)
        max_length = 4096
        if len(response_text) <= max_length:
            await update.message.reply_text(response_text, parse_mode='Markdown')
        else:
            chunks = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')

        logger.info(f"Response to {user_id}: {response_text[:100]}...")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n\n💡 Usa /health para verificar el estado."
        )


def main() -> None:
    """Start the hybrid bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN no configurado")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY no configurado")

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("🤖 Bot Híbrido iniciando...")
    logger.info(f"🧠 Gemini: {GEMINI_API_KEY[:10]}...")
    logger.info(f"⚡ Claudio Server: {CLADIO_SERVER_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
