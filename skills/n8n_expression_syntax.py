#!/usr/bin/env python3
"""
n8n Expression Syntax Expert
Validates n8n expression syntax and fixes common errors
Activates when writing expressions, using {{}} syntax, accessing $json/$node variables
"""

import re
from typing import Dict, List, Any, Optional

# Key insights covered by this skill:
# - Webhook data is under `$json.body` (not `$json`)
# - Use {{}} for expressions, not in Code nodes
# - Node names with spaces require bracket notation: `{{$node["HTTP Request"]}}`
# - Array access: `$json.items[0].name`
# - Nested fields: `$json.data.user.email`
# - Previous node: `$node["HTTP Request"].json.result`


class ExpressionSyntaxExpert:
    """Expert in n8n expression syntax validation and correction"""

    # Common syntax patterns
    PATTERNS = {
        "webhook_body": {
            "correct": r"\$json\.body",
            "wrong_patterns": [
                (r"\$json(?!\.body)", "Webhook data is under $json.body, not $json directly"),
                (r"\$data", "Use $json, not $data for webhook data")
            ],
            "examples": [
                ("$json.body.email", "Access email field from webhook"),
                ("$json.body.user.name", "Access nested field"),
                ("$json.body.items[0]", "Access first array item")
            ]
        },
        "node_reference": {
            "correct": r'\$node\[".*?"\]\.json\.',
            "wrong_patterns": [
                (r'\$node\.[a-zA-Z0-9_]+\.json', "Node names with spaces require bracket notation"),
                (r"\$node\['.*?'\]\.json", "Use double quotes, not single quotes"),
            ],
            "examples": [
                ('$node["HTTP Request"].json.result', "Reference HTTP Request output"),
                ('$node["Get Data"].json.data', "Reference Get Data output"),
                ('$node["Slack"].json.message.ts', "Reference Slack timestamp")
            ]
        },
        "array_access": {
            "correct": r"\$json\.[a-zA-Z0-9_]+\[\d+\]",
            "wrong_patterns": [
                (r"\$json\.[a-zA-Z0-9_]+\.\d+", "Arrays require bracket notation"),
            ],
            "examples": [
                ("$json.items[0]", "First item in items array"),
                ("$json.users[5].name", "Name of 6th user"),
                ("$json.data[0].results[1]", "Nested array access")
            ]
        },
        "environment_variables": {
            "correct": r"\$env\.[a-zA-Z0-9_]+",
            "examples": [
                ("$env.API_KEY", "Access API_KEY environment variable"),
                ("$env.DATABASE_URL", "Access database URL"),
                ("$env.WEBHOOK_URL", "Access webhook URL")
            ]
        },
        "datetime": {
            "correct": r"\$now",
            "formats": ["ISO8601", "timestamp", "date"],
            "examples": [
                ("$now", "Current timestamp"),
                ("$now.toISO()", "ISO 8601 format"),
                ("$now.plus({ hours: 1 })", "One hour from now")
            ]
        }
    }

    # Common error patterns (covering 62%+ of failures)
    COMMON_ERRORS = {
        "webhook_direct_access": {
            "error": "$json.field instead of $json.body.field",
            "fix": "Add .body after $json for webhook data",
            "pattern": r"webhook.*\$json(?!\.body)",
            "severity": "critical"
        },
        "node_name_spaces": {
            "error": "$node.Node Name with dots",
            "fix": "Use bracket notation: $node[\"Node Name\"]",
            "pattern": r'\$node\.[A-Z][a-zA-Z\s]*\.',
            "severity": "critical"
        },
        "array_dot_notation": {
            "error": "$json.items.0 instead of $json.items[0]",
            "fix": "Use bracket notation for arrays",
            "pattern": r"\$json\.[a-zA-Z]+\.\d+",
            "severity": "high"
        },
        "missing_quotes": {
            "error": "Missing quotes in expression",
            "fix": "Wrap strings in single or double quotes",
            "pattern": r'= [a-zA-Z]+(?=[,}])',
            "severity": "medium"
        },
        "wrong_curly_braces": {
            "error": "{{}} used in Code node",
            "fix": "Remove {{}} in Code nodes, use plain JavaScript",
            "pattern": r'code.*{{.*}}',
            "severity": "high"
        }
    }

    @classmethod
    def validate_expression(cls, expression: str, context: str = "") -> Dict[str, Any]:
        """
        Validate an n8n expression and return diagnostics

        Args:
            expression: The expression to validate
            context: Additional context about where this is used (node type, etc.)

        Returns:
            Validation result with errors, warnings, and suggestions
        """
        result = {
            "expression": expression,
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }

        # Check for common error patterns
        for error_name, error_info in cls.COMMON_ERRORS.items():
            if re.search(error_info["pattern"], expression + " " + context, re.IGNORECASE):
                result["valid"] = False
                result["errors"].append({
                    "type": error_name,
                    "severity": error_info["severity"],
                    "message": error_info["error"],
                    "fix": error_info["fix"],
                    "position": cls._find_error_position(expression, error_info["pattern"])
                })

        # Check for webhook-specific issues
        if "webhook" in context.lower() and not re.search(r'\$json\.body', expression):
            if re.search(r'\$json', expression):
                result["warnings"].append({
                    "type": "webhook_body_missing",
                    "message": "Webhook data is under $json.body, not $json directly",
                    "suggestion": "Use $json.body.field instead of $json.field"
                })

        # Check for node reference issues
        if re.search(r'\$node\.', expression):
            if not re.search(r'\$node\[', expression):
                result["warnings"].append({
                    "type": "node_reference_format",
                    "message": "Node references with spaces require bracket notation",
                    "suggestion": 'Use $node["Node Name"] instead of $node.Node Name'
                })

        return result

    @classmethod
    def _find_error_position(cls, expression: str, pattern: str) -> Dict[str, int]:
        """Find the position of an error in the expression"""
        match = re.search(pattern, expression, re.IGNORECASE)
        if match:
            return {
                "start": match.start(),
                "end": match.end(),
                "snippet": expression[match.start():match.end()]
            }
        return {}

    @classmethod
    def suggest_correction(cls, expression: str, error_type: str) -> Optional[str]:
        """Suggest a correction for a given expression error"""
        corrections = {
            "webhook_direct_access": lambda e: e.replace("$json.", "$json.body.", 1),
            "node_name_spaces": lambda e: re.sub(r'\$node\.([a-zA-Z][a-zA-Z0-9_ ]+)', r'$node["\1"]', e),
            "array_dot_notation": lambda e: re.sub(r'\.(\d+)(?=[^[]|$)', r'[\1]', e),
        }

        corrector = corrections.get(error_type)
        if corrector:
            return corrector(expression)
        return None

    @classmethod
    def get_examples(cls, concept: str) -> List[str]:
        """Get code examples for a specific concept"""
        for pattern_name, pattern_info in cls.PATTERNS.items():
            if concept.lower() in pattern_name.lower():
                return [ex[0] for ex in pattern_info.get("examples", [])]
        return []

    @classmethod
    def explain_syntax(cls, expression: str) -> str:
        """Explain what an expression does"""
        explanation = []

        if "$json.body" in expression:
            explanation.append("📥 Accesses webhook body data")
        elif "$json" in expression:
            explanation.append("📥 Accesses JSON data")

        if "$node[" in expression:
            node_match = re.search(r'\$node\["([^"]+)"\]', expression)
            if node_match:
                explanation.append(f"🔗 References output from node: {node_match.group(1)}")

        if "[0]" in expression or "[1]" in expression:
            explanation.append("📊 Accesses array element by index")

        if "$env." in expression:
            env_match = re.search(r'\$env\.([a-zA-Z0-9_]+)', expression)
            if env_match:
                explanation.append(f"🔐 Reads environment variable: {env_match.group(1)}")

        if "$now" in expression:
            explanation.append("⏰ Current timestamp")

        return "\n".join(explanation) if explanation else "🤔 Unknown expression pattern"


# Export for use in other modules
__all__ = ['ExpressionSyntaxExpert']
