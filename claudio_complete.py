#!/usr/bin/env python3
"""
Claudio Server - Multi-AI Provider Support
Supports Anthropic, OpenAI, Ollama, and multi-provider configurations
"""

import os
import sys
import json
import logging
import asyncio
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

# Load environment variables
load_dotenv()

# Add skills directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database and skills
from n8n_database import (
    N8N_NODES_CORE, N8N_NODES_COMMUNITY, N8N_TEMPLATES,
    N8N_VALIDATION_PROFILES, N8N_EXPRESSION_PATTERNS, N8N_COMMON_ISSUES
)

# Configure logging
file_handler = logging.FileHandler('claudio_complete.log', encoding='utf-8')
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
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

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

    def is_available(self) -> bool:
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

    def is_available(self) -> bool:
        return ANTHROPIC_AVAILABLE and bool(self.api_key)


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str, model: str = 'gpt-4o'):
        super().__init__(api_key, model)
        if OPENAI_AVAILABLE and api_key:
            self.client = OpenAI(api_key=api_key)

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        if not self.client:
            raise ValueError("OpenAI client not initialized")

        # Add system prompt as first message
        all_messages = [{"role": "system", "content": system_prompt}] + messages

        response = self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            max_tokens=4096
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
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


class MultiProvider(AIProvider):
    """Multi-provider fallback support"""

    def __init__(self, providers: List[AIProvider]):
        self.providers = providers
        self.api_key = "multi"

    async def chat(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        last_error = None

        for provider in self.providers:
            if await provider.is_available():
                try:
                    return await provider.chat(messages, system_prompt)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Provider {provider.__class__.__name__} failed: {e}")
                    continue

        if last_error:
            raise last_error
        raise ValueError("No AI providers available")

    async def is_available(self) -> bool:
        return any(await p.is_available() for p in self.providers)


# ============================================
# INITIALIZE AI PROVIDER
# ============================================

def get_ai_provider() -> AIProvider:
    """Get configured AI provider"""

    if AI_PROVIDER == 'anthropic':
        return AnthropicProvider(
            api_key=ANTHROPIC_API_KEY or '',
            model=ANTHROPIC_MODEL
        )

    elif AI_PROVIDER == 'openai':
        return OpenAIProvider(
            api_key=OPENAI_API_KEY or '',
            model=OPENAI_MODEL
        )

    elif AI_PROVIDER == 'ollama':
        return OllamaProvider(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL
        )

    elif AI_PROVIDER == 'multi':
        providers = []

        if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
            providers.append(AnthropicProvider(ANTHROPIC_API_KEY, ANTHROPIC_MODEL))

        if OPENAI_AVAILABLE and OPENAI_API_KEY:
            providers.append(OpenAIProvider(OPENAI_API_KEY, OPENAI_MODEL))

        if OllamaProvider(OLLAMA_BASE_URL, OLLAMA_MODEL).is_available():
            providers.append(OllamaProvider(OLLAMA_BASE_URL, OLLAMA_MODEL))

        if not providers:
            logger.warning("No providers configured for multi-provider mode, falling back to Anthropic")
            return AnthropicProvider(ANTHROPIC_API_KEY or '', ANTHROPIC_MODEL)

        return MultiProvider(providers)

    else:
        logger.warning(f"Unknown provider '{AI_PROVIDER}', falling back to Anthropic")
        return AnthropicProvider(ANTHROPIC_API_KEY or '', ANTHROPIC_MODEL)


# Initialize AI provider
ai_provider = get_ai_provider()

# ============================================
# SYSTEM PROMPT
# ============================================

CLADIO_COMPLETE_PROMPT = """You are Claudio, an expert n8n workflow automation specialist with COMPLETE ACCESS to n8n.

## YOUR CAPABILITIES

### REAL n8n API ACCESS
You have these tools available:
- **list_workflows()** - View all workflows (real data from n8n)
- **get_workflow(id)** - Get specific workflow
- **create_workflow(data)** - Create new workflow in n8n
- **update_workflow(id, data)** - Update existing workflow
- **activate_workflow(id)** - Activate workflow
- **search_nodes(query)** - Search 1396 n8n nodes
- **search_templates(query)** - Search 2709+ templates
- **validate_expression(expr)** - Validate n8n expressions

### DATABASE ACCESS
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

## RESPONSE APPROACH

When users ask about n8n:
1. Search your database for relevant nodes/templates
2. Provide exact configurations
3. Warn about common pitfalls
4. Suggest validation steps
5. Offer to create/modify workflows

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


# Initialize tools
n8n_tools = N8NMCPTools()

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Claudio - Multi-AI n8n Assistant",
    description="Expert n8n workflow automation with multi-AI provider support",
    version="4.0.0"
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
    return {
        "service": "Claudio",
        "version": "4.0.0",
        "ai_provider": AI_PROVIDER,
        "features": [
            "Multi-AI provider support (Anthropic, OpenAI, Ollama)",
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
    """Health check"""
    n8n_health = await n8n_tools.list_workflows()
    ai_available = await ai_provider.is_available()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ai_provider": AI_PROVIDER,
        "ai_available": ai_available,
        "n8n": {
            "connected": not isinstance(n8n_health, dict) or "error" not in n8n_health,
            "instance": N8N_INSTANCE_URL,
            "has_api_key": bool(N8N_API_KEY)
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
        response_text = await ai_provider.chat(
            messages=conversation_history[user_id],
            system_prompt=CLADIO_COMPLETE_PROMPT
        )

        # Add to history
        conversation_history[user_id].append({
            "role": "assistant",
            "content": response_text
        })

        # Keep last 20
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        return ChatResponse(
            response=response_text,
            timestamp=datetime.now().isoformat(),
            model=ai_provider.model,
            provider=AI_PROVIDER,
            tools_used=tools_used,
            context=tool_context
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_and_use_tools(message: str) -> Dict[str, Any]:
    """Analyze message and use appropriate tools"""
    context = {}
    message_lower = message.lower()

    # Check workflows
    if any(word in message_lower for word in ["workflow", "workflows", "mis workflows", "listar"]):
        try:
            workflows = await n8n_tools.list_workflows()
            if not isinstance(workflows, dict) or "error" not in workflows:
                context["workflows"] = {
                    "count": len(workflows) if isinstance(workflows, list) else "unknown",
                    "recent": workflows[:5] if isinstance(workflows, list) else list(workflows.values())[:5] if isinstance(workflows, dict) else []
                }
        except:
            pass

    # Search nodes
    if any(word in message_lower for word in ["nodo", "node", "buscar", "search"]):
        query = message
        for skip in ["nodo", "node", "buscar", "search", "find"]:
            query = query.replace(skip, "").strip()
        nodes = await n8n_tools.search_nodes(query=query)
        if nodes:
            context["nodes"] = {
                "query": query,
                "found": len(nodes),
                "results": nodes[:10]
            }

    # Search templates
    if any(word in message_lower for word in ["template", "ejemplo", "example", "crear"]):
        templates = await n8n_tools.search_templates(query=message)
        if templates:
            context["templates"] = templates[:8]

    # Expression validation
    if any(word in message_lower for word in ["expresión", "expression", "$json", "$node", "validar"]):
        # Extract potential expression
        expr_match = re.search(r'[\$][\w\[\."\{\} ]+', message)
        if expr_match:
            expr = expr_match.group()
            validation = await n8n_tools.validate_expression(expr, context=message)
            context["expression_validation"] = {
                "expression": expr,
                "validation": validation
            }

    return context


@app.get("/api/tools")
async def list_tools():
    """List available tools"""
    return {
        "n8n_api": ["list_workflows", "get_workflow", "create_workflow", "update_workflow", "activate_workflow"],
        "database": ["search_nodes", "get_node", "validate_node", "search_templates", "validate_expression"],
        "stats": {
            "nodes_total": len(n8n_tools.nodes),
            "templates_total": len(n8n_tools.templates),
            "ai_provider": AI_PROVIDER,
            "ai_model": ai_provider.model
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


def main():
    """Start server"""
    logger.info("🚀 Claudio starting...")
    logger.info(f"📡 Port: {PORT}")
    logger.info(f"🤖 AI Provider: {AI_PROVIDER}")
    logger.info(f"🧠 AI Model: {ai_provider.model}")
    logger.info(f"🔌 n8n: {N8N_INSTANCE_URL}")
    logger.info(f"📊 Nodes: {len(n8n_tools.nodes)}")
    logger.info(f"📋 Templates: {len(n8n_tools.templates)}")

    # Check AI provider availability
    if not ai_provider.api_key or ai_provider.api_key == "multi":
        logger.warning("⚠️  AI provider may not be configured properly")

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")


if __name__ == '__main__':
    main()
