#!/usr/bin/env python3
"""
Telegram Bot powered by Claude AI
Deploy on VPS for 24/7 availability
"""

import os
import logging
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from anthropic import Anthropic

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []

# Claude client
claude = Anthropic(api_key=ANTHROPIC_API_KEY)

# Conversation history per user
conversation_history = {}


def check_permission(user_id: int) -> bool:
    """Check if user is allowed to use the bot"""
    if not ALLOWED_USERS:
        return True  # Allow all if no restriction
    return str(user_id) in ALLOWED_USERS


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    if not check_permission(update.effective_user.id):
        await update.message.reply_text("⛔ You don't have permission to use this bot.")
        return

    welcome_message = (
        "🤖 *Claude Telegram Bot*\n\n"
        "I'm Claude, powered by Anthropic's AI.\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/clear - Clear conversation history\n"
        "/help - Show help\n\n"
        "Just send me a message to chat!"
    )
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    help_text = (
        "📚 *Help*\n\n"
        "• Send any text message to chat with Claude\n"
        "• Use /clear to reset conversation\n"
        "• Context is remembered per user\n"
        "• Supports markdown formatting"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear conversation history"""
    user_id = update.effective_user.id
    if user_id in conversation_history:
        del conversation_history[user_id]
    await update.message.reply_text("🧹 Conversation history cleared.")


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
        # Get or initialize conversation history
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Add user message to history
        conversation_history[user_id].append({
            "role": "user",
            "content": user_message
        })

        # Call Claude API
        logger.info(f"User {user_id} ({user_name}): {user_message}")

        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system="You are Claude, a helpful AI assistant created by Anthropic. You are communicating through Telegram. Be concise and helpful.",
            messages=conversation_history[user_id]
        )

        # Extract response
        assistant_message = response.content[0].text

        # Add assistant response to history
        conversation_history[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # Keep only last 20 messages to avoid token limits
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        # Send response (handle Telegram message length limit)
        max_length = 4096
        if len(assistant_message) <= max_length:
            await update.message.reply_text(assistant_message, parse_mode='Markdown')
        else:
            # Split long messages
            chunks = [assistant_message[i:i+max_length] for i in range(0, len(assistant_message), max_length)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')

        logger.info(f"Claude response to {user_id}: {assistant_message[:100]}...")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


def main() -> None:
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable not set")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start bot
    logger.info("🤖 Claude Telegram Bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
