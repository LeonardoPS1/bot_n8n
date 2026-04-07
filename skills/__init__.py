#!/usr/bin/env python3
"""
Claudio Skills Package - 7 Specialized n8n Expert Skills
"""

from . import (
    n8n_expression_syntax,
    n8n_mcp_tools_expert,
    n8n_workflow_patterns,
    n8n_validation_expert,
    n8n_node_configuration,
    n8n_code_javascript,
    n8n_code_python
)

__all__ = [
    'n8n_expression_syntax',
    'n8n_mcp_tools_expert',
    'n8n_workflow_patterns',
    'n8n_validation_expert',
    'n8n_node_configuration',
    'n8n_code_javascript',
    'n8n_code_python'
]

# Initialize all skills
SKILLS = {
    'expression_syntax': n8n_expression_syntax,
    'mcp_tools': n8n_mcp_tools_expert,
    'workflow_patterns': n8n_workflow_patterns,
    'validation': n8n_validation_expert,
    'node_config': n8n_node_configuration,
    'code_js': n8n_code_javascript,
    'code_python': n8n_code_python
}

def get_skill(skill_name: str):
    """Get a specific skill module"""
    return SKILLS.get(skill_name)

def list_skills():
    """List all available skills"""
    return list(SKILLS.keys())
