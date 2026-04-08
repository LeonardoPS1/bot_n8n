"""
Environment File Management Utilities
Functions for managing .env file updates
"""

import aiofiles
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def update_env_file(
    env_path: str,
    key: str,
    value: str
) -> bool:
    """Update or add a key-value pair in .env file (async)

    Args:
        env_path: Path to .env file
        key: Environment variable name
        value: Value to set

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(env_path)

        # Read current content
        if path.exists():
            async with aiofiles.open(env_path, 'r') as f:
                lines = await f.readlines()
        else:
            lines = []

        # Update or add the key
        updated = False
        key_prefix = f"{key}="

        for i, line in enumerate(lines):
            if line.strip().startswith(key_prefix):
                lines[i] = f"{key}={value}\n"
                updated = True
                break

        if not updated:
            lines.append(f"{key}={value}\n")

        # Write back
        async with aiofiles.open(env_path, 'w') as f:
            await f.writelines(lines)

        logger.info(f"Updated {key} in {env_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to update {env_path}: {e}")
        return False


async def read_env_value(env_path: str, key: str, default: str = "") -> str:
    """Read a value from .env file

    Args:
        env_path: Path to .env file
        key: Environment variable name
        default: Default value if key not found

    Returns:
        The value or default
    """
    try:
        path = Path(env_path)
        if not path.exists():
            return default

        async with aiofiles.open(env_path, 'r') as f:
            async for line in f:
                if line.strip().startswith(f"{key}="):
                    # Extract value after the equals sign
                    _, value = line.strip().split("=", 1)
                    return value.strip()

        return default

    except Exception as e:
        logger.warning(f"Failed to read {key} from {env_path}: {e}")
        return default


async def backup_env_file(env_path: str) -> bool:
    """Create a backup of .env file

    Args:
        env_path: Path to .env file

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(env_path)
        if path.exists():
            backup_path = path.with_suffix('.backup')

            async with aiofiles.open(env_path, 'r') as f:
                content = await f.read()

            async with aiofiles.open(backup_path, 'w') as f:
                await f.write(content)

            logger.info(f"Created backup: {backup_path}")
            return True

        return False

    except Exception as e:
        logger.error(f"Failed to backup {env_path}: {e}")
        return False
