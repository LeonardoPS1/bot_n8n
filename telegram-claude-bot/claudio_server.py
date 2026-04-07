#!/usr/bin/env python3
"""
Claudio Server - Claude Code with n8n-MCP backend for Telegram Bot
Exposes Claude's n8n workflow capabilities via HTTP API
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

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('claudio_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Environment variables
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
N8N_API_KEY = os.getenv('N8N_API_KEY')
N8N_INSTANCE_URL = os.getenv('N8N_INSTANCE_URL', 'https://n8n.aicorebots.com')
PORT = int(os.getenv('CLADIO_PORT', '8000'))

# Claude client
claude = Anthropic(api_key=ANTHROPIC_API_KEY)

# Conversation history per user
conversation_history: Dict[int, List[Dict[str, str]]] = {}

# System prompt with n8n expertise
CLADIO_SYSTEM_PROMPT = """You are Claudio, an expert n8n workflow automation specialist with deep knowledge of:

**n8n Platform**: 1,396 nodes (812 core + 584 community), workflow patterns, best practices
**n8n-MCP Tools**: Complete access to node documentation, validation, and workflow management
**Expression Syntax**: Advanced {{}} patterns, $json, $node, $now, $env variables
**Workflow Validation**: Multi-level validation from quick checks to comprehensive runtime validation
**AI Agent Workflows**: LangChain nodes, AI tool connections, streaming mode constraints
**Production Workflows**: Error handling, batching, conditional routing, API integrations

## Core Principles

1. **Templates First**: Always check templates before building from scratch (2,709+ available)
2. **Never Trust Defaults**: Default parameter values are the #1 source of runtime failures
3. **Multi-Level Validation**: Use minimal → full → comprehensive pattern
4. **Explicit Configuration**: ALWAYS configure ALL parameters that control node behavior

## Critical Syntax Rules

- **Webhook data**: Access via `$json.body`, not directly `$json`
- **Node references**: `$node["NodeName"].json.field` (use brackets for spaces)
- **Expressions**: Use `{{}}` in parameters, plain JavaScript in Code nodes
- **Array access**: `$json.items[0].name`
- **Previous node**: `$node["HTTP Request"].json.result`

## IF Node Connections
Use `branch` parameter for TRUE/FALSE routing:
- TRUE branch: `branch: "true"`
- FALSE branch: `branch: "false"`

## Common Patterns

1. **Webhook Processing**: Webhook → Parse → Process → Response
2. **HTTP API Integration**: Schedule → HTTP Request → Process → Notify
3. **Database Operations**: Trigger → Query → Transform → Update
4. **AI Agent**: Trigger → AI Agent → Tools → Response
5. **Batch Processing**: Trigger → Split → Process → Aggregate

When users ask about n8n workflows, be specific about node types, provide exact configurations, and always validate before suggesting deployment.

You are communicating through Telegram. Be concise and helpful. Focus on practical, working solutions."""

app = FastAPI(
    title="Claudio Server",
    description="Claude Code with n8n-MCP backend for Telegram Bot",
    version="1.0.0"
)

# Add CORS middleware
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


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    n8n_connected: bool


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Claudio Server",
        "version": "1.0.0",
        "description": "Claude Code with n8n-MCP backend for Telegram Bot",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "history": "/api/history/{user_id}",
            "clear": "/api/clear/{user_id}"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Check n8n connectivity
    n8n_connected = False
    if N8N_API_KEY:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{N8N_INSTANCE_URL}/api/v1/workflows",
                    headers={"X-N8N-API-KEY": N8N_API_KEY},
                    timeout=5.0
                )
                n8n_connected = response.status_code == 200
        except Exception as e:
            logger.warning(f"n8n health check failed: {e}")

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        n8n_connected=n8n_connected
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message with Claude and return response"""
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

        # Log the incoming message
        logger.info(f"User {user_id} ({request.user_name}): {user_message[:100]}...")

        # Call Claude API
        response = claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=CLADIO_SYSTEM_PROMPT,
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

        # Log response
        logger.info(f"Claudio response to {user_id}: {assistant_message[:100]}...")

        return ChatResponse(
            response=assistant_message,
            timestamp=datetime.now().isoformat(),
            model="claude-sonnet-4"
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history/{user_id}")
async def get_history(user_id: int):
    """Get conversation history for a user"""
    if user_id not in conversation_history:
        return {"user_id": user_id, "history": []}

    return {
        "user_id": user_id,
        "message_count": len(conversation_history[user_id]),
        "history": conversation_history[user_id]
    }


@app.delete("/api/history/{user_id}")
async def clear_history(user_id: int):
    """Clear conversation history for a user"""
    if user_id in conversation_history:
        del conversation_history[user_id]
        return {"message": "History cleared", "user_id": user_id}
    return {"message": "No history to clear", "user_id": user_id}


@app.post("/api/n8n/workflows")
async def create_n8n_workflow(workflow_data: Dict[str, Any]):
    """Create a workflow in n8n via API"""
    if not N8N_API_KEY:
        raise HTTPException(status_code=503, detail="n8n API key not configured")

    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_INSTANCE_URL}/api/v1/workflows",
                headers={"X-N8N-API-KEY": N8N_API_KEY},
                json=workflow_data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error creating n8n workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Start the server"""
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    logger.info("🚀 Claudio Server starting...")
    logger.info(f"📡 Port: {PORT}")
    logger.info(f"🔌 n8n Instance: {N8N_INSTANCE_URL}")
    logger.info(f"✅ n8n API Key: {'Configured' if N8N_API_KEY else 'Not configured'}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )


if __name__ == '__main__':
    main()
