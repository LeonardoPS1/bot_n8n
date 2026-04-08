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
ALLOWED_ADMIN_USERS = os.getenv('ALLOWED_ADMIN_USERS', '').split(',') if os.getenv('ALLOWED_ADMIN_USERS') else []
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))
ADMIN_KEY = os.getenv('ADMIN_KEY', '')  # Additional security for admin commands


def check_permission(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    if not ALLOWED_USERS:
        return True  # Allow all if no restriction
    return str(user_id) in ALLOWED_USERS or "*" in ALLOWED_USERS


def check_admin_permission(user_id: int) -> bool:
    """Check if user is admin"""
    if not ALLOWED_ADMIN_USERS:
        return False  # No admin configured
    return str(user_id) in ALLOWED_ADMIN_USERS or "*" in ALLOWED_ADMIN_USERS


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


# ============================================
# ADMIN COMMANDS
# ============================================

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current model status"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/status",
                json={"user_id": update.effective_user.id}
            )
            response.raise_for_status()
            data = response.json()

        status_text = (
            f"📊 *Model Status*\n\n"
            f"Provider: {data['current_provider']}\n"
            f"Model: {data['current_model']}\n"
            f"Auto-fallback: {'✅ Enabled' if data['auto_fallback'] else '❌ Disabled'}\n\n"
            f"*Available Providers:*\n"
        )

        for provider in data['available_providers']:
            status_text += f"• {provider}\n"

        if data.get('custom_model'):
            custom = data['custom_model']
            status_text += f"\n*Custom Model:*\n• Name: {custom['name']}\n• Configured: {'✅' if custom['configured'] else '❌'}\n"

        await update.message.reply_text(status_text, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to get status: {str(e)}")


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available models"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/list-models",
                json={"user_id": update.effective_user.id}
            )
            response.raise_for_status()
            data = response.json()

        models_text = f"📋 *Available Models*\n\nCurrent mode: *{data['current_mode']}*\n\n"

        for provider_key, provider_info in data['providers'].items():
            status = "✅" if provider_info['configured'] else "❌"
            models_text += f"{status} *{provider_info['name']}*\n"

            if provider_info.get('current_model'):
                models_text += f"  Current: {provider_info['current_model']}\n"

            if provider_info.get('models'):
                models_text += f"  Available: {', '.join(provider_info['models'][:3])}"
                if len(provider_info['models']) > 3:
                    models_text += f" (+{len(provider_info['models'])-3} more)"
                models_text += "\n"

            if provider_key == 'ollama' and provider_info.get('base_url'):
                models_text += f"  Base URL: {provider_info['base_url']}\n"

            models_text += "\n"

        await update.message.reply_text(models_text, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to list models: {str(e)}")


async def switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to a different model"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    args = context.args if hasattr(context, 'args') else []

    if not args:
        await update.message.reply_text(
            "🔄 *Switch Model*\n\n"
            "Usage: /switch <provider> [<model>]\n\n"
            "Available providers:\n"
            "• anthropic\n"
            "• openai\n"
            "• gemini\n"
            "• qwen\n"
            "• deepseek\n"
            "• ollama\n\n"
            "Example: /switch anthropic\n"
            "Example: /switch openai gpt-4o"
        )
        return

    try:
        new_provider = args[0]
        new_model = args[1] if len(args) > 1 else None

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/switch-model",
                json={
                    "user_id": update.effective_user.id,
                    "new_provider": new_provider,
                    "new_model": new_model
                }
            )
            response.raise_for_status()
            data = response.json()

        if data.get("requires_restart"):
            await update.message.reply_text(
                f"⚠️ {data['message']}\n\n"
                f"Para cambiar de modelo, edita el archivo .env en tu servidor:\n"
                f"AI_PROVIDER={new_provider}\n"
                f"Luego reinicia el servidor:\n"
                f"sudo systemctl restart claudio-server"
            )
        else:
            await update.message.reply_text(f"✅ {data['message']}")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to switch model: {str(e)}")


async def addmodel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a custom model"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    args = context.args if hasattr(context, 'args') else []

    if len(args) < 3:
        await update.message.reply_text(
            "➕ *Add Custom Model*\n\n"
            "Usage: /addmodel <name> <api_key> <base_url> [provider_type]\n\n"
            "Parameters:\n"
            "• name - Model name (ej: mi-modelo-custom)\n"
            "• api_key - Your API key\n"
            "• base_url - API base URL (ej: https://api.example.com/v1)\n"
            "• provider_type - openai or anthropic (default: openai)\n\n"
            "Example:\n"
            "/addmodel mi-modelo sk-... https://api.example.com/v1 openai\n\n"
            "Note: El modo multi-provider debe estar activo en el servidor"
        )
        return

    try:
        name = args[0]
        api_key = args[1]
        base_url = args[2]
        provider_type = args[3] if len(args) > 3 else "openai"

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/add-custom-model",
                json={
                    "user_id": update.effective_user.id,
                    "name": name,
                    "api_key": api_key,
                    "base_url": base_url,
                    "provider_type": provider_type
                }
            )
            response.raise_for_status()
            data = response.json()

        if data.get("requires_multi_provider"):
            await update.message.reply_text(
                f"⚠️ {data['message']}\n\n"
                f"Para agregar modelos custom, activa multi-provider en .env:\n"
                f"AI_PROVIDER=multi\n"
                f"Y reinicia el servidor."
            )
        else:
            available = data.get('available_providers', [])
            await update.message.reply_text(
                f"✅ {data['message']}\n\n"
                f"Proveedores disponibles: {', '.join(available)}"
            )

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to add custom model: {str(e)}")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Test current model availability"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/test-model",
                json={"user_id": update.effective_user.id}
            )
            response.raise_for_status()
            data = response.json()

        status_emoji = "✅" if data['available'] else "❌"

        test_text = (
            f"🧪 *Model Test*\n\n"
            f"{status_emoji} Status: {data['status']}\n"
            f"Provider: {data['provider']}\n"
            f"Model: {data['model']}\n"
        )

        if data.get('error'):
            test_text += f"\n❌ Error: {data['error']}"

        await update.message.reply_text(test_text, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to test model: {str(e)}")


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin help"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    admin_text = (
        "⚙️ *Admin Commands*\n\n"
        "*Model Management:*\n"
        "/status - Show current model status\n"
        "/models - List all available models\n"
        "/switch <provider> - Switch to different provider\n"
        "/addmodel <name> <key> <url> [type] - Add custom model\n"
        "/test - Test current model availability\n\n"
        "*System Commands:*\n"
        "/health - Check server health\n"
        "/clear - Clear conversation history\n"
        "/help - Show this help\n\n"
        "*Available Providers:*\n"
        "anthropic, openai, gemini, qwen, deepseek, ollama\n\n"
        "*Provider Types for Custom Models:*\n"
        "openai (default) - For OpenAI-compatible APIs\n"
        "anthropic - For Anthropic-compatible APIs"
    )

    await update.message.reply_text(admin_text, parse_mode='Markdown')


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

    # Admin commands
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("models", models_command))
    application.add_handler(CommandHandler("switch", switch_command))
    application.add_handler(CommandHandler("addmodel", addmodel_command))
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("admin", admin_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("Claudio Telegram Bot starting...")
    logger.info(f"Claudio Server: {CLADIO_SERVER_URL}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
