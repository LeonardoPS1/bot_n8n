#!/usr/bin/env python3
"""
n8n MCP Tools Expert
Expert guide for using n8n-mcp MCP tools effectively
Key insights:
- Tool selection guide for each task type
- Validation profiles (minimal/runtime/ai-friendly/strict)
- Smart parameters like branch="true" for IF nodes
- Auto-sanitization system behavior
"""


class MCPToolsExpert:
    """Expert in n8n-MCP tools usage and best practices"""

    TOOL_SELECTION_GUIDE = {
        "search_nodes": {
            "use_when": "Need to find nodes by type, name, or capability",
            "parameters": {
                "query": "search term",
                "includeExamples": "include usage examples",
                "source": "core|community"
            }
        },
        "validate_node": {
            "use_when": "Validating node configuration before execution",
            "parameters": {
                "nodeType": "exact node type",
                "config": "configuration object",
                "mode": "minimal|standard|full",
                "profile": "minimal|runtime|ai-friendly|strict"
            },
            "profiles": {
                "minimal": "Quick required fields check (<100ms)",
                "runtime": "Full validation with runtime compatibility",
                "ai-friendly": "Optimized for AI Agent workflows",
                "strict": "Most thorough validation"
            }
        },
        "search_templates": {
            "use_when": "Finding workflow templates",
            "parameters": {
                "searchMode": "by_metadata|by_task|by_nodes",
                "complexity": "simple|medium|advanced",
                "maxSetupMinutes": "max setup time filter"
            }
        },
        "validate_workflow": {
            "use_when": "Validating complete workflow",
            "checks": ["connections", "node_types", "expressions", "credentials"]
        }
    }

    SMART_PARAMETERS = {
        "IF_node": {
            "branch": {
                "true": "Main output (TRUE condition)",
                "false": "Second output (FALSE condition)",
                "note": "Required for bot connections with IF nodes"
            }
        },
        "HTTP_Request": {
            "sendBody": {
                "true": "Include body in POST/PUT/PATCH",
                "false": "Send without body",
                "default": "false",
                "warning": "60%+ of failures are due to missing sendBody=true"
            }
        },
        "Code_node": {
            "mode": {
                "runOnceForAllItems": "Process all items at once",
                "runOnceForEachItem": "Process each item separately",
                "default": "runOnceForAllItems"
            }
        },
        "Webhook": {
            "responseMode": {
                "onReceived": "Respond immediately",
                "lastNode": "Wait for workflow completion",
                "default": "onReceived"
            }
        }
    }


class WorkflowPatternsExpert:
    """Expert in proven n8n workflow patterns"""

    CORE_PATTERNS = {
        "webhook_processing": {
            "flow": "Webhook → Parse → Process → Response",
            "nodes": ["webhook", "set", "code", "if", "httpRequest", "respondToWebhook"],
            "use_case": "API endpoints, webhooks",
            "complexity": "medium",
            "key_consideration": "Webhook data under $json.body"
        },
        "http_api_integration": {
            "flow": "Schedule → HTTP Request → Process → Notify",
            "nodes": ["scheduleTrigger", "httpRequest", "code", "merge", "slack"],
            "use_case": "Periodic API calls, data sync",
            "complexity": "simple",
            "key_consideration": "Set sendBody=true for POST requests"
        },
        "database_operations": {
            "flow": "Trigger → Query → Transform → Update/Insert",
            "nodes": ["webhook", "postgres", "code", "splitInBatches", "postgres"],
            "use_case": "CRUD operations, data migration",
            "complexity": "medium",
            "key_consideration": "Use transactions for batch operations"
        },
        "ai_agent": {
            "flow": "Trigger → AI Agent → Tools → Response",
            "nodes": ["slack", "langchain.agent", "httpRequest", "slack"],
            "use_case": "AI assistants, chatbots",
            "complexity": "advanced",
            "key_consideration": "Streaming incompatible with switch/IF nodes"
        },
        "batch_processing": {
            "flow": "Trigger → Split → Process Each → Aggregate",
            "nodes": ["scheduleTrigger", "postgres", "splitInBatches", "httpRequest", "merge", "postgres"],
            "use_case": "Bulk operations, API rate limiting",
            "complexity": "advanced",
            "key_consideration": "Configure reset=true for repeated executions"
        }
    }

    CONNECTION_RULES = {
        "IF_node_multi_output": "Use branch='true' or branch='false' for connections",
        "Webhook_response": "Only respondToWebhook can send response to webhook",
        "AI_streaming": "Cannot use with Switch, IF, or Merge nodes",
        "Split_batches": "Must configure batch size and reset for proper looping"
    }


class ValidationExpert:
    """Expert in workflow validation and error interpretation"""

    ERROR_CATALOG = {
        "NODE_MISSING": {
            "cause": "Node type not found",
            "solution": "Check node type spelling, verify node is installed",
            "false_positive": "Community node may not be loaded"
        },
        "REQUIRED_FIELD": {
            "cause": "Required parameter missing",
            "solution": "Check node documentation for required fields",
            "common_fields": {
                "httpRequest": ["url", "method"],
                "slack": ["channel", "text"],
                "set": ["values"],
                "code": ["language", "code"]
            }
        },
        "EXPRESSION_ERROR": {
            "cause": "Invalid expression syntax",
            "solution": "Use $json.body for webhook, $node['Name'] for references",
            "validator": "Use ExpressionSyntaxExpert skill"
        },
        "CONNECTION_ERROR": {
            "cause": "Invalid node connection",
            "solution": "Check sourcePort/targetPort match node outputs",
            "IF_special": "Use branch parameter for TRUE/FALSE routing"
        },
        "CREDENTIAL_ERROR": {
            "cause": "Invalid or missing credentials",
            "solution": "Verify credential exists and has correct permissions"
        }
    }

    FALSE_POSITIVES = {
        "deprecated_warning": "Node may still work with deprecated option",
        "unused_output": "Output may be used conditionally",
        "expression_complexity": "Complex expressions are valid"
    }


class NodeConfigExpert:
    """Expert in operation-aware node configuration"""

    PROPERTY_DEPENDENCIES = {
        "httpRequest": {
            "sendBody": {
                "requires": "POST|PUT|PATCH",
                "affects": "contentType",
                "note": "Must set sendBody=true for body to be sent"
            },
            "authentication": {
                "requires": "genericCredentialType or predefinedCredentialType",
                "options": ["header", "genericCredentialType", "predefinedCredentialType"]
            }
        },
        "slack": {
            "channel": {
                "requires": "channel ID, not name",
                "how_to_find": "Use 'List Channels' operation"
            },
            "attachments": {
                "requires": "Array of attachment objects",
                "format": "[{text, title, color, ...}]"
            }
        },
        "code": {
            "mode": {
                "affects": "item processing",
                "options": ["runOnceForAllItems", "runOnceForEachItem"]
            },
            "language": {
                "options": ["javaScript", "python"],
                "python_limitation": "No external libraries (requests, pandas)"
            }
        },
        "if": {
            "combineOperation": {
                "affects": "how multiple conditions are evaluated",
                "options": ["all", "any", "some"]
            }
        }
    }

    AI_CONNECTION_TYPES = [
        "8 types for AI Agent workflows",
        "Streaming incompatible with flow control",
        "Vector store connections require embeddings model",
        "Tool connections must match AI provider"
    ]


class CodeJavaScriptExpert:
    """Expert in writing effective JavaScript code in n8n Code nodes"""

    DATA_ACCESS_PATTERNS = {
        "all_items": "$input.all()",
        "first_item": "$input.first()",
        "single_item": "$input.item",
        "item_by_index": "$input.item(0)",
        "json_data": "input.item.json"
    }

    RETURN_FORMAT = "return [{json: {...}}]"

    BUILTIN_FUNCTIONS = {
        "$helpers.httpRequest(url, options)": "Make HTTP request",
        "$helpers.dateTime(zone)": "Get current datetime",
        "$jmespath(data, expression)": "JMESPath query",
        "$helpers.formatDateTime(date, format)": "Format datetime"
    }

    TOP_5_ERRORS = {
        "no_return": "Forgot return statement - must return [{json: {...}}]",
        "wrong_format": "Returned array without 'json' wrapper",
        "sync_instead_async": "Used await without async function",
        "missing_json": "Returned {json: {...}} without array wrapper",
        "undefined_access": "Accessed property without checking if exists"
    }


class CodePythonExpert:
    """Expert in Python code in n8n Code nodes"""

    CRITICAL_LIMITATION = "No external libraries (requests, pandas, numpy)"

    STANDARD_LIBRARY = {
        "json": "JSON encoding/decoding",
        "datetime": "Date/time operations",
        "re": "Regular expressions",
        "base64": "Base64 encoding/decoding",
        "hashlib": "Hashing functions",
        "uuid": "UUID generation",
        "urllib": "Basic HTTP (limited)",
        "http.client": "HTTP client (limited)"
    }

    HTTP_WORKAROUNDS = {
        "no_requests": "Use $helpers.httpRequest() instead",
        "no_pandas": "Process JSON manually with loops",
        "no_numpy": "Use Python lists and comprehensions"
    }


__all__ = [
    'MCPToolsExpert',
    'WorkflowPatternsExpert',
    'ValidationExpert',
    'NodeConfigExpert',
    'CodeJavaScriptExpert',
    'CodePythonExpert'
]
