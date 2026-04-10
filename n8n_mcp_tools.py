#!/usr/bin/env python3
"""
n8n MCP Tools - Python implementation of n8n-MCP functionality
Direct connection to n8n API for workflow operations
"""

import httpx
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class N8NConfig:
    """n8n API Configuration"""
    api_key: str
    instance_url: str
    timeout: int = 30
    host_header: Optional[str] = None  # For Traefik routing


class N8NMCPClient:
    """
    Python implementation of n8n-MCP tools
    Provides direct access to n8n API operations
    """

    def __init__(self, config: N8NConfig):
        self.config = config
        self.base_url = f"{config.instance_url}/api/v1"
        self.headers = {
            "X-N8N-API-KEY": config.api_key,
            "Content-Type": "application/json"
        }
        # Add Host header for Traefik routing
        if config.host_header:
            self.headers["Host"] = config.host_header
        self.timeout = config.timeout

    async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to n8n API"""
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,  # Follow 301/302 redirects
            verify=False  # Disable SSL verification for localhost/self-signed certs
        ) as client:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"{method} {url}")

            response = await client.request(
                method,
                url,
                headers=self.headers,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

    # ==================== WORKFLOW OPERATIONS ====================

    async def list_workflows(self, **filters) -> List[Dict[str, Any]]:
        """List all workflows with optional filters"""
        params = {}
        if filters:
            params.update(filters)

        result = await self._request("GET", "/workflows", params=params)
        return result.get("data", result) if isinstance(result, dict) else result

    async def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get a specific workflow by ID"""
        return await self._request("GET", f"/workflows/{workflow_id}")

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow"""
        return await self._request("POST", "/workflows", json=workflow_data)

    async def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow"""
        return await self._request("PUT", f"/workflows/{workflow_id}", json=workflow_data)

    async def delete_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Delete a workflow"""
        return await self._request("DELETE", f"/workflows/{workflow_id}")

    async def activate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Activate a workflow"""
        return await self._request("POST", f"/workflows/{workflow_id}/activate")

    async def deactivate_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Deactivate a workflow"""
        return await self._request("POST", f"/workflows/{workflow_id}/deactivate")

    # ==================== NODE OPERATIONS ====================

    async def get_node_documentation(self, node_type: str) -> Dict[str, Any]:
        """
        Get documentation for a specific node type
        This simulates the get_node operation from n8n-MCP
        """
        # n8n API doesn't have direct node documentation endpoint
        # We'll return structured information about the node
        return {
            "nodeType": node_type,
            "description": f"Documentation for {node_type}",
            "note": "Full node documentation requires local n8n instance or n8n docs"
        }

    async def search_nodes(
        self,
        query: str = "",
        source: str = "core",
        include_examples: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for nodes by name, description, or capability
        Simulates search_nodes from n8n-MCP
        """
        # n8n has 1396 nodes (812 core + 584 community)
        # This is a simplified implementation

        # Common node types
        core_nodes = [
            {"type": "n8n-nodes-base.webhook", "category": "trigger", "description": "Starts workflow on HTTP request"},
            {"type": "n8n-nodes-base.httpRequest", "category": "action", "description": "Makes an HTTP request"},
            {"type": "n8n-nodes-base.setCode", "category": "logic", "description": "Runs JavaScript or Python code"},
            {"type": "n8n-nodes-base.if", "category": "logic", "description": "Splits workflow based on condition"},
            {"type": "n8n-nodes-base.merge", "category": "logic", "description": "Merges data from multiple streams"},
            {"type": "n8n-nodes-base.switch", "category": "logic", "description": "Routes data based on rules"},
            {"type": "n8n-nodes-base.set", "category": "data", "description": "Sets values on data"},
            {"type": "n8n-nodes-base.noOp", "category": "utility", "description": "Does nothing (pass through)"},
            {"type": "@n8n/n8n-nodes-langchain.agent", "category": "ai", "description": "AI Agent with LangChain"},
            {"type": "n8n-nodes-base.slack", "category": "communication", "description": "Sends messages to Slack"},
            {"type": "n8n-nodes-base.emailSend", "category": "communication", "description": "Sends emails"},
            {"type": "n8n-nodes-base.mysql", "category": "database", "description": "MySQL database operations"},
            {"type": "n8n-nodes-base.postgres", "category": "database", "description": "PostgreSQL operations"},
            {"type": "n8n-nodes-base.scheduleTrigger", "category": "trigger", "description": "Triggers on schedule"},
            {"type": "n8n-nodes-base.manualTrigger", "category": "trigger", "description": "Manual trigger"},
            {"type": "n8n-nodes-base.splitInBatches", "category": "data", "description": "Splits data into batches"},
        ]

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                node for node in core_nodes
                if query_lower in node["type"].lower() or
                   query_lower in node["description"].lower() or
                   query_lower in node["category"].lower()
            ]
        else:
            results = core_nodes

        return results

    # ==================== TEMPLATE OPERATIONS ====================

    async def search_templates(
        self,
        query: str = "",
        complexity: str = "",
        category: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search for workflow templates
        Simulates search_templates from n8n-MCP (2709+ templates)
        """
        # This is a simplified implementation
        # Real implementation would query n8n templates API

        templates = [
            {"id": "1", "name": "Webhook to Slack", "category": "integration", "complexity": "simple"},
            {"id": "2", "name": "HTTP API Integration", "category": "api", "complexity": "simple"},
            {"id": "3", "name": "Data Transformation Pipeline", "category": "data", "complexity": "medium"},
            {"id": "4", "name": "AI Agent Workflow", "category": "ai", "complexity": "advanced"},
            {"id": "5", "name": "Database Sync", "category": "database", "complexity": "medium"},
            {"id": "6", "name": "Email Automation", "category": "communication", "complexity": "simple"},
            {"id": "7", "name": "Scheduled Report", "category": "automation", "complexity": "simple"},
            {"id": "8", "name": "Webhook Processing", "category": "trigger", "complexity": "medium"},
            {"id": "9", "name": "Batch Processing", "category": "data", "complexity": "advanced"},
            {"id": "10", "name": "Conditional Routing", "category": "logic", "complexity": "simple"},
        ]

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                t for t in templates
                if query_lower in t["name"].lower() or
                   query_lower in t["category"].lower()
            ]
        else:
            results = templates

        # Filter by complexity
        if complexity and complexity != "any":
            results = [t for t in results if t["complexity"] == complexity]

        # Filter by category
        if category:
            results = [t for t in results if t["category"] == category]

        return results

    # ==================== VALIDATION OPERATIONS ====================

    async def validate_workflow_structure(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate workflow structure
        Simulates validate_workflow from n8n-MCP
        """
        issues = []
        warnings = []

        # Basic validation
        if "nodes" not in workflow_data:
            issues.append("Workflow has no nodes")
        elif len(workflow_data["nodes"]) == 0:
            issues.append("Workflow has empty nodes array")

        # Check for connections
        if "connections" in workflow_data:
            for node_id, connections in workflow_data["connections"].items():
                if not connections:
                    warnings.append(f"Node {node_id} has no connections")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    async def validate_node_configuration(
        self,
        node_type: str,
        node_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate node configuration
        Simulates validate_node from n8n-MCP
        """
        issues = []
        warnings = []

        # Check for required fields
        if "parameters" not in node_data:
            warnings.append("Node has no parameters configured")

        # Node-specific validation
        if node_type == "n8n-nodes-base.httpRequest":
            if "url" not in node_data.get("parameters", {}):
                issues.append("HTTP Request node requires URL")

        elif node_type == "n8n-nodes-base.slack":
            if "channel" not in node_data.get("parameters", {}):
                issues.append("Slack node requires channel")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }

    # ==================== EXECUTION OPERATIONS ====================

    async def get_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get workflow executions"""
        endpoint = "/executions"
        params = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id

        result = await self._request("GET", endpoint, params=params)
        return result.get("data", result) if isinstance(result, dict) else result

    async def test_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Test a workflow execution"""
        return await self._request(
            "POST",
            f"/workflows/{workflow_id}/test",
            json=data or {}
        )

    # ==================== HEALTH CHECK ====================

    async def health_check(self) -> Dict[str, Any]:
        """Check n8n API connectivity"""
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
                return {
                    "status": "healthy",
                    "instance": self.config.instance_url,
                    "authenticated": True
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "instance": self.config.instance_url
            }
