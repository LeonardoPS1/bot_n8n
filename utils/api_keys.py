"""
API Key Management Utilities
Shared functions for validating and masking API keys
"""

from typing import Dict, Callable


def mask_api_key(api_key: str) -> str:
    """Mask API key for display - show only first 8 and last 4 characters"""
    if not api_key or len(api_key) < 12:
        return "***"
    return f"{api_key[:8]}...{api_key[-4:]}"


def validate_api_key_format(provider: str, api_key: str) -> bool:
    """Validate API key format based on provider

    Args:
        provider: Provider name (anthropic, openai, gemini, qwen, deepseek)
        api_key: The API key to validate

    Returns:
        True if the key format is valid for the provider, False otherwise
    """
    if not api_key or len(api_key) < 10:
        return False

    provider = provider.lower()

    # Validation rules for each provider
    validation_rules: Dict[str, Callable[[str], bool]] = {
        'anthropic': lambda k: k.startswith('sk-ant-'),
        'openai': lambda k: k.startswith('sk-') and not k.startswith('sk-ant-'),
        'gemini': lambda k: len(k) >= 20,
        'qwen': lambda k: k.startswith('sk-'),
        'deepseek': lambda k: k.startswith('sk-'),
        'ollama': lambda k: len(k) >= 5,  # URL validation would be different
    }

    validator = validation_rules.get(provider)
    if validator:
        return validator(api_key)

    # Default validation for unknown providers
    return len(api_key) >= 10


# Provider configuration constants
PROVIDER_ENV_MAPPING = {
    'anthropic': 'ANTHROPIC_API_KEY',
    'openai': 'OPENAI_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'qwen': 'QWEN_API_KEY',
    'deepseek': 'DEEPSEEK_API_KEY',
    'ollama': 'OLLAMA_BASE_URL',
}

VALID_PROVIDERS = list(PROVIDER_ENV_MAPPING.keys())

# API key format examples for documentation
API_KEY_FORMATS = {
    'anthropic': 'sk-ant-xxxx (starts with sk-ant-)',
    'openai': 'sk-proj-xxxx (starts with sk-, not sk-ant-)',
    'gemini': 'AIzaSyxxxx (20+ characters)',
    'qwen': 'sk-xxxx (starts with sk-)',
    'deepseek': 'sk-xxxx (starts with sk-)',
}
