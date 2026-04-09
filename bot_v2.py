#!/usr/bin/env python3
"""
Telegram Bot powered by Claudio (Claude Code with n8n-MCP)
Connects to Claudio Server for n8n workflow expertise
Deploy on VPS for 24/7 availability
Version 4.6.1 - Complete Provider Configuration with Ollama Support
"""

import os
import logging
import httpx
import re
from typing import Optional, Dict
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging (UTF-8 for file, ASCII-safe for console) - use absolute path
LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / 'bot.log'
file_handler = logging.FileHandler(str(LOG_FILE), encoding='utf-8')
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
VPS_PROJECT_DIR = '/opt/claudio-bot'  # Path on VPS
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []
ALLOWED_ADMIN_USERS = os.getenv('ALLOWED_ADMIN_USERS', '').split(',') if os.getenv('ALLOWED_ADMIN_USERS') else []
TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '180'))  # Increased to 3 minutes for bulk operations
ADMIN_KEY = os.getenv('ADMIN_KEY', '')

# Conversation states for API key input
WAITING_FOR_API_KEY = 1

# Store pending API key operations
pending_key_operations: Dict[int, Dict] = {}


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


def mask_api_key(api_key: str) -> str:
    """Mask API key for display - show only first 8 and last 4 characters"""
    if not api_key or len(api_key) < 12:
        return "***"
    return f"{api_key[:8]}...{api_key[-4:]}"


def validate_api_key_format(provider: str, api_key: str) -> bool:
    """Validate API key format based on provider"""
    if not api_key or len(api_key) < 10:
        return False

    provider = provider.lower()

    # Anthropic keys start with sk-ant-
    if provider == 'anthropic':
        return api_key.startswith('sk-ant-')

    # OpenAI keys start with sk-
    elif provider == 'openai':
        return api_key.startswith('sk-') and not api_key.startswith('sk-ant-')

    # Gemini keys are longer alphanumeric
    elif provider == 'gemini':
        return len(api_key) >= 20

    # Qwen keys start with sk-
    elif provider == 'qwen':
        return api_key.startswith('sk-')

    # DeepSeek keys start with sk-
    elif provider == 'deepseek':
        return api_key.startswith('sk-')

    # GLM keys contain dots and are longer
    elif provider == 'glm':
        return len(api_key) >= 20 and '.' in api_key

    # Custom providers - minimal validation
    else:
        return len(api_key) >= 10


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


async def update_env_file(provider: str, api_key: str) -> bool:
    """Update .env file with new API key"""
    try:
        # Map provider to env variable name
        env_mapping = {
            'anthropic': 'ANTHROPIC_API_KEY',
            'openai': 'OPENAI_API_KEY',
            'gemini': 'GEMINI_API_KEY',
            'qwen': 'QWEN_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY',
            'glm': 'GLM_API_KEY',
            'ollama': 'OLLAMA_BASE_URL',
        }

        env_var = env_mapping.get(provider.lower())
        if not env_var:
            return False

        # Read current .env
        env_path = f'{VPS_PROJECT_DIR}/.env'
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update or add the API key line
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f'{env_var}='):
                lines[i] = f'{env_var}={api_key}\n'
                updated = True
                break

        if not updated:
            lines.append(f'{env_var}={api_key}\n')

        # Write back
        with open(env_path, 'w') as f:
            f.writelines(lines)

        logger.info(f"Updated {env_var} in .env file")
        return True

    except Exception as e:
        logger.error(f"Failed to update .env: {e}")
        return False


async def restart_services() -> bool:
    """Restart claudio-server to load new API keys"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Use local script or command to restart
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/restart",
                timeout=5.0
            )
            return True
    except:
        # If endpoint doesn't exist, try direct command
        pass

    return False


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
        "• Advanced expression syntax\n"
        "• **Dynamic AI model switching** 🔄\n"
        "• **Secure API key management** 🔐\n\n"
        "*Commands:*\n"
        "/start - Show this message\n"
        "/clear - Clear conversation history\n"
        "/health - Check Claudio server status\n"
        "/help - Show help\n\n"
        "*Admin Commands:*\n"
        "/admin - Show admin commands\n\n"
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
        "• Explain n8n patterns\n"
        "• **Switch AI models dynamically** 🔄\n"
        "• **Add API keys securely** 🔐\n\n"
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
            n8n_status = "✅ Connected" if data.get("n8n", {}).get("connected") else "❌ Disconnected"

            current_provider = data.get("current_provider", "N/A")
            current_model = data.get("current_model", "N/A")

            health_message = (
                f"{status_emoji} *Claudio Server Status*\n\n"
                f"Server: {data.get('status', 'unknown')}\n"
                f"Provider: {current_provider}\n"
                f"Model: {current_model}\n"
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
# API KEY MANAGEMENT COMMANDS
# ============================================

async def addkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start the process to add an API key"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    args = context.args if hasattr(context, 'args') else []

    if not args:
        await update.message.reply_text(
            "🔐 *Add API Key*\n\n"
            "Usage: /addkey <provider>\n\n"
            "Available providers:\n"
            "• anthropic\n"
            "• openai\n"
            "• gemini\n"
            "• qwen\n"
            "• deepseek\n"
            "• glm\n\n"
            "Example: /addkey gemini\n\n"
            "After this command, send me your API key in a separate message. "
            "The key will be hidden and stored securely.",
            parse_mode='Markdown'
        )
        return

    provider = args[0].lower()

    # Validate provider
    valid_providers = ['anthropic', 'openai', 'gemini', 'qwen', 'deepseek', 'glm', 'ollama']
    if provider not in valid_providers:
        await update.message.reply_text(
            f"❌ Invalid provider '{provider}'\n\n"
            f"Valid providers: {', '.join(valid_providers)}"
        )
        return

    # Store the pending operation
    user_id = update.effective_user.id
    pending_key_operations[user_id] = {
        'provider': provider,
        'timestamp': None
    }

    # Send instructions for secure key input
    await update.message.reply_text(
        f"🔐 *Adding API Key for {provider.title()}*\n\n"
        f"Please send me your API key in the next message.\n\n"
        f"📝 *Format guidelines:*\n"
        f"• The key will be automatically hidden after processing\n"
        f"• Make sure the key is valid and active\n"
        f"• You can cancel with /cancel\n\n"
        f"⏳ *Waiting for your key...*",
        parse_mode='Markdown'
    )

    return WAITING_FOR_API_KEY


async def receive_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive and process the API key"""
    user_id = update.effective_user.id

    # Check if user is in the middle of adding a key
    if user_id not in pending_key_operations:
        return ConversationHandler.END

    # Get the API key from the message
    api_key = update.message.text.strip()

    # Get provider
    provider = pending_key_operations[user_id]['provider']

    # Validate the key format
    if not validate_api_key_format(provider, api_key):
        await update.message.reply_text(
            f"❌ *Invalid API key format for {provider.title()}*\n\n"
            f"Please check your key and try again.\n"
            f"Use /cancel to abort.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END

    # Try to delete the message with the key for security
    try:
        await update.message.delete()
    except:
        pass

    # Update the .env file
    success = await update_env_file(provider, api_key)

    if not success:
        await update.message.reply_text(
            "❌ Failed to update API key. Please check server logs."
        )
        del pending_key_operations[user_id]
        return ConversationHandler.END

    # Mask the key for display
    masked_key = mask_api_key(api_key)

    # Show success message
    await update.message.reply_text(
        f"✅ *API Key Added Successfully*\n\n"
        f"Provider: {provider.title()}\n"
        f"Key: `{masked_key}`\n\n"
        f"🔄 Restarting server to apply changes...\n\n"
        f"This will take a few seconds...",
        parse_mode='Markdown'
    )

    # Restart services via API
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            # Call reload endpoint to restart server with new config
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/reload",
                timeout=10.0
            )
            response.raise_for_status()

        await update.message.reply_text(
            "✅ *Server Restarted*\n\n"
            f"The new API key is now active.\n"
            f"You can switch to this provider with:\n"
            f"/switch {provider}",
            parse_mode='Markdown'
        )
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ API key saved to .env, but auto-restart failed.\n\n"
            f"Please restart manually:\n"
            f"`sudo systemctl restart claudio-server`\n\n"
            f"Error: {str(e)}",
            parse_mode='Markdown'
        )

    # Clear the pending operation
    del pending_key_operations[user_id]

    return ConversationHandler.END


async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current operation"""
    user_id = update.effective_user.id

    if user_id in pending_key_operations:
        del pending_key_operations[user_id]

    await update.message.reply_text(
        "❌ Operation cancelled.\n\n"
        "Your API key was NOT saved."
    )

    return ConversationHandler.END


async def listkeys_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all configured API keys (masked)"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    # Read current API keys from environment
    keys_info = {
        'Anthropic': {
            'key': os.getenv('ANTHROPIC_API_KEY', ''),
            'env': 'ANTHROPIC_API_KEY'
        },
        'OpenAI': {
            'key': os.getenv('OPENAI_API_KEY', ''),
            'env': 'OPENAI_API_KEY'
        },
        'Gemini': {
            'key': os.getenv('GEMINI_API_KEY', ''),
            'env': 'GEMINI_API_KEY'
        },
        'Qwen': {
            'key': os.getenv('QWEN_API_KEY', ''),
            'env': 'QWEN_API_KEY'
        },
        'DeepSeek': {
            'key': os.getenv('DEEPSEEK_API_KEY', ''),
            'env': 'DEEPSEEK_API_KEY'
        },
        'GLM': {
            'key': os.getenv('GLM_API_KEY', ''),
            'env': 'GLM_API_KEY'
        }
    }

    message = "🔐 *Configured API Keys*\n\n"

    for name, info in keys_info.items():
        key = info['key']
        if key:
            masked = mask_api_key(key)
            message += f"✅ {name}: `{masked}`\n"
        else:
            message += f"❌ {name}: *Not configured*\n"

    message += "\n*Add a key:*\n/addkey <provider>\n"

    await update.message.reply_text(message, parse_mode='Markdown')


# ============================================
# ADMIN COMMANDS - DYNAMIC MODEL SWITCHING
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

        mode = data.get('mode', 'single')
        auto_fallback = data.get('auto_fallback', False)

        status_text = (
            f"📊 *Model Status*\n\n"
            f"Mode: {'🔄 Dynamic' if mode == 'dynamic-multi' else '📌 Single'}\n"
            f"Provider: {data['current_provider']}\n"
            f"Model: {data['current_model']}\n"
            f"Auto-fallback: {'✅ Enabled' if auto_fallback else '❌ Disabled'}\n\n"
        )

        if mode == 'dynamic-multi':
            status_text += "*Available Providers:*\n"
            providers_info = data.get('providers_info', {})
            for name, info in providers_info.items():
                current = " 🔸" if info.get('current') else ""
                configured = "✅" if info.get('configured') else "❌"
                model = info.get('model', 'N/A')
                status_text += f"{configured} {name}{current}: {model}\n"

            status_text += f"\n*Fallback Order:*\n{', '.join(data.get('fallback_order', []))}"

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

        mode = data.get('mode', 'single')

        models_text = f"📋 *Available Models*\n\nMode: *{mode}*\n\n"

        if mode == 'dynamic-multi':
            providers = data.get('providers', {})
            current = data.get('current_provider', '')

            for name, info in providers.items():
                is_current = " 🔸" if name == current else ""
                configured = "✅" if info.get('configured') else "❌"
                ptype = info.get('type', 'unknown')
                model = info.get('model', 'N/A')
                models_text += f"{configured} *{name}*{is_current}\n"
                models_text += f"  Type: {ptype}\n"
                models_text += f"  Model: {model}\n"
                if info.get('base_url'):
                    models_text += f"  URL: {info['base_url']}\n"
                models_text += "\n"
        else:
            providers = data.get('providers', {})
            for name, info in providers.items():
                configured = "✅" if info.get('configured') else "❌"
                model = info.get('model', 'N/A')
                models_text += f"{configured} *{name}*\n"
                models_text += f"  Model: {model}\n\n"

        await update.message.reply_text(models_text, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to list models: {str(e)}")


async def switch_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Switch to a different model dynamically"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    args = context.args if hasattr(context, 'args') else []

    if not args:
        await update.message.reply_text(
            "🔄 *Switch Model*\n\n"
            "Usage: /switch <provider>\n\n"
            "Available providers:\n"
            "• anthropic\n"
            "• openai\n"
            "• gemini\n"
            "• qwen\n"
            "• deepseek\n"
            "• glm\n"
            "• ollama\n\n"
            "Example: /switch openai\n\n"
            "💡 In dynamic mode, this switches instantly without restart!",
            parse_mode='Markdown'
        )
        return

    try:
        new_provider = args[0].lower()

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{CLADIO_SERVER_URL}/api/admin/switch-model",
                json={
                    "user_id": update.effective_user.id,
                    "new_provider": new_provider
                }
            )
            response.raise_for_status()
            data = response.json()

            if data.get("requires_restart"):
                await update.message.reply_text(
                    f"⚠️ {data['message']}\n\n"
                    f"Para habilitar cambio dinámico:\n"
                    f"1. Edita .env: AI_PROVIDER=multi\n"
                    f"2. Reinicia: sudo systemctl restart claudio-server"
                )
            else:
                old = data.get('old_provider', 'unknown')
                new = data.get('new_provider', 'unknown')
                await update.message.reply_text(
                    f"✅ {data['message']}\n\n"
                    f"Provider changed: {old} → {new}\n"
                    f"Next message will use the new model."
                )

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to switch model: {str(e)}")


async def addmodel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a custom model (redirects to /addkey for standard providers)"""
    if not check_admin_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have admin permission.")
        return

    await update.message.reply_text(
        "➕ *Add Custom Model*\n\n"
        "For standard providers (Anthropic, OpenAI, Gemini, etc.),\n"
        "use the new secure command:\n\n"
        "🔐 /addkey <provider>\n\n"
        "This will:\n"
        "• Prompt you for the API key securely\n"
        "• Hide the key after input\n"
        "• Update .env automatically\n"
        "• Restart the server\n\n"
        "Example: /addkey gemini",
        parse_mode='Markdown'
    )


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
        "*🔐 API Key Management:*\n"
        "/addkey <provider> - Add API key securely 🔐\n"
        "/listkeys - Show configured keys (masked)\n\n"
        "*🔄 Model Management:*\n"
        "/status - Show current model status\n"
        "/models - List all available models\n"
        "/switch <provider> - Switch provider dynamically\n"
        "/test - Test current model availability\n\n"
        "*🔧 System Commands:*\n"
        "/health - Check server health\n"
        "/clear - Clear conversation history\n"
        "/cancel - Cancel current operation\n\n"
        "*Available Providers:*\n"
        "anthropic, openai, gemini, qwen, deepseek, ollama\n\n"
        "*🔐 Security Features:*\n"
        "• API keys are automatically hidden\n"
        "• Key messages are deleted after processing\n"
        "• Keys are stored securely in .env\n"
        "• Only masked versions are displayed"
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
            try:
                await update.message.reply_text(response_text, parse_mode='Markdown')
            except Exception as e:
                logger.warning(f"Markdown parsing failed, falling back to pure text: {e}")
                await update.message.reply_text(response_text)
        else:
            # Split long messages
            chunks = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
            for chunk in chunks:
                try:
                    await update.message.reply_text(chunk, parse_mode='Markdown')
                except Exception as e:
                    logger.warning(f"Markdown parsing failed for chunk, falling back to pure text: {e}")
                    await update.message.reply_text(chunk)

        logger.info(f"Claudio response to {user_id}: {response_text[:100]}...")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(
            f"❌ Error: {str(e)}\n\n"
            f"💡 Use /health to check if Claudio server is running.\n"
            f"💡 Use /switch <provider> to try a different AI model."
        )


def main() -> None:
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
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
    application.add_handler(CommandHandler("listkeys", listkeys_command))

    # Conversation handler for API key input
    addkey_handler = ConversationHandler(
        entry_points=[CommandHandler("addkey", addkey_command)],
        states={
            WAITING_FOR_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_api_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel_operation)],
    )
    application.add_handler(addkey_handler)

    # Regular message handler (must be last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("Claudio Telegram Bot starting...")
    logger.info(f"Claudio Server: {CLADIO_SERVER_URL}")
    logger.info(f"Admin users: {ALLOWED_ADMIN_USERS}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
