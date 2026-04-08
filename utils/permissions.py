"""
Permission and Authorization Utilities
Shared functions for checking user permissions
"""

from typing import List


def check_permission(user_id: int, allowed_users: List[str]) -> bool:
    """Check if user is allowed to use the bot

    Args:
        user_id: Telegram user ID
        allowed_users: List of allowed user IDs (strings)

    Returns:
        True if user is allowed, False otherwise
    """
    if not allowed_users:
        return True
    return str(user_id) in allowed_users or "*" in allowed_users


def check_admin_permission(user_id: int, admin_users: List[str]) -> bool:
    """Check if user has admin permissions

    Args:
        user_id: Telegram user ID
        admin_users: List of admin user IDs (strings)

    Returns:
        True if user is admin, False otherwise
    """
    if not admin_users:
        return False
    return str(user_id) in admin_users or "*" in admin_users
