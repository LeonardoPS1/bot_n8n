#!/usr/bin/env python3
"""Test n8n API on VPS"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASSWORD = "Cool220479..@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)

print("[=== Testing n8n API from VPS ===]\n")

# Test with curl
print("[1] Testing n8n API with curl...")
stdin, stdout, stderr = client.exec_command("""
curl -s -w '\n\nHTTP Status: %{http_code}\n' \
  -H 'X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyY2I5MzM0Mi05YTY2LTQxZWYtODJhZi1kM2JlYjExZGViNGMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDMxODE0NjYtOTViMi00ZGM1LWFhMjctODlkNzdmM2M2ZDEyIiwiaWF0IjoxNzc1NTc3NTc1fQ.eDKwfVpsqrDUYFCaL8HbcjqgEq5N74ImwTi9RBGfKw4' \
  'https://n8n.aicorebots.com/api/v1/workflows' | head -100
""")
print(stdout.read().decode())

# Check current env
print("\n[2] Current N8N configuration in .env...")
stdin, stdout, stderr = client.exec_command("sudo grep -E 'N8N_' /opt/claudio-bot/.env | sed 's/=.*/=***HIDDEN***/'")
print(stdout.read().decode())

client.close()
