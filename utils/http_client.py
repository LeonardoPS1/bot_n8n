"""
HTTP Client Utilities
Shared HTTP client with connection pooling for efficiency
"""

import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Persistent HTTP client with connection pooling
# Reuses connections across requests for better performance
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    """Get or create persistent HTTP client

    Returns:
        Shared AsyncClient instance with connection pooling
    """
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20
            ),
            follow_redirects=True,
            verify=False  # For self-signed certs
        )
    return _http_client


async def close_http_client():
    """Close the persistent HTTP client

    Call this when shutting down the application
    """
    global _http_client
    if _http_client:
        await _http_client.aclose()
        _http_client = None


async def make_http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Make HTTP request with shared client for better performance

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Optional request headers
        **kwargs: Additional arguments for httpx

    Returns:
        JSON response as dictionary

    Raises:
        httpx.HTTPStatusError: If request fails
    """
    client = get_http_client()
    response = await client.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response.json()
