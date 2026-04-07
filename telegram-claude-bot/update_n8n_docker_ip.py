#!/usr/bin/env python3
"""Update n8n configuration to use Docker internal IP"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASSWORD = "Cool220479..@"

# New n8n configuration (Docker internal IP)
NEW_N8N_URL = "http://10.11.0.4:5678"
NEW_N8N_INSTANCE_URL = "http://10.11.0.4:5678"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)

print("[=== Updating n8n Configuration ===]\n")

# Update .env file with new n8n URL
print("[1] Updating .env with Docker internal IP...")
stdin, stdout, stderr = client.exec_command(f"""
sudo sed -i 's|^N8N_INSTANCE_URL=.*|N8N_INSTANCE_URL={NEW_N8N_INSTANCE_URL}|' /opt/claudio-bot/.env
sudo cat /opt/claudio-bot/.env | grep N8N_INSTANCE_URL
""")
print(stdout.read().decode())

# Test the new configuration
print("\n[2] Testing n8n API with new URL...")
stdin, stdout, stderr = client.exec_command(f"""
curl -s -w '\\nHTTP Status: %{{http_code}}\\n' \\
  -H 'X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyY2I5MzM0Mi05YTY2LTQxZWYtODJhZi1kM2JlYjExZGViNGMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDMxODE0NjYtOTViMi00ZGM1LWFhMjctODlkNzdmM2M2ZDEyIiwiaWF0IjoxNzc1NTc3NTc1fQ.eDKwfVpsqrDUYFCaL8HbcjqgEq5N74ImwTi9RBGfKw4' \\
  '{NEW_N8N_URL}/api/v1/workflows' | head -50
""")
print(stdout.read().decode())

# Restart services
print("\n[3] Restarting Claudio services...")
commands = [
    "sudo systemctl restart claudio-server.service",
    "sleep 2",
    "sudo systemctl restart claudio-telegram-bot.service"
]

for cmd in commands:
    print(f"    {cmd}")
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.read()

# Wait and check status
import time
time.sleep(3)

print("\n[4] Service Status...")
stdin, stdout, stderr = client.exec_command("sudo systemctl status claudio-server --no-pager | head -12")
print(stdout.read().decode())

print("\n[5] Testing Claudio health endpoint...")
stdin, stdout, stderr = client.exec_command("curl -s http://localhost:8000/health")
health_output = stdout.read().decode()
print(health_output)

client.close()

print("\n[+] Configuration updated!")
print(f"[+] n8n now accessible via: {NEW_N8N_URL}")
