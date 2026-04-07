#!/usr/bin/env python3
"""
Claudio Server FULL - Claude Code with real n8n-MCP integration
Exposes Claude with full access to n8n tools and specialized skills
"""

import os
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from anthropic import Anthropic
from n8n_mcp_tools import N8NMCPClient, N8NConfig

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('claudio_server_full.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
N8N_API_KEY = os.getenv('N8N_API_KEY')
N8N_INSTANCE_URL = os.getenv('N8N_INSTANCE_URL', 'https://n8n.aicorebots.com')
N8N_HOST_HEADER = os.getenv('N8N_HOST_HEADER', 'n8n.aicorebots.com')  # For Traefik routing
PORT = int(os.getenv('CLADIO_PORT', '8000'))

# Initialize clients
claude = Anthropic(api_key=ANTHROPIC_API_KEY)
n8n_config = N8NConfig(
    api_key=N8N_API_KEY,
    instance_url=N8N_INSTANCE_URL,
    host_header=N8N_HOST_HEADER
)
n8n_client = N8NMCPClient(n8n_config)

# Conversation history per user
conversation_history: Dict[int, List[Dict[str, str]]] = {}

# Skills - Specialized n8n expertise
SKILLS = {
    "workflow_patterns": {
        "name": "n8n Workflow Patterns",
        "description": "Proven patterns from 2709+ templates",
        "patterns": [
            "Webhook Processing: Webhook → Parse → Process → Response",
            "HTTP API Integration: Schedule → HTTP Request → Process → Notify",
            "Database Operations: Trigger → Query → Transform → Update",
            "AI Agent: Trigger → AI Agent → Tools → Response",
            "Batch Processing: Trigger → Split → Process → Aggregate"
        ]
    },
    "expression_syntax": {
        "name": "n8n Expression Syntax",
        "description": "Advanced {{}} patterns and variables",
        "rules": [
            "Webhook data: $json.body (not $json directly)",
            "Node references: $node[\"NodeName\"].json.field",
            "Expressions: {{}} in parameters, plain JS in Code nodes",
            "Previous node: $node[\"HTTP Request\"].json.result"
        ]
    },
    "validation_rules": {
        "name": "Workflow Validation",
        "description": "Multi-level validation patterns",
        "rules": [
            "Never trust defaults - always configure explicitly",
            "IF node: use branch parameter (true/false)",
            "Webhook: data under $json.body",
            "Connections: proper source/target/ports"
        ]
    },
    "node_configuration": {
        "name": "Node Configuration",
        "description": "Operation-aware configuration",
        "common_nodes": {
            "httpRequest": {
                "required": ["url", "method"],
                "optional": ["authentication", "headers", "body"]
            },
            "set": {
                "required": ["values"],
                "optional": ["includeOtherFields", "options"]
            },
            "if": {
                "required": ["conditions"],
                "optional": ["combineOperation", "looseTypeValidation"]
            },
            "code": {
                "required": ["code", "language"],
                "optional": ["mode", "jsCode", "pythonCode"]
            }
        }
    }
}

# Enhanced system prompt with tool access awareness
CLADIO_SYSTEM_PROMPT = """You are Claudio, an expert n8n workflow automation specialist with REAL ACCESS to n8n tools and APIs.

## Your Capabilities

You have access to these REAL tools:
- **list_workflows()** - View all workflows in the n8n instance
- **get_workflow(id)** - Get specific workflow details
- **create_workflow(data)** - Create new workflows
- **update_workflow(id, data)** - Update existing workflows
- **activate_workflow(id)** - Activate a workflow
- **search_nodes(query)** - Search 1396 n8n nodes
- **search_templates(query)** - Search 2709+ workflow templates
- **validate_workflow(data)** - Validate workflow structure
- **get_executions()** - View workflow execution history

## Your Expertise

**n8n Platform**: 1,396 nodes (812 core + 584 community)
**Workflow Patterns**: 5 core patterns from 2709+ templates
**Expression Syntax**: Advanced {{}} patterns, $json, $node variables
**Validation**: Multi-level validation from quick to comprehensive
**Production Workflows**: Error handling, batching, conditional routing

## Critical Rules

1. **Templates First**: Always check templates before building from scratch
2. **Never Trust Defaults**: Default values cause 60%+ of runtime failures
3. **Explicit Configuration**: ALWAYS configure ALL parameters
4. **Webhook Data**: Access via `$json.body`, not `$json`
5. **IF Node Routing**: Use `branch` parameter for TRUE/FALSE

## Workflow Patterns

1. **Webhook Processing**: Webhook → Parse → Process → Response
2. **HTTP API Integration**: Schedule → HTTP Request → Process → Notify
3. **Database Operations**: Trigger → Query → Transform → Update
4. **AI Agent**: Trigger → AI Agent → Tools → Response
5. **Batch Processing**: Trigger → Split → Process → Aggregate

## Expression Syntax

- **Webhook data**: `$json.body` (NOT `$json`)
- **Node references**: `$node["NodeName"].json.field`
- **Array access**: `$json.items[0].name`
- **Previous node**: `$node["HTTP Request"].json.result`

## Response Format

When users ask about n8n:
1. Use search tools when appropriate
2. Provide exact node configurations
3. Include validation steps
4. Reference templates when available
5. Warn about common pitfalls

You are communicating through Telegram. Be concise and practical. Focus on working solutions.
"""

app = FastAPI(
    title="Claudio Server FULL",
    description="Claude Code with real n8n-MCP integration",
    version="2.0.0"
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
    tools_used: List[str] = []


class ToolCall(BaseModel):
    tool: str
    parameters: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Claudio Server FULL",
        "version": "2.0.0",
        "features": [
            "Claude API integration",
            "Real n8n API access",
            "Workflow templates (2709+)",
            "Node search (1396 nodes)",
            "Workflow validation",
            "Specialized skills"
        ],
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "tools": "/api/tools",
            "workflows": "/api/n8n/workflows",
            "nodes": "/api/n8n/nodes",
            "templates": "/api/n8n/templates"
        }
    }


@app.get("/health")
async def health_check():
    """Health check with n8n connectivity"""
    n8n_health = await n8n_client.health_check()

    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "anthropic": ANTHROPIC_API_KEY is not None,
        "n8n": n8n_health
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat with Claude and n8n tool access
    Automatically uses n8n tools when needed
    """
    user_id = request.user_id
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        # Clear history if requested
        if request.clear_history and user_id in conversation_history:
            del conversation_history[user_id]

        # Get or initialize conversation history
        if user_id not in conversation_history:
            conversation_history[user_id] = []

        # Add user message to history
        conversation_history[user_id].append({
            "role": "user",
            "content": user_message
        })

        # Detect if n8n tools are needed
        tools_used = []
        tool_context = await analyze_and_use_tools(user_message)

        if tool_context:
            tools_used = list(tool_context.keys())
            # Add tool results to context
            enhanced_message = f"{user_message}\n\n[Relevant Information]\n{json.dumps(tool_context, indent=2)}"
        else:
            enhanced_message = user_message

        # Log the message
        logger.info(f"User {user_id}: {user_message}")
        if tools_used:
            logger.info(f"Tools used: {tools_used}")

        # Call Claude API
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=CLADIO_SYSTEM_PROMPT,
            messages=conversation_history[user_id] + [
                {"role": "user", "content": enhanced_message}
            ]
        )

        # Extract response
        assistant_message = response.content[0].text

        # Add assistant response to history (original message, not enhanced)
        conversation_history[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # Keep only last 20 messages
        if len(conversation_history[user_id]) > 20:
            conversation_history[user_id] = conversation_history[user_id][-20:]

        logger.info(f"Claudio response to {user_id}: {assistant_message[:100]}...")

        return ChatResponse(
            response=assistant_message,
            timestamp=datetime.now().isoformat(),
            model="claude-sonnet-4",
            tools_used=tools_used
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_and_use_tools(message: str) -> Dict[str, Any]:
    """
    Analyze message and automatically use appropriate n8n tools
    Returns context information from tools
    """
    message_lower = message.lower()
    context = {}

    # Check for workflow-related queries
    if any(word in message_lower for word in ["workflow", "workflows", "list", "show"]):
        try:
            workflows = await n8n_client.list_workflows()
            context["workflows"] = {
                "count": len(workflows),
                "recent": workflows[:5] if len(workflows) > 5 else workflows
            }
        except Exception as e:
            logger.warning(f"Failed to list workflows: {e}")

    # Check for node search
    if any(word in message_lower for word in ["node", "nodes", "search"]):
        try:
            # Extract search terms
            search_query = message
            for skip in ["search", "find", "look for", "nodes", "node"]:
                search_query = search_query.replace(skip, "").strip()

            nodes = await n8n_client.search_nodes(query=search_query)
            context["nodes"] = {
                "query": search_query,
                "results": nodes[:10]  # Limit results
            }
        except Exception as e:
            logger.warning(f"Failed to search nodes: {e}")

    # Check for template search
    if any(word in message_lower for word in ["template", "templates", "example"]):
        try:
            templates = await n8n_client.search_templates(query=message)
            context["templates"] = templates[:10]
        except Exception as e:
            logger.warning(f"Failed to search templates: {e}")

    # Check for validation request
    if "validate" in message_lower or "check" in message_lower:
        context["validation_rules"] = SKILLS["validation_rules"]
        context["expression_syntax"] = SKILLS["expression_syntax"]

    return context


@app.get("/api/tools")
async def list_tools():
    """List available n8n tools"""
    return {
        "tools": {
            "workflows": ["list", "get", "create", "update", "delete", "activate", "deactivate"],
            "nodes": ["search", "get_documentation"],
            "templates": ["search"],
            "validation": ["validate_workflow", "validate_node"],
            "executions": ["list", "test"]
        },
        "skills": list(SKILLS.keys())
    }


@app.get("/api/n8n/workflows")
async def get_workflows():
    """Get all workflows"""
    try:
        workflows = await n8n_client.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/n8n/nodes")
async def search_nodes_api(query: str = ""):
    """Search n8n nodes"""
    try:
        nodes = await n8n_client.search_nodes(query=query)
        return {"nodes": nodes, "count": len(nodes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/n8n/templates")
async def search_templates_api(query: str = "", complexity: str = "", category: str = ""):
    """Search workflow templates"""
    try:
        templates = await n8n_client.search_templates(
            query=query,
            complexity=complexity,
            category=category
        )
        return {"templates": templates, "count": len(templates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills")
async def get_skills():
    """Get specialized skills"""
    return SKILLS


def main():
    """Start the server"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    logger.info("🚀 Claudio Server FULL starting...")
    logger.info(f"📡 Port: {PORT}")
    logger.info(f"🔌 n8n Instance: {N8N_INSTANCE_URL}")
    logger.info(f"✅ n8n API: {'Configured' if N8N_API_KEY else 'Not configured'}")
    logger.info(f"🤖 Claude API: {'Configured'}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )


if __name__ == '__main__':
    main()
