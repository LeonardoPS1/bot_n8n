import asyncio
import json
import os
import sys
import logging
from typing import List, Dict, Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class MCPClient:
    """
    Client for interacting with n8n-mcp server.
    Handles connection, tool listing, and tool execution.
    """
    def __init__(self, command: str = "npx", args: List[str] = ["n8n-mcp"]):
        self.command = command
        self.args = args
        self.session: Optional[ClientSession] = None
        self._client_context = None
        self._exit_stack = None
        self.local_tools = {} # New: Registry for local tool implementations

    async def connect(self):
        """Connect to the MCP server via stdio"""
        if self.session:
            return

        # Find absolute path for command if possible
        actual_command = self.command
        import shutil
        found_path = shutil.which(self.command)
        if not found_path:
            # Fallback to common locations if not in PATH (common in systemd)
            for fallback in ["/usr/bin/npx", "/usr/local/bin/npx", "/bin/npx"]:
                if os.path.exists(fallback):
                    actual_command = fallback
                    logger.info(f"Found {self.command} at fallback path: {fallback}")
                    break
        else:
            actual_command = found_path

        # Ensure PATH includes standard system locations
        current_path = os.environ.get("PATH", "")
        standard_paths = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        if standard_paths not in current_path:
            full_path = f"{current_path}:{standard_paths}" if current_path else standard_paths
        else:
            full_path = current_path

        server_params = StdioServerParameters(
            command=actual_command,
            args=self.args,
            env={
                "MCP_MODE": "stdio",
                "LOG_LEVEL": "error",
                "DISABLE_CONSOLE_OUTPUT": "true",
                "N8N_API_URL": os.getenv("N8N_INSTANCE_URL", "http://localhost:5678"),
                "N8N_API_KEY": os.getenv("N8N_API_KEY", ""),
                "PATH": full_path
            }
        )

        logger.info(f"Connecting to MCP server: {actual_command} {' '.join(self.args)}")
        
        try:
            self._client_context = stdio_client(server_params)
            read, write = await self._client_context.__aenter__()
            self.session = ClientSession(read, write)
            await self.session.__aenter__()
            await self.session.initialize()
            logger.info("MCP server connected and initialized")
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.session = None
            raise

    async def disconnect(self):
        """Disconnect from the MCP server"""
        if self.session:
            try:
                await self.session.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error disconnecting session: {e}")
            self.session = None
            
        if self._client_context:
            try:
                await self._client_context.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error closing context: {e}")
            self._client_context = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from both MCP server and local registry"""
        tools = []
        
        # 1. Get tools from MCP server
        if not self.session:
            try:
                await self.connect()
            except Exception:
                pass # Continue with local tools if server fails
        
        if self.session:
            try:
                result = await self.session.list_tools()
                for tool in result.tools:
                    tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    })
            except Exception as e:
                logger.error(f"Error listing MCP tools: {e}")
        
        # 2. Add local tools
        for name, info in self.local_tools.items():
            tools.append({
                "name": name,
                "description": info["description"],
                "inputSchema": info["inputSchema"]
            })
            
        return tools

    def register_local_tool(self, name: str, description: str, input_schema: Dict[str, Any], handler):
        """Register a local tool implementation"""
        self.local_tools[name] = {
            "description": description,
            "inputSchema": input_schema,
            "handler": handler
        }

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool (local or on the MCP server)"""
        # 1. Try local tools first
        if name in self.local_tools:
            try:
                logger.info(f"Calling local tool '{name}' with args: {json.dumps(arguments)}")
                result = await self.local_tools[name]["handler"](arguments)
                # Results must be list of content objects (like MCP)
                if isinstance(result, (dict, list)):
                    return [{"type": "text", "text": json.dumps(result, indent=2)}]
                return [{"type": "text", "text": str(result)}]
            except Exception as e:
                logger.error(f"Error calling local tool '{name}': {e}")
                return [{"type": "text", "text": f"Error: {str(e)}"}]

        # 2. Call MCP server
        if not self.session:
            await self.connect()
            
        try:
            logger.info(f"Calling MCP tool '{name}' with args: {json.dumps(arguments)}")
            result = await self.session.call_tool(name, arguments)
            return result.content
        except Exception as e:
            logger.error(f"Error calling tool '{name}': {e}")
            return [{"type": "text", "text": f"Error: {str(e)}"}]

# Singleton instance
_mcp_client_instance = None

async def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client instance"""
    global _mcp_client_instance
    if _mcp_client_instance is None:
        # Check if we should use local source or npx
        # For now, use npx n8n-mcp as it's the easiest to deploy
        # If npx is not available or we want to use the cloned repo:
        # client = MCPClient(command="node", args=["/path/to/n8n-mcp/dist/mcp/index.js"])
        _mcp_client_instance = MCPClient(command="npx", args=["-y", "n8n-mcp@latest"])
        await _mcp_client_instance.connect()
    return _mcp_client_instance
