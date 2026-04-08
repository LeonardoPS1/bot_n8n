#!/usr/bin/env python3
"""
Telegram Bot powered by Claudio (Claude Code with n8n-MCP)
Connects to Claudio Server for n8n workflow expertise
Deploy on VPS for 24/7 availability
"""

import os
import logging
import httpx
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

# Load environment variables from .env file
load_dotenv()

# Configure logging (UTF-8 for file, ASCII-safe for console)
file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CLADIO_SERVER_URL = os.getenv('CLADIO_SERVER_URL', 'http://localhost:8000')
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))


def check_permission(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    if not ALLOWED_USERS:
        return True  # Allow all if no restriction
    return str(user_id) in ALLOWED_USERS


async def call_claudio(message: str, user_id: int, user_name: str, clear_history: bool = False) -> str:
    """Call Claudio Server API"""
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/chat",
                json={
                    "message": message,
                    "user_id": user_id,
                    "user_name": user_name,
                    "clear_history": clear_history
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "No response from Claudio")
    except httpx.TimeoutException:
        raise Exception("Claudio server timeout. Please try again.")
    except httpx.HTTPStatusError as e:
        raise Exception(f"Claudio server error: {e.response.status_code}")
    except Exception as e:
        raise Exception(f"Failed to connect to Claudio: {str(e)}")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    if not check_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have permission to use this bot.")
        return

    welcome_message = (
        "🤖 *Claudio Telegram Bot*\n\n"
        "I'm **Claudio**, your expert n8n workflow assistant with full access to:\n"
        "• 1,396 n8n nodes (core + community)\n"
        "• n8n-MCP tools & validation\n"
        "• 2,709+ workflow templates\n"
        "• Advanced expression syntax\n\n"
        "*Commands:*\n"
        "/start - Show this message\n"
        "/clear - Clear conversation history\n"
        "/health - Check Claudio server status\n"
        "/help - Show help\n\n"
        "Ask me anything about n8n workflows!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 *Claudio Help*\n\n"
        "*What I can do:*\n"
        "• Search and recommend n8n nodes\n"
        "• Build and validate workflows\n"
        "• Fix expression errors\n"
        "• Suggest templates (2,709+ available)\n"
        "• Debug workflow issues\n"
        "• Explain n8n patterns\n\n"
        "*Commands:*\n"
        "/clear - Reset conversation\n"
        "/health - Check server status\n\n"
        "*Examples:*\n"
        "• \"Create a webhook to Slack workflow\"\n"
        "• \"Fix my IF node connections\"\n"
        "• \"Find templates for HTTP API\"\n"
        "• \"Validate this configuration\""
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check Claudio server health"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{CLADIO_SERVER_URL}/health")
            response.raise_for_status()
            data = response.json()

            status_emoji = "✅" if data.get("status") == "healthy" else "❌"
            n8n_status = "✅ Connected" if data.get("n8n_connected") else "❌ Disconnected"

            health_message = (
                f"{status_emoji} *Claudio Server Status*\n\n"
                f"Server: {data.get('status', 'unknown')}\n"
                f"n8n: {n8n_status}\n"
                f"Timestamp: {data.get('timestamp', 'unknown')}"
            )
            await update.message.reply_text(health_message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Claudio server is unreachable: {str(e)}")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    user_id = update.effective_user.id

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.delete(f"{CLADIO_SERVER_URL}/api/history/{user_id}")
        await update.message.reply_text("🧹 Conversation history cleared.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Failed to clear history: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming messages"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if not check_permission(user_id):
        await update.message.reply_text("⛔ You don't have permission to use this bot.")
        return

    user_message = update.message.text
    if not user_message:
        return

    # Send typing indicator
    await update.message.chat.send_action('typing')

    try:
        # Call Claudio Server
        logger.info(f"User {user_id} ({user_name}): {user_message}")

        response_text = await call_claudio(user_message, user_id, user_name)

        # Send response (handle Telegram message length limit)
        max_length = 4096
        if len(response_text) <= max_length:
            await update.message.reply_text(response_text, parse_mode='Markdown')
        else:
            # Split long messages
            chunks = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')

        logger.info(f"Claudio response to {user_id}: {response_text[:100]}...")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n\n"
            f"💡 Use /health to check if Claudio server is running."
        )


def main() -> None:
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("Claudio Telegram Bot starting...")
    logger.info(f"Claudio Server: {CLADIO_SERVER_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
