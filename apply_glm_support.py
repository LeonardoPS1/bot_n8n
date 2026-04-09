#!/usr/bin/env python3
"""
Aplica soporte para GLM 5.1 a los archivos existentes
"""

import re

# Configuración GLM para claudio_complete.py
glm_config = """
# Provider settings
PROVIDERS = {
    'anthropic': {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514'),
    },
    'openai': {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': os.getenv('OPENAI_MODEL', 'gpt-4o'),
    },
    'ollama': {
        'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        'model': os.getenv('OLLAMA_MODEL', 'phi3:mini'),
    },
    'glm': {
        'api_key': os.getenv('GLM_API_KEY'),
        'base_url': os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4'),
        'model': os.getenv('GLM_MODEL', 'glm-4-flash'),
    }
}
"""

# Actualizar claudio_complete.py
print("Actualizando claudio_complete.py...")
with open('claudio_complete.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add GLM import (after OpenAI import)
if 'from openai import OpenAI' in content and 'GLM_AVAILABLE' not in content:
    content = content.replace(
        'from openai import OpenAI\nOPENAI_AVAILABLE = True',
        'from openai import OpenAI\nOPENAI_AVAILABLE = True\n\nGLM_AVAILABLE = True  # GLM uses OpenAI client'
    )

# Add GLM to providers dict
if "'glm': {" not in content:
    # Find the providers dict and add GLM
    providers_pattern = r"(\s+'ollama': \{[^}]+\}\)"
    if re.search(providers_pattern, content):
        content = re.sub(
            providers_pattern,
            r"\1,\n    'glm': {\n        'api_key': os.getenv('GLM_API_KEY'),\n        'base_url': os.getenv('GLM_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4'),\n        'model': os.getenv('GLM_MODEL', 'glm-4-flash'),\n    }",
            content
        )

with open('claudio_complete.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  - GLM agregado a PROVIDERS")

# Update bot_v2.py
print("Actualizando bot_v2.py...")
with open('bot_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update valid_providers list
if "'glm'" not in content and "valid_providers = [" in content:
    content = re.sub(
        r"valid_providers = \['anthropic', 'openai'[^\]]*\]",
        "valid_providers = ['anthropic', 'openai', 'gemini', 'qwen', 'deepseek', 'glm', 'ollama']",
        content
    )

# Update env_mapping
if "'glm': 'GLM_API_KEY'" not in content and "'ollama': 'OLLAMA_BASE_URL'" in content:
    content = re.sub(
        r"('ollama': 'OLLAMA_BASE_URL',?\s*\})",
        r"\1,\n            'glm': 'GLM_API_KEY'",
        content
    )

with open('bot_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  - /addkey glm actualizado")
print("  - /switch glm actualizado")

# Update install.py
print("Actualizando install.py...")
with open('install.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update providers list
if '"GLM (z.ai GLM 5.1 - Costo eficiente)"' not in content:
    content = re.sub(
        r'"Ollama \(Local, gratuito\)",',
        '"GLM (z.ai GLM 5.1 - Costo eficiente)",\n        "Ollama (Local, gratuito)",',
        content
    )

with open('install.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  - GLM agregado como opcion en instalador")

print("Archivos actualizados exitosamente!")
