import os
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)

class SkillsLoader:
    """
    Loads specialized n8n skills from the n8n-skills repository.
    """
    def __init__(self, skills_dir: str):
        self.skills_dir = Path(skills_dir)
        self.skills_content = {}

    def load_skills(self) -> str:
        """
        Walks through the skills directory and loads all SKILL.md files.
        Returns a combined prompt string.
        """
        if not self.skills_dir.exists():
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return ""

        combined_skills = ["\n## SPECIALIZED N8N SKILLS\n"]
        
        # Walk through subdirectories (each represents a skill)
        for skill_path in self.skills_dir.glob("*/SKILL.md"):
            skill_name = skill_path.parent.name
            try:
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_skills.append(f"### SKILL: {skill_name}\n{content}\n")
                    logger.info(f"Loaded skill: {skill_name}")
            except Exception as e:
                logger.error(f"Error loading skill {skill_name}: {e}")

        # Also load common mistakes if they exist
        for mistake_path in self.skills_dir.glob("*/COMMON_MISTAKES.md"):
            skill_name = mistake_path.parent.name
            try:
                with open(mistake_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    combined_skills.append(f"### COMMON MISTAKES: {skill_name}\n{content}\n")
            except Exception as e:
                logger.error(f"Error loading common mistakes for {skill_name}: {e}")

        return "\n".join(combined_skills)

def get_enhanced_system_prompt(base_prompt: str, skills_dir: str) -> str:
    """
    Combines the base system prompt with specialized skills.
    """
    loader = SkillsLoader(skills_dir)
    skills_prompt = loader.load_skills()
    
    if not skills_prompt:
        return base_prompt
        
    return base_prompt + "\n" + skills_prompt
