#!/usr/bin/env python3
"""
Claudio Server - Multi-AI Provider Support with Dynamic Switching
Supports Anthropic, OpenAI, Gemini 2.5/3.1, Qwen, DeepSeek, Ollama, and multi-provider configurations
Version 4.6.1 - Complete Provider Configuration with Ollama Support
"""

import os
import sys
import json
import logging
import asyncio
import signal
import re
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import httpx
from dotenv import load_dotenv

# AI Provider imports
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.genai as genai
    GEMINI_AVAILABLE = True
    GEMINI_NEW_API = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        GEMINI_NEW_API = False
    except ImportError:
        GEMINI_AVAILABLE = False
        GEMINI_NEW_API = False

# Load environment variables
load_dotenv()

# Add skills directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database and skills
from n8n_database import (
    N8N_NODES_CORE, N8N_NODES_COMMUNITY, N8N_TEMPLATES,
    N8N_VALIDATION_PROFILES, N8N_EXPRESSION_PATTERNS, N8N_COMMON_ISSUES
)

# Import specialized skills
from skills.n8n_expression_syntax import ExpressionSyntaxExpert
from skills.n8n_other_skills import (
    MCPToolsExpert,
    WorkflowPatternsExpert,
    ValidationExpert,
    NodeConfigExpert,
    CodeJavaScriptExpert,
    CodePythonExpert
)

# Configure logging - use absolute path for systemd service
LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / 'claudio_complete.log'
file_handler = logging.FileHandler(str(LOG_FILE), encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# ============================================
# ENVIRONMENT VARIABLES
# ============================================

# AI Provider Configuration
AI_PROVIDER = os.getenv('AI_PROVIDER', 'anthropic').lower()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-pro')
QWEN_API_KEY = os.getenv('QWEN_API_KEY')
QWEN_BASE_URL = os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-plus')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
GLM_API_KEY = os.getenv('GLM_API_KEY')
GLM_BASE_URL = os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')
GLM_MODEL = os.getenv('GLM_MODEL', 'glm-4-flash')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

# Custom model support
CUSTOM_MODEL_NAME = os.getenv('CUSTOM_MODEL_NAME', '')
CUSTOM_MODEL_API_KEY = os.getenv('CUSTOM_MODEL_API_KEY', '')
CUSTOM_MODEL_BASE_URL = os.getenv('CUSTOM_MODEL_BASE_URL', '')
CUSTOM_MODEL_PROVIDER = os.getenv('CUSTOM_MODEL_PROVIDER', 'openai')

# Fallback configuration
AUTO_FALLBACK = os.getenv('AUTO_FALLBACK', 'true').lower() == 'true'
FALLBACK_ORDER = os.getenv('FALLBACK_ORDER', 'anthropic,openai,gemini,qwen,deepseek,ollama').split(',')

# Notification bot configuration
BOT_NOTIFICATION_URL = os.getenv('BOT_NOTIFICATION_URL', '')
ALLOWED_ADMIN_USERS = os.getenv('ALLOWED_ADMIN_USERS', '').split(',') if os.getenv('ALLOWED_ADMIN_USERS') else []

# n8n Configuration
N8N_API_KEY = os.getenv('N8N_API_KEY')
N8N_INSTANCE_URL = os.getenv('N8N_INSTANCE_URL', 'https://localhost')
N8N_HOST_HEADER = os.getenv('N8N_HOST_HEADER', 'n8n.aicorebots.com')

# Server Configuration
PORT = int(os.getenv('CLADIO_PORT', '8000'))
CLADIO_SERVER_URL = os.getenv('CLADIO_SERVER_URL', f'http://localhost:{PORT}')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))

# ============================================
# AI PROVIDER CLASSES
# ============================================

class AIProvider:
    """Base class for AI providers"""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Send chat request and return response"""
        raise NotImplementedError

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return bool(self.api_key)


class AnthropicProvider(AIProvider):
    """Anthropic Claude AI provider"""

    def __init__(self, api_key: str, model: str = 'claude-sonnet-4-20250514'):
        super().__init__(api_key, model)
        if ANTHROPIC_AVAILABLE and api_key:
            self.client = Anthropic(api_key=api_key)

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("Anthropic client not initialized")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    async def is_available(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(self.api_key)


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider with async support"""

    def __init__(self, api_key: str, model: str = 'gpt-4o'):
        super().__init__(api_key, model)
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("OpenAI client not initialized")

        # Add system prompt as first message
        all_messages = [{"role": "system", "content": system_prompt}] + messages

        # Run in thread pool to avoid blocking event loop
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                max_tokens=4096,
                timeout=30.0  # 30 second timeout for OpenAI API
            )
        )

        return response.choices[0].message.content

    async def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)


class OllamaProvider(AIProvider):
    """Ollama local AI provider"""

    def __init__(self, base_url: str, model: str = 'llama3'):
        self.base_url = base_url
        self.model = model
        self.api_key = "not-needed"

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        # Convert messages to Ollama format
        prompt = f"System: {system_prompt}\n\n"
        for msg in messages:
            role = msg['role'].capitalize()
            prompt += f"{role}: {msg['content']}\n"
        prompt += "Assistant:"

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', '')

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False


class GeminiProvider(AIProvider):
    """Google Gemini AI provider - compatible API"""

    def __init__(self, api_key: str, model: str = 'gemini-2.0-flash-exp'):
        super().__init__(api_key, model)
        self.use_new_api = False

        if GEMINI_AVAILABLE and api_key:
            try:
                # Use the old/generativeai API (more stable)
                import google.generativeai as genai_old
                genai_old.configure(api_key=api_key)
                self.client = genai_old.GenerativeModel(model)
                self.use_new_api = False
            except Exception as e:
                logger.warning(f"Gemini initialization failed: {e}")
                self.client = None

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("Gemini client not initialized")

        try:
            # Build prompt with system instruction
            full_prompt = f"{system_prompt}\n\n"

            for msg in messages:
                role = msg['role']
                content = msg['content']
                if role == 'user':
                    full_prompt += f"User: {content}\n"
                elif role == 'assistant':
                    full_prompt += f"Assistant: {content}\n"

            full_prompt += "Assistant:"

            # Generate response
            response = await asyncio.to_thread(
                self.client.generate_content,
                full_prompt,
                generation_config={"max_output_tokens": 4096}
            )
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise ValueError(f"Gemini API error: {e}")

    async def is_available(self) -> bool:
        return GEMINI_AVAILABLE and bool(self.api_key) and self.client is not None


class QwenProvider(AIProvider):
    """Alibaba Qwen AI provider (OpenAI-compatible)"""

    def __init__(self, api_key: str, base_url: str = 'https://dashscope.aliyuncs.com/compatible-mode/v1', model: str = 'qwen-plus'):
        super().__init__(api_key, model)
        self.base_url = base_url
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("Qwen client not initialized")

        # Add system prompt as first message
        all_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"Qwen API error: {e}")

    async def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)


class DeepSeekProvider(AIProvider):
    """DeepSeek AI provider (OpenAI-compatible)"""

    def __init__(self, api_key: str, base_url: str = 'https://api.deepseek.com', model: str = 'deepseek-chat'):
        super().__init__(api_key, model)
        self.base_url = base_url
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("DeepSeek client not initialized")

        # Add system prompt as first message
        all_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"DeepSeek API error: {e}")

    async def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)


class GLMProvider(AIProvider):
    """GLM (z.ai / BigModel) AI provider (OpenAI-compatible)"""

    def __init__(self, api_key: str, base_url: str = 'https://open.bigmodel.cn/api/paas/v4', model: str = 'glm-4-flash'):
        super().__init__(api_key, model)
        self.base_url = base_url
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("GLM client not initialized")

        # Add system prompt as first message
        all_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                max_tokens=4096
            )
            return response.choices[0].message.content
        except Exception as e:
            raise ValueError(f"GLM API error: {e}")

    async def is_available(self) -> bool:
        return OPENAI_AVAILABLE and bool(self.api_key)


class CustomProvider(AIProvider):
    """Custom AI provider for user-defined models (OpenAI or Anthropic compatible)"""

    def __init__(self, name: str, api_key: str, base_url: str, model: str, provider_type: str = 'openai'):
        super().__init__(api_key, model)
        self.name = name
        self.base_url = base_url
        self.provider_type = provider_type

        if provider_type == 'openai' and OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        elif provider_type == 'anthropic' and ANTHROPIC_AVAILABLE and api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            self.client = None

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError(f"Custom provider '{self.name}' not initialized")

        if self.provider_type == 'openai':
            all_messages = [{"role": "system", "content": system_prompt}] + messages
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=all_messages,
                    max_tokens=4096
                )
                return response.choices[0].message.content
            except Exception as e:
                raise ValueError(f"Custom provider API error: {e}")

        elif self.provider_type == 'anthropic':
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=system_prompt,
                    messages=messages
                )
                return response.content[0].text
            except Exception as e:
                raise ValueError(f"Custom provider API error: {e}")

        raise ValueError(f"Unsupported provider type: {self.provider_type}")

    async def is_available(self) -> bool:
        return self.client is not None

    def get_name(self) -> str:
        return self.name


class DynamicMultiProvider(AIProvider):
    """Dynamic multi-provider with runtime switching and automatic fallback"""

    def __init__(self, notification_callback=None):
        self.api_key = "dynamic"
        self.notification_callback = notification_callback
        self.providers = {}  # name -> provider instance
        self.current_provider = None
        self.provider_order = []  # Priority order
        self.failed_providers = {}  # Track failed providers with timestamps

        # Load all available providers
        self._load_providers()

    def _load_providers(self):
        """Load all configured providers"""
        if ANTHROPIC_API_KEY:
            self.providers['anthropic'] = AnthropicProvider(ANTHROPIC_API_KEY, ANTHROPIC_MODEL)
            self.provider_order.append('anthropic')

        if OPENAI_API_KEY:
            self.providers['openai'] = OpenAIProvider(OPENAI_API_KEY, OPENAI_MODEL)
            if 'openai' not in self.provider_order:
                self.provider_order.append('openai')

        if GEMINI_API_KEY:
            self.providers['gemini'] = GeminiProvider(GEMINI_API_KEY, GEMINI_MODEL)
            if 'gemini' not in self.provider_order:
                self.provider_order.append('gemini')

        if QWEN_API_KEY:
            self.providers['qwen'] = QwenProvider(QWEN_API_KEY, QWEN_BASE_URL, QWEN_MODEL)
            if 'qwen' not in self.provider_order:
                self.provider_order.append('qwen')

        if DEEPSEEK_API_KEY:
            self.providers['deepseek'] = DeepSeekProvider(DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL)
            if 'deepseek' not in self.provider_order:
                self.provider_order.append('deepseek')

        if GLM_API_KEY:
            self.providers['glm'] = GLMProvider(GLM_API_KEY, GLM_BASE_URL, GLM_MODEL)
            if 'glm' not in self.provider_order:
                self.provider_order.append('glm')

        # Always add Ollama (will check availability dynamically)
        self.providers['ollama'] = OllamaProvider(OLLAMA_BASE_URL, OLLAMA_MODEL)
        if 'ollama' not in self.provider_order:
            self.provider_order.append('ollama')

        # Custom model
        if CUSTOM_MODEL_NAME and CUSTOM_MODEL_API_KEY:
            self.providers['custom'] = CustomProvider(
                name=CUSTOM_MODEL_NAME,
                api_key=CUSTOM_MODEL_API_KEY,
                base_url=CUSTOM_MODEL_BASE_URL,
                model=CUSTOM_MODEL_NAME,
                provider_type=CUSTOM_MODEL_PROVIDER
            )
            if 'custom' not in self.provider_order:
                self.provider_order.append('custom')

        # Set initial provider based on FALLBACK_ORDER
        if FALLBACK_ORDER:
            for provider_name in FALLBACK_ORDER:
                provider_name = provider_name.strip()
                if provider_name in self.providers:
                    self.current_provider = provider_name
                    break

        # Fallback to first available
        if not self.current_provider and self.provider_order:
            self.current_provider = self.provider_order[0]

        logger.info(f"DynamicMultiProvider loaded {len(self.providers)} providers: {list(self.providers.keys())}")
        logger.info(f"Current provider: {self.current_provider}")

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Try current provider, fallback to others on failure"""
        last_error = None

        # Get ordered providers (respect failed ones)
        available_providers = self._get_available_providers()

        for provider_name in available_providers:
            # Skip if recently failed
            if provider_name in self.failed_providers:
                fail_time = self.failed_providers[provider_name]
                if datetime.now().timestamp() - fail_time < 300:  # 5 min cooldown
                    logger.warning(f"Skipping {provider_name} (recently failed)")
                    continue
                else:
                    # Remove from failed list
                    del self.failed_providers[provider_name]

            provider = self.providers.get(provider_name)
            if not provider:
                continue

            try:
                # Check availability
                if not await provider.is_available():
                    logger.warning(f"Provider {provider_name} is not available")
                    continue

                # Try to get response
                response = await provider.chat(messages, system_prompt)

                # Success - update current if changed
                if provider_name != self.current_provider:
                    old = self.current_provider
                    self.current_provider = provider_name
                    logger.info(f"Switched provider: {old} -> {provider_name}")

                    if self.notification_callback:
                        await self.notification_callback(
                            message=f"🔄 Modelo cambiado: {old} → {provider_name}",
                            notification_type="model_switch"
                        )

                return response

            except Exception as e:
                last_error = e
                error_msg = str(e)

                # Check for quota/token errors
                if any(keyword in error_msg.lower() for keyword in ['quota', 'limit', 'token', 'insufficient', 'rate', 'credit']):
                    logger.warning(f"Provider {provider_name} quota error: {e}")
                    self.failed_providers[provider_name] = datetime.now().timestamp()

                    if self.notification_callback:
                        await self.notification_callback(
                            message=f"⚠️ Sin cuota en {provider_name}, cambiando de modelo...",
                            notification_type="quota_error"
                        )

                    # Try next provider
                    continue
                else:
                    logger.error(f"Provider {provider_name} error: {e}")
                    continue

        # All providers failed
        if last_error:
            if self.notification_callback:
                await self.notification_callback(
                    message=f"❌ Todos los modelos fallaron. Último error: {str(last_error)}",
                    notification_type="all_providers_failed"
                )
            raise last_error

        raise ValueError("No AI providers available")

    def _get_available_providers(self) -> List[str]:
        """Get ordered list of providers to try"""
        # If AUTO_FALLBACK is enabled, try all in configured order
        if AUTO_FALLBACK:
            ordered = []
            for name in FALLBACK_ORDER:
                name = name.strip()
                if name in self.providers and name not in ordered:
                    ordered.append(name)
            # Add any remaining providers
            for name in self.providers:
                if name not in ordered:
                    ordered.append(name)
            return ordered
        else:
            # Only try current provider
            return [self.current_provider] if self.current_provider else []

    async def is_available(self) -> bool:
        """Check if any provider is available"""
        for provider in self.providers.values():
            try:
                if await provider.is_available():
                    return True
            except:
                continue
        return False

    def force_switch(self, provider_name: str) -> bool:
        """Force switch to a specific provider"""
        provider_name = provider_name.lower()
        if provider_name in self.providers:
            old = self.current_provider
            self.current_provider = provider_name
            # Clear failed status
            if provider_name in self.failed_providers:
                del self.failed_providers[provider_name]
            logger.info(f"Force switched provider: {old} -> {provider_name}")
            return True
        return False

    def add_custom_provider(self, provider: AIProvider):
        """Add a custom provider dynamically"""
        if hasattr(provider, 'name'):
            name = provider.name
        else:
            name = provider.__class__.__name__.replace("Provider", "").lower()

        self.providers[name] = provider
        if name not in self.provider_order:
            self.provider_order.append(name)
        logger.info(f"Added custom provider: {name}")

    def get_available_providers(self) -> List[str]:
        """Get list of configured provider names"""
        return list(self.providers.keys())

    def get_current_provider(self) -> str:
        """Get the currently active provider name"""
        return self.current_provider or "Unknown"

    def get_current_model(self) -> str:
        """Get current model name"""
        provider = self.providers.get(self.current_provider)
        if provider:
            return getattr(provider, 'model', 'N/A')
        return 'N/A'

    def get_provider_info(self) -> Dict[str, Any]:
        """Get detailed info about all providers"""
        info = {}
        for name, provider in self.providers.items():
            info[name] = {
                'type': provider.__class__.__name__,
                'model': getattr(provider, 'model', 'N/A'),
                'configured': bool(getattr(provider, 'api_key', True) or getattr(provider, 'client', None)),
                'current': (name == self.current_provider)
            }
            if hasattr(provider, 'base_url'):
                info[name]['base_url'] = provider.base_url
        return info


# ============================================
# NOTIFICATION SYSTEM
# ============================================

async def send_bot_notification(message: str, notification_type: str = "info"):
    """Send notification to Telegram bot"""
    if not BOT_NOTIFICATION_URL:
        return

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                BOT_NOTIFICATION_URL,
                json={
                    "message": message,
                    "type": notification_type,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=5.0
            )
    except Exception as e:
        logger.warning(f"Failed to send bot notification: {e}")


# ============================================
# INITIALIZE AI PROVIDER
# ============================================

def create_ai_provider() -> AIProvider:
    """Create the appropriate AI provider"""

    if AI_PROVIDER == 'multi':
        # Use new dynamic multi-provider
        return DynamicMultiProvider(notification_callback=send_bot_notification)

    # Single provider modes (for backward compatibility)
    elif AI_PROVIDER == 'anthropic':
        return AnthropicProvider(
            api_key=ANTHROPIC_API_KEY or '',
            model=ANTHROPIC_MODEL
        )

    elif AI_PROVIDER == 'openai':
        return OpenAIProvider(
            api_key=OPENAI_API_KEY or '',
            model=OPENAI_MODEL
        )

    elif AI_PROVIDER == 'gemini':
        return GeminiProvider(
            api_key=GEMINI_API_KEY or '',
            model=GEMINI_MODEL
        )

    elif AI_PROVIDER == 'qwen':
        return QwenProvider(
            api_key=QWEN_API_KEY or '',
            base_url=QWEN_BASE_URL,
            model=QWEN_MODEL
        )

    elif AI_PROVIDER == 'deepseek':
        return DeepSeekProvider(
            api_key=DEEPSEEK_API_KEY or '',
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL
        )

    elif AI_PROVIDER == 'glm':
        return GLMProvider(
            api_key=GLM_API_KEY or '',
            base_url=GLM_BASE_URL,
            model=GLM_MODEL
        )

    elif AI_PROVIDER == 'ollama':
        return OllamaProvider(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL
        )

    elif AI_PROVIDER == 'custom' and CUSTOM_MODEL_NAME:
        return CustomProvider(
            name=CUSTOM_MODEL_NAME,
            api_key=CUSTOM_MODEL_API_KEY,
            base_url=CUSTOM_MODEL_BASE_URL,
            model=CUSTOM_MODEL_NAME,
            provider_type=CUSTOM_MODEL_PROVIDER
        )

    else:
        logger.warning(f"Unknown provider '{AI_PROVIDER}', falling back to dynamic multi-provider")
        return DynamicMultiProvider(notification_callback=send_bot_notification)


# Initialize AI provider
ai_provider = create_ai_provider()

# ============================================
# SYSTEM PROMPT
# ============================================

CLAUDIO_COMPLETE_PROMPT = """You are Claudio, an expert n8n workflow automation specialist with COMPLETE ACCESS to n8n.

## YOUR CAPABILITIES

## HOW YOU GET DATA

The system automatically intercepts user requests, executes necessary n8n API requests, and injects the live results under the section `[Acciones Ejecutadas]` at the end of the user's message.
**DO NOT attempt to invoke any tools, functions, or write `[Tool Execution]`**. Just read the `[Acciones Ejecutadas]` block, and answer the user naturally based on that data!

### ANTI-HALLUCINATION RULES (STRICT STRICT STRICT)
1. **Never invent data**: If the user asks for their workflows and `[Acciones Ejecutadas]` does not show any, or says `0` workflows, you MUST reply clearly say there are zero workflows.
2. **Never guess**: If the `[Acciones Ejecutadas]` block is empty or missing, say: "No tengo acceso a esa información en este momento" or similarly. DO NOT invent fake workflows, nodes, or execution states.
3. **Be factual**: Stick exactly to the counts, names, and information provided in `[Acciones Ejecutadas]`.

### DATABASE KNOWLEDGE
- **1396 n8n nodes** (812 core + 584 community)
- **2709+ workflow templates**
- Complete node documentation
- Parameter requirements and defaults
- Common issues and solutions

### 7 SPECIALIZED SKILLS
1. **Expression Syntax** - Validate {{}} patterns, $json, $node
2. **MCP Tools Expert** - Tool selection and usage
3. **Workflow Patterns** - 5 proven patterns from templates
4. **Validation Expert** - Multi-level validation
5. **Node Configuration** - Operation-aware setup
6. **JavaScript Code** - Code node best practices
7. **Python Code** - Python limitations and workarounds

## CRITICAL RULES

1. **NEVER TRUST DEFAULTS** - 60%+ of failures are from default parameters
2. **Webhook Data** - ALWAYS use `$json.body`, never `$json`
3. **IF Node** - Use `branch="true"` or `branch="false"` for connections
4. **HTTP Body** - MUST set `sendBody=true` for POST/PUT/PATCH
5. **Node References** - Use `$node["Name"]` with brackets for spaces

## EXPRESSION SYNTAX

| Context | Correct | Wrong |
|---------|---------|-------|
| Webhook body | `$json.body.field` | `$json.field` ❌ |
| Node with spaces | `$node["HTTP Request"]` | `$node.HTTP Request` ❌ |
| Array access | `$json.items[0]` | `$json.items.0` ❌ |
| Environment | `$env.API_KEY` | N/A |
| Previous node | `$node["Node Name"].json.result` | N/A |

## WORKFLOW PATTERNS

1. **Webhook Processing**: Webhook → Parse → Process → Response
2. **HTTP API**: Schedule → HTTP Request → Process → Notify
3. **Database**: Trigger → Query → Transform → Update
4. **AI Agent**: Trigger → AI Agent → Tools → Response
5. **Batch**: Trigger → Split → Process → Aggregate

## NODE KNOWLEDGE

You have detailed info on 1396 nodes including:
- Required/optional parameters
- Authentication needs
- Common issues
- Code examples
- Connection requirements

## ACTION CONFIRMATION (CRITICAL)

When the `[Acciones Ejecutadas]` section shows that the system has performed an action (like fetching workflows, searching nodes, deleting workflows, etc.), you MUST:

1. **Confirm what the system did**: "He encontrado X workflows" or "Se eliminaron Y workflows"
2. **Report success/failure clearly**: "✓ Completado" or "✗ Error: razón" (based on the injected data)
3. **Provide details**: List what was done, what worked, what failed based on the injected data.
4. **Never stay silent**: Always acknowledge user requests.

### Action Confirmation Format Example:
```
✅ ACCIÓN COMPLETADA: Encontrar workflows
- Encontrados: 5 workflows
- Detalles: [lista de resultados]
```

```
❌ ACCIÓN FALLIDA: [acción intentada]
- Error: [razón del error tomada de Acciones Ejecutadas]
- Solución: [qué hacer]
```

You communicate through Telegram. Be practical and precise. Focus on working solutions.
"""

# Conversation history
conversation_history: Dict[int, List[Dict[str, str]]] = {}

# ============================================
# N8N MCP TOOLS IMPLEMENTATION
# ============================================

class N8NMCPTools:
    """Complete n8n-MCP tools implementation with real database"""

    def __init__(self):
        self.base_url = f"{N8N_INSTANCE_URL}/api/v1"
        self.headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json",
            "Host": N8N_HOST_HEADER
        }
        # Load complete node database
        self.nodes = {**N8N_NODES_CORE, **N8N_NODES_COMMUNITY}
        self.templates = N8N_TEMPLATES

    async def search_nodes(
        self,
        query: str = "",
        category: str = "",
        source: str = "all"
    ) -> List[Dict[str, Any]]:
        """Search in 1396 n8n nodes"""
        results = []
        query_lower = query.lower()

        for node_id, node_info in self.nodes.items():
            # Filter by source
            if source == "core" and node_id.startswith("@"):
                continue
            if source == "community" and not node_id.startswith("@"):
                continue

            # Handle both dict and string node_info
            if isinstance(node_info, str):
                node_dict = {"id": node_id, "description": node_info, "category": "community"}
            else:
                node_dict = {"id": node_id, **node_info}

            # Filter by category
            if category and node_dict.get("category") != category:
                continue

            # Search query
            if query:
                searchable_text = f"{node_id} {node_dict.get('description', '')} {node_dict.get('category', '')}".lower()
                if query_lower in searchable_text:
                    results.append(node_dict)
            else:
                results.append(node_dict)

        return results[:50]

    async def get_node(
        self,
        node_type: str,
        detail: str = "full"
    ) -> Dict[str, Any]:
        """Get detailed node information"""
        if node_type not in self.nodes:
            return {"error": f"Node {node_type} not found"}

        node_info = self.nodes[node_type]

        if detail == "full":
            return {
                "nodeType": node_type,
                "category": node_info.get("category"),
                "description": node_info.get("description"),
                "parameters": node_info.get("parameters", {}),
                "common_issues": node_info.get("common_issues", []),
                "examples": node_info.get("examples", [])
            }
        return {"nodeType": node_type, **node_info}

    async def search_templates(
        self,
        query: str = "",
        category: str = "",
        complexity: str = ""
    ) -> List[Dict[str, Any]]:
        """Search in workflow templates"""
        results = []
        query_lower = query.lower()

        for template_id, template_info in self.templates.items():
            # Filter by category
            if category and template_info.get("category") != category:
                continue

            # Filter by complexity
            if complexity and template_info.get("complexity") != complexity:
                continue

            # Search query
            if query_lower:
                if (query_lower in template_info["name"].lower() or
                    query_lower in template_info.get("description", "").lower() or
                    any(query_lower in tag.lower() for tag in template_info.get("tags", []))):
                    results.append(template_info)
            else:
                results.append(template_info)

        return results[:20]

    async def validate_expression(
        self,
        expression: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Validate n8n expression syntax"""
        result = {"valid": True, "errors": [], "warnings": [], "suggestions": []}

        # Check webhook body access
        if "webhook" in context.lower():
            if re.search(r'\$json(?!\.body)', expression):
                result["valid"] = False
                result["errors"].append({
                    "error": "Using $json instead of $json.body for webhook",
                    "fix": "Use $json.body.field instead of $json.field"
                })

        # Check node references
        if re.search(r'\$node\.[a-zA-Z]+', expression):
            result["warnings"].append({
                "warning": "Node reference may need bracket notation",
                "suggestion": 'Use $node["Node Name"] for nodes with spaces'
            })

        # Check array access
        if re.search(r'\$json\.[a-z]+\.\d+', expression):
            result["valid"] = False
            result["errors"].append({
                "error": "Array access with dot notation",
                "fix": "Use brackets: $json.items[0] instead of $json.items.0"
            })

        return result

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows from n8n"""
        if not N8N_API_KEY:
            return {"error": "N8N_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.get(
                    f"{self.base_url}/workflows",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", data) if isinstance(data, dict) else data
        except Exception as e:
            return {"error": str(e)}

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get specific workflow"""
        if not N8N_API_KEY:
            return {"error": "N8N_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.get(
                    f"{self.base_url}/workflows/{workflow_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new workflow in n8n"""
        if not N8N_API_KEY:
            return {"error": "N8N_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.post(
                    f"{self.base_url}/workflows",
                    headers=self.headers,
                    json=workflow_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def update_workflow(
        self,
        workflow_id: str,
        workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update workflow"""
        if not N8N_API_KEY:
            return {"error": "N8N_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(
                timeout=30,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.patch(
                    f"{self.base_url}/workflows/{workflow_id}",
                    headers=self.headers,
                    json=workflow_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate workflow"""
        if not N8N_API_KEY:
            return {"error": "N8N_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.post(
                    f"{self.base_url}/workflows/{workflow_id}/activate",
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete workflow from n8n"""
        if not N8N_API_KEY:
            return {"error": "N8N_API_KEY not configured"}

        try:
            async with httpx.AsyncClient(
                timeout=10,
                follow_redirects=True,
                verify=False
            ) as client:
                response = await client.delete(
                    f"{self.base_url}/workflows/{workflow_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return {"success": True, "message": f"Workflow {workflow_id} deleted"}
        except Exception as e:
            return {"error": str(e)}


# Initialize tools
n8n_tools = N8NMCPTools()

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Claudio - Multi-AI n8n Assistant",
    description="Expert n8n workflow automation with multi-AI provider support",
    version="4.6.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    user_id: int
    user_name: Optional[str] = "User"
    clear_history: bool = False


class ChatResponse(BaseModel):
    response: str
    timestamp: str
    model: str
    provider: str
    tools_used: List[str] = []
    context: Dict[str, Any] = {}


@app.get("/")
async def root():
    """Root endpoint"""
    current_provider = ai_provider.get_current_provider() if isinstance(ai_provider, DynamicMultiProvider) else AI_PROVIDER
    current_model = ai_provider.get_current_model() if isinstance(ai_provider, DynamicMultiProvider) else getattr(ai_provider, 'model', 'N/A')

    return {
        "service": "Claudio",
        "version": "4.6.1",
        "ai_provider": AI_PROVIDER,
        "current_provider": current_provider,
        "current_model": current_model,
        "features": [
            "Dynamic multi-AI provider support (switch without restart)",
            "Anthropic, OpenAI, Gemini, Qwen, DeepSeek, Ollama",
            "Real n8n API access",
            "1396 n8n nodes database",
            "2709+ workflow templates",
            "7 specialized skills",
            "Expression validation",
            "Node configuration guidance",
            "Workflow pattern recommendations"
        ],
        "stats": {
            "nodes": len(n8n_tools.nodes),
            "templates": len(n8n_tools.templates),
            "skills": 7,
            "ai_provider": AI_PROVIDER,
            "n8n_connected": N8N_INSTANCE_URL
        }
    }


@app.get("/health")
async def health_check():
    """Health check - n8n failures are non-fatal"""
    import asyncio

    # Try to check n8n with short timeout (3 seconds max)
    n8n_health = {"error": "timeout"}
    n8n_connected = False

    try:
        n8n_health = await asyncio.wait_for(n8n_tools.list_workflows(), timeout=3.0)
        n8n_connected = not isinstance(n8n_health, dict) or "error" not in n8n_health
    except asyncio.TimeoutError:
        n8n_health = {"error": "timeout"}
        n8n_connected = False
    except Exception as e:
        n8n_health = {"error": str(e)}
        n8n_connected = False

    ai_available = await ai_provider.is_available()

    current_provider = ai_provider.get_current_provider() if isinstance(ai_provider, DynamicMultiProvider) else AI_PROVIDER
    current_model = ai_provider.get_current_model() if isinstance(ai_provider, DynamicMultiProvider) else getattr(ai_provider, 'model', 'N/A')

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_provider": AI_PROVIDER,
        "current_provider": current_provider,
        "current_model": current_model,
        "ai_available": ai_available,
        "n8n": {
            "connected": n8n_connected,
            "instance": N8N_INSTANCE_URL,
            "has_api_key": bool(N8N_API_KEY),
            "error": n8n_health.get("error") if isinstance(n8n_health, dict) and "error" in n8n_health else None
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat with full tool access"""
    user_id = request.user_id
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Clear history if requested
        if request.clear_history and user_id in conversation_history:
            del conversation_history[user_id]

        # Get or initialize history
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Add user message
        conversation_history[user_id].append({
            "role": "user",
            "content": user_message
        })

        # Analyze and use tools
        tools_used = []
        tool_context = await analyze_and_use_tools(user_message)

        if tool_context:
            tools_used = list(tool_context.keys())
            enhanced_message = f"{user_message}\n\n[Tool Results]\n{json.dumps(tool_context, indent=2)}"
        else:
            enhanced_message = user_message

        # Call AI provider
        # Use globals() to access CLAUDIO_COMPLETE_PROMPT
        PROMPT = globals().get('CLAUDIO_COMPLETE_PROMPT', 'You are Claudio, an n8n expert.')

        # Add tool context to the user message so AI can use it
        final_message = enhanced_message
        if tool_context:
            context_info = "\n\n[Acciones Ejecutadas]\n"

            # Format deletion results clearly
            if "workflows_deleted" in tool_context:
                deleted = tool_context["workflows_deleted"]
                if "error" in deleted:
                    context_info += f"❌ ERROR ELIMINANDO WORKFLOWS: {deleted['error']}\n"
                else:
                    count = deleted.get('count', 0)
                    results = deleted.get('results', [])
                    context_info += f"✅ WORKFLOWS ELIMINADOS: {count} eliminados correctamente\n"
                    if results:
                        context_info += "Resultados:\n"
                        for r in results[:10]:  # Max 10 results
                            context_info += f"  {r}\n"

            # Format workflow list
            if "workflows" in tool_context and "workflows_deleted" not in tool_context:
                wf = tool_context["workflows"]
                count = wf.get('count', 0)
                context_info += f"📋 WORKFLOWS ENCONTRADOS: {count} workflows\n"
                recent = wf.get('recent', [])
                if recent:
                    context_info += "Workflows recientes:\n"
                    for w in recent[:5]:
                        context_info += f"  - {w.get('name', 'Unknown')} (ID: {w.get('id', 'N/A')})\n"

            # Format node search
            if "nodes" in tool_context:
                nodes = tool_context["nodes"]
                count = nodes.get('found', 0) if isinstance(nodes, dict) else len(nodes) if isinstance(nodes, list) else 0
                context_info += f"🔍 NODOS ENCONTRADOS: {count} nodos\n"

            # Format template search
            if "templates" in tool_context:
                templates = tool_context["templates"]
                count = len(templates) if isinstance(templates, list) else 0
                context_info += f"📄 TEMPLATES ENCONTRADOS: {count} templates\n"

            # Add any errors
            if "workflows_error" in tool_context:
                context_info += f"⚠️ ERROR: {tool_context['workflows_error']}\n"

            final_message = enhanced_message + context_info

        # Update the last message with tool context
        conversation_history[user_id][-1]["content"] = final_message

        response_text = await ai_provider.chat(
            messages=conversation_history[user_id],
            system_prompt=PROMPT
        )

        # Add to history
        conversation_history[user_id].append({
            "role": "assistant",
            "content": response_text
        })

        # Keep last 20
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        current_provider = ai_provider.get_current_provider() if isinstance(ai_provider, DynamicMultiProvider) else AI_PROVIDER
        current_model = ai_provider.get_current_model() if isinstance(ai_provider, DynamicMultiProvider) else getattr(ai_provider, 'model', 'N/A')

        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            model=current_model,
            provider=current_provider,
            tools_used=tools_used,
            context=tool_context
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_and_use_tools(message: str) -> Dict[str, Any]:
    """Analyze message and use appropriate tools - n8n errors are non-fatal"""
    import asyncio

    context = {}
    message_lower = message.lower()

    # Helper function to call n8n with timeout
    async def call_n8n_safe(coro, timeout=5.0, default=None):
        """Call n8n function with timeout, return default on failure"""
        try:
            result = await asyncio.wait_for(coro, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"n8n call timeout after {timeout}s")
            return default or {"error": "timeout"}
        except Exception as e:
            logger.warning(f"n8n call failed: {e}")
            return default or {"error": str(e)}

    # DELETE WORKFLOWS - Detect delete/eliminate commands
    if any(word in message_lower for word in ["eliminar", "borrar", "delete", "elimina", "borra"]):
        if any(word in message_lower for word in ["workflow", "workflows", "todo", "todos", "todos los", "all"]):
            workflows = await call_n8n_safe(n8n_tools.list_workflows(), timeout=5.0)
            if isinstance(workflows, list) and len(workflows) > 0:
                deleted_count = 0
                results = []
                for wf in workflows:
                    wf_id = wf.get("id")
                    wf_name = wf.get("name", "Unknown")
                    if wf_id:
                        result = await n8n_tools.delete_workflow(wf_id)
                        if "error" not in result:
                            deleted_count += 1
                            results.append(f"✓ Deleted: {wf_name}")
                        else:
                            results.append(f"✗ Failed: {wf_name} - {result.get('error', 'Unknown error')}")

                context["workflows_deleted"] = {
                    "count": deleted_count,
                    "results": results
                }
            else:
                context["workflows_deleted"] = {"error": "No workflows found or couldn't list workflows"}

    # Check workflows (list)
    if any(word in message_lower for word in ["workflow", "workflows", "mis workflows", "listar", "cuantos"]):
        # Don't list if already deleted (avoid duplicate context)
        if "workflows_deleted" not in context:
            workflows = await call_n8n_safe(n8n_tools.list_workflows(), timeout=5.0)
            # Make sure to handle empty list [] correctly (boolean evaluation of [] is False)
            if workflows is not None and (not isinstance(workflows, dict) or "error" not in workflows):
                context["workflows"] = {
                    "count": len(workflows) if isinstance(workflows, list) else "unknown",
                    "recent": workflows[:5] if isinstance(workflows, list) else list(workflows.values())[:5] if isinstance(workflows, dict) else []
                }
            elif isinstance(workflows, dict) and "error" in workflows:
                context["workflows_error"] = f"n8n unavailable: {workflows['error']}"

    # Search nodes
    if any(word in message_lower for word in ["nodo", "node", "buscar", "search"]):
        query = message
        for skip in ["nodo", "node", "buscar", "search", "find"]:
            query = query.replace(skip, "").strip()

        # Try n8n search first with timeout, fallback to offline
        nodes = await call_n8n_safe(n8n_tools.search_nodes(query=query), timeout=3.0, default=None)
        if nodes:
            context["nodes"] = {
                "query": query,
                "found": len(nodes),
                "results": nodes[:10]
            }
        else:
            # Use offline database as fallback
            try:
                nodes_offline = []
                query_lower = query.lower()
                for node_id, node_info in {**N8N_NODES_CORE, **N8N_NODES_COMMUNITY}.items():
                    searchable = f"{node_id} {str(node_info)}".lower()
                    if query_lower in searchable:
                        nodes_offline.append({"id": node_id, "info": node_info})
                if nodes_offline:
                    context["nodes"] = {
                        "query": query,
                        "found": len(nodes_offline),
                        "results": nodes_offline[:10],
                        "note": "Using offline database"
                    }
            except Exception as e2:
                logger.error(f"Offline search also failed: {e2}")

    # Search templates
    if any(word in message_lower for word in ["template", "ejemplo", "example", "crear"]):
        templates = await call_n8n_safe(n8n_tools.search_templates(query=message), timeout=3.0, default=None)
        if templates:
            context["templates"] = templates[:8]
        else:
            # Use offline database as fallback
            try:
                templates_offline = []
                query_lower = message.lower()
                for template_id, template_info in N8N_TEMPLATES.items():
                    searchable = f"{template_id} {str(template_info)}".lower()
                    if query_lower in searchable:
                        templates_offline.append(template_info)
                if templates_offline:
                    context["templates"] = templates_offline[:8]
                    context["templates_note"] = "Using offline database"
            except Exception as e2:
                logger.error(f"Offline template search failed: {e2}")

    # Expression validation
    if any(word in message_lower for word in ["expresión", "expression", "$json", "$node", "validar"]):
        try:
            # Extract potential expression
            expr_match = re.search(r'[\$][\w\[\."\{\} ]+', message)
            if expr_match:
                expr = expr_match.group()
                validation = await n8n_tools.validate_expression(expr, context=message)
                context["expression_validation"] = {
                    "expression": expr,
                    "validation": validation
                }
        except Exception as e:
            logger.warning(f"Failed to validate expression: {e}")

    return context


@app.get("/api/tools")
async def list_tools():
    """List available tools and skills"""
    current_provider = ai_provider.get_current_provider() if isinstance(ai_provider, DynamicMultiProvider) else AI_PROVIDER

    return {
        "n8n_api": ["list_workflows", "get_workflow", "create_workflow", "update_workflow", "activate_workflow"],
        "database": ["search_nodes", "get_node", "validate_node", "search_templates", "validate_expression"],
        "skills": [
            {
                "name": "expression_syntax",
                "description": "Validates n8n expression syntax and fixes common errors",
                "expert": "ExpressionSyntaxExpert",
                "features": ["validate_expression", "suggest_correction", "explain_syntax", "get_examples"]
            },
            {
                "name": "mcp_tools",
                "description": "Expert guide for using n8n-MCP MCP tools effectively",
                "expert": "MCPToolsExpert",
                "features": ["tool_selection", "smart_parameters", "validation_profiles"]
            },
            {
                "name": "workflow_patterns",
                "description": "Proven n8n workflow patterns from real workflows",
                "expert": "WorkflowPatternsExpert",
                "features": ["core_patterns", "connection_rules", "use_cases"]
            },
            {
                "name": "validation",
                "description": "Workflow validation and error interpretation",
                "expert": "ValidationExpert",
                "features": ["error_catalog", "false_positives", "solutions"]
            },
            {
                "name": "node_configuration",
                "description": "Operation-aware node configuration guidance",
                "expert": "NodeConfigExpert",
                "features": ["property_dependencies", "ai_connection_types", "common_issues"]
            },
            {
                "name": "code_javascript",
                "description": "JavaScript code best practices for n8n Code nodes",
                "expert": "CodeJavaScriptExpert",
                "features": ["data_access", "return_format", "builtin_functions", "common_errors"]
            },
            {
                "name": "code_python",
                "description": "Python code limitations and workarounds for n8n",
                "expert": "CodePythonExpert",
                "features": ["standard_library", "http_workarounds", "limitations"]
            }
        ],
        "stats": {
            "nodes_total": len(n8n_tools.nodes),
            "templates_total": len(n8n_tools.templates),
            "skills_total": 7,
            "ai_provider": AI_PROVIDER,
            "current_provider": current_provider
        }
    }


@app.get("/api/nodes")
async def search_nodes_api(query: str = "", category: str = ""):
    """Search n8n nodes"""
    nodes = await n8n_tools.search_nodes(query=query, category=category)
    return {"nodes": nodes, "count": len(nodes)}


@app.get("/api/templates")
async def search_templates_api(query: str = "", category: str = ""):
    """Search workflow templates"""
    templates = await n8n_tools.search_templates(query=query, category=category)
    return {"templates": templates, "count": len(templates)}


@app.get("/api/workflows")
async def get_workflows():
    """Get workflows from n8n"""
    return await n8n_tools.list_workflows()


@app.post("/api/validate/expression")
async def validate_expression_api(request: Dict[str, str]):
    """Validate n8n expression"""
    expression = request.get("expression")
    context = request.get("context", "")
    return await n8n_tools.validate_expression(expression, context)


@app.get("/api/skills")
async def list_skills():
    """List all available skills with details"""
    return {
        "skills": {
            "expression_syntax": {
                "name": "Expression Syntax Expert",
                "description": "Validates n8n expression syntax and fixes common errors",
                "patterns": ExpressionSyntaxExpert.PATTERNS,
                "common_errors": ExpressionSyntaxExpert.COMMON_ERRORS
            },
            "mcp_tools": {
                "name": "MCP Tools Expert",
                "description": "Expert guide for using n8n-MCP MCP tools effectively",
                "tool_selection": MCPToolsExpert.TOOL_SELECTION_GUIDE,
                "smart_parameters": MCPToolsExpert.SMART_PARAMETERS
            },
            "workflow_patterns": {
                "name": "Workflow Patterns Expert",
                "description": "Proven n8n workflow patterns from real workflows",
                "patterns": WorkflowPatternsExpert.CORE_PATTERNS,
                "rules": WorkflowPatternsExpert.CONNECTION_RULES
            },
            "validation": {
                "name": "Validation Expert",
                "description": "Workflow validation and error interpretation",
                "error_catalog": ValidationExpert.ERROR_CATALOG,
                "false_positives": ValidationExpert.FALSE_POSITIVES
            },
            "node_configuration": {
                "name": "Node Configuration Expert",
                "description": "Operation-aware node configuration guidance",
                "dependencies": NodeConfigExpert.PROPERTY_DEPENDENCIES,
                "ai_connections": NodeConfigExpert.AI_CONNECTION_TYPES
            },
            "code_javascript": {
                "name": "JavaScript Code Expert",
                "description": "JavaScript code best practices for n8n Code nodes",
                "patterns": CodeJavaScriptExpert.DATA_ACCESS_PATTERNS,
                "common_errors": CodeJavaScriptExpert.TOP_5_ERRORS
            },
            "code_python": {
                "name": "Python Code Expert",
                "description": "Python code limitations and workarounds for n8n",
                "limitation": CodePythonExpert.CRITICAL_LIMITATION,
                "workarounds": CodePythonExpert.HTTP_WORKAROUNDS
            }
        },
        "total": 7
    }


@app.get("/api/skills/{skill_name}")
async def get_skill_details(skill_name: str):
    """Get details for a specific skill"""
    skill_map = {
        "expression_syntax": ExpressionSyntaxExpert,
        "mcp_tools": MCPToolsExpert,
        "workflow_patterns": WorkflowPatternsExpert,
        "validation": ValidationExpert,
        "node_configuration": NodeConfigExpert,
        "code_javascript": CodeJavaScriptExpert,
        "code_python": CodePythonExpert
    }

    if skill_name not in skill_map:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    skill_class = skill_map[skill_name]

    # Return skill information
    return {
        "name": skill_name,
        "class": skill_class.__name__,
        "doc": skill_class.__doc__,
        "attributes": [attr for attr in dir(skill_class) if not attr.startswith('_')]
    }


# ============================================
# ADMIN ENDPOINTS - DYNAMIC MODEL SWITCHING
# ============================================

class AdminConfig(BaseModel):
    user_id: int
    admin_key: Optional[str] = None


class ModelSwitchRequest(BaseModel):
    user_id: int
    new_provider: Optional[str] = None
    admin_key: Optional[str] = None


class CustomModelRequest(BaseModel):
    user_id: int
    name: str
    api_key: str
    base_url: str
    provider_type: str = "openai"
    admin_key: Optional[str] = None


def is_admin_user(user_id: int) -> bool:
    """Check if user is admin"""
    if not ALLOWED_ADMIN_USERS:
        return False
    return str(user_id) in ALLOWED_ADMIN_USERS or "*" in ALLOWED_ADMIN_USERS


@app.post("/api/admin/status")
async def admin_status(request: AdminConfig):
    """Get admin status and current model info"""
    if not is_admin_user(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    if isinstance(ai_provider, DynamicMultiProvider):
        return {
            "current_provider": ai_provider.get_current_provider(),
            "current_model": ai_provider.get_current_model(),
            "available_providers": ai_provider.get_available_providers(),
            "auto_fallback": AUTO_FALLBACK,
            "fallback_order": FALLBACK_ORDER,
            "providers_info": ai_provider.get_provider_info(),
            "mode": "dynamic-multi"
        }
    else:
        return {
            "current_provider": AI_PROVIDER,
            "current_model": getattr(ai_provider, 'model', 'N/A'),
            "available_providers": [AI_PROVIDER],
            "auto_fallback": AUTO_FALLBACK,
            "mode": "single"
        }


@app.post("/api/admin/switch-model")
async def switch_model(request: ModelSwitchRequest):
    """Dynamically switch to a different model/provider WITHOUT RESTART"""
    if not is_admin_user(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    global ai_provider

    if isinstance(ai_provider, DynamicMultiProvider):
        # Dynamic switching available!
        if request.new_provider:
            old_provider = ai_provider.get_current_provider()

            if ai_provider.force_switch(request.new_provider):
                new_provider = ai_provider.get_current_provider()

                await send_bot_notification(
                    f"🔄 Modelo cambiado: {old_provider} → {new_provider}",
                    "model_changed"
                )

                return {
                    "message": f"✅ Modelo cambiado exitosamente",
                    "old_provider": old_provider,
                    "new_provider": new_provider,
                    "requires_restart": False
                }
            else:
                available = ai_provider.get_available_providers()
                return {
                    "message": f"❌ Proveedor '{request.new_provider}' no disponible",
                    "available_providers": available,
                    "requires_restart": False
                }
        else:
            return {
                "message": "❌ Especifica el proveedor al que deseas cambiar",
                "available_providers": ai_provider.get_available_providers()
            }
    else:
        # Single provider mode - restart required
        return {
            "message": f"⚠️ Modo single-provider activo. Para cambiar dinámicamente, activa AI_PROVIDER=multi en .env y reinicia",
            "requires_restart": True,
            "current_mode": AI_PROVIDER
        }


@app.post("/api/admin/add-custom-model")
async def add_custom_model(request: CustomModelRequest):
    """Add a custom model dynamically"""
    if not is_admin_user(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    if isinstance(ai_provider, DynamicMultiProvider):
        custom_provider = CustomProvider(
            name=request.name,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.name,
            provider_type=request.provider_type
        )

        ai_provider.add_custom_provider(custom_provider)

        await send_bot_notification(
            f"✅ Modelo custom agregado: {request.name}",
            "model_added"
        )

        return {
            "message": f"Modelo custom '{request.name}' agregado exitosamente",
            "provider_type": request.provider_type,
            "available_providers": ai_provider.get_available_providers(),
            "auto_switch_available": True
        }
    else:
        return {
            "message": "El modo dinámico no está activo. Activa AI_PROVIDER=multi en .env y reinicia",
            "requires_restart": True
        }


@app.post("/api/admin/list-models")
async def list_models(request: AdminConfig):
    """List all available models and providers"""
    if not is_admin_user(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    if isinstance(ai_provider, DynamicMultiProvider):
        return {
            "providers": ai_provider.get_provider_info(),
            "current_provider": ai_provider.get_current_provider(),
            "current_model": ai_provider.get_current_model(),
            "auto_fallback": AUTO_FALLBACK,
            "fallback_order": FALLBACK_ORDER,
            "mode": "dynamic-multi"
        }
    else:
        providers = {
            "anthropic": {
                "configured": bool(ANTHROPIC_API_KEY),
                "model": ANTHROPIC_MODEL
            },
            "openai": {
                "configured": bool(OPENAI_API_KEY),
                "model": OPENAI_MODEL
            },
            "gemini": {
                "configured": bool(GEMINI_API_KEY),
                "model": GEMINI_MODEL
            },
            "qwen": {
                "configured": bool(QWEN_API_KEY),
                "model": QWEN_MODEL
            },
            "deepseek": {
                "configured": bool(DEEPSEEK_API_KEY),
                "model": DEEPSEEK_MODEL
            },
            "ollama": {
                "configured": True,
                "model": OLLAMA_MODEL
            }
        }

        return {
            "providers": providers,
            "current_provider": AI_PROVIDER,
            "current_model": getattr(ai_provider, 'model', 'N/A'),
            "mode": "single"
        }


@app.post("/api/admin/test-model")
async def test_model(request: AdminConfig):
    """Test if a model is available and working"""
    if not is_admin_user(request.user_id):
        raise HTTPException(status_code=403, detail="Not authorized as admin")

    try:
        is_avail = await ai_provider.is_available()
        return {
            "provider": ai_provider.get_current_provider() if isinstance(ai_provider, DynamicMultiProvider) else AI_PROVIDER,
            "model": ai_provider.get_current_model() if isinstance(ai_provider, DynamicMultiProvider) else getattr(ai_provider, 'model', 'N/A'),
            "available": is_avail,
            "status": "OK" if is_avail else "NOT_AVAILABLE"
        }
    except Exception as e:
        return {
            "provider": AI_PROVIDER,
            "model": getattr(ai_provider, 'model', 'N/A'),
            "available": False,
            "error": str(e)
        }


@app.delete("/api/history/{user_id}")
async def clear_history(user_id: int):
    """Clear conversation history for a user"""
    if user_id in conversation_history:
        del conversation_history[user_id]
        return {"status": "cleared", "user_id": user_id}
    return {"status": "no_history", "user_id": user_id}


@app.post("/api/admin/restart")
async def restart_server():
    """Restart the server to load new configuration"""
    # This endpoint triggers a graceful restart
    # The actual restart is handled by systemd's auto-restart
    logger.info("Restart requested via API - triggering graceful shutdown...")

    # Give time for response to be sent
    async def delayed_shutdown():
        import asyncio
        await asyncio.sleep(1)
        logger.info("Shutting down for restart...")
        # Systemd will auto-restart because of Restart=always
        import signal
        import os
        os.kill(os.getpid(), signal.SIGTERM)

    # Start the delayed shutdown
    asyncio.create_task(delayed_shutdown())

    return {
        "status": "restarting",
        "message": "Server is restarting. This will take a few seconds..."
    }


@app.post("/api/notify")
async def notify_bot(notification: Dict[str, str]):
    """Endpoint to receive notifications from the server"""
    message = notification.get("message", "")
    notification_type = notification.get("type", "info")

    logger.info(f"Notification to bot [{notification_type}]: {message}")

    return {
        "status": "delivered",
        "message": message,
        "type": notification_type
    }


def main():
    """Start server"""
    logger.info("🚀 Claudio starting...")
    logger.info(f"📡 Port: {PORT}")
    logger.info(f"🤖 AI Provider: {AI_PROVIDER}")
    logger.info(f"🧠 Dynamic Mode: {isinstance(ai_provider, DynamicMultiProvider)}")
    if isinstance(ai_provider, DynamicMultiProvider):
        logger.info(f"🔄 Current Provider: {ai_provider.get_current_provider()}")
        logger.info(f"🧠 Current Model: {ai_provider.get_current_model()}")
        logger.info(f"📊 Available Providers: {ai_provider.get_available_providers()}")
    else:
        logger.info(f"🧠 AI Model: {ai_provider.model}")
    logger.info(f"🔌 n8n: {N8N_INSTANCE_URL}")
    logger.info(f"📊 Nodes: {len(n8n_tools.nodes)}")
    logger.info(f"📋 Templates: {len(n8n_tools.templates)}")
    logger.info(f"🔄 Auto-Fallback: {AUTO_FALLBACK}")

    # Check AI provider availability
    if not ai_provider.api_key or ai_provider.api_key == "dynamic":
        logger.info("🔧 Using dynamic multi-provider mode")

    # Increase timeout for long operations (e.g., deleting multiple workflows)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info",
        timeout_keep_alive=300,
        timeout_graceful_shutdown=30
    )


if __name__ == '__main__':
    main()
