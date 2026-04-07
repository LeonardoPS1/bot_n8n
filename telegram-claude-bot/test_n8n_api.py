#!/usr/bin/env python3
"""Test n8n API connectivity with different configurations"""

import httpx
import asyncio

async def test_n8n_api():
    """Test n8n API with current configuration"""

    # Test 1: Current configuration
    api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyY2I5MzM0Mi05YTY2LTQxZWYtODJhZi1kM2JlYjExZGViNGMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDMxODE0NjYtOTViMi00ZGM1LWFhMjctODlkNzdmM2M2ZDEyIiwiaWF0IjoxNzc1NTc3NTc1fQ.eDKwfVpsqrDUYFCaL8HbcjqgEq5N74ImwTi9RBGfKw4"
    instance_url = "https://n8n.aicorebots.com"

    print("[=] Testing n8n API connectivity...")
    print(f"    URL: {instance_url}")
    print(f"    API Key: {api_key[:50]}...")

    headers = {
        "X-N8N-API-KEY": api_key,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{instance_url}/api/v1/workflows",
                headers=headers
            )
            print(f"\n[=] Response Status: {response.status_code}")
            print(f"[=] Response Headers: {dict(response.headers)}")

            if response.status_code == 200:
                data = response.json()
                print(f"[=] SUCCESS! Found {len(data.get('data', data))} workflows")
                return True
            else:
                print(f"[=] FAILED: {response.text}")
                return False

    except Exception as e:
        print(f"[=] ERROR: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_n8n_api())
