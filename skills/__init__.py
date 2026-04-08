#!/usr/bin/env python3
"""
Claudio Skills Package - n8n Expert Skills
"""

from . import n8n_expression_syntax, n8n_other_skills

__all__ = [
    'n8n_expression_syntax',
    'n8n_other_skills'
]

# Initialize all skills
SKILLS = {
    'expression_syntax': n8n_expression_syntax,
    'other_skills': n8n_other_skills
}

def get_skill(skill_name: str):
    """Get a specific skill module"""
    return SKILLS.get(skill_name)

def list_skills():
    """List all available skills"""
    return list(SKILLS.keys())
