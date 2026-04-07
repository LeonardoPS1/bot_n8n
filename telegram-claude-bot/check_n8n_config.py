#!/usr/bin/env python3
"""Deep check of n8n configuration"""

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

print("[=== Deep n8n Configuration Check ===]\n")

# Check all listening ports
print("[1] All listening ports...")
stdin, stdout, stderr = client.exec_command("sudo netstat -tlnp | grep LISTEN")
print(stdout.read().decode())

# Check n8n configuration
print("\n[2] n8n environment variables...")
stdin, stdout, stderr = client.exec_command("sudo cat /etc/systemd/system/n8n.service 2>/dev/null || cat ~/.n8n/config 2>/dev/null || echo 'Config not found in standard locations'")
print(stdout.read().decode())

# Check if we can access n8n API locally
print("\n[3] Testing n8n API locally...")
stdin, stdout, stderr = client.exec_command("curl -s -H 'X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyY2I5MzM0Mi05YTY2LTQxZWYtODJhZi1kM2JlYjExZGViNGMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDMxODE0NjYtOTViMi00ZGM1LWFhMjctODlkNzdmM2M2ZDEyIiwiaWF0IjoxNzc1NTc3NTc1fQ.eDKwfVpsqrDUYFCaL8HbcjqgEq5N74ImwTi9RBGfKw4' http://localhost:5678/api/v1/workflows 2>&1 | head -100")
print(stdout.read().decode())

# Check n8n URL configuration
print("\n[4] Checking n8n webhook/base URL...")
stdin, stdout, stderr = client.exec_command("sudo grep -r 'N8N_HOST\\|N8N_PORT\\|WEBHOOK_URL\\|N8N_PROTOCOL' /etc/systemd/system/n8n.service ~/.n8n/ 2>/dev/null || echo 'No URL config found'")
print(stdout.read().decode())

client.close()
