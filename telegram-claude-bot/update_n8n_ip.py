#!/usr/bin/env python3
"""Update n8n configuration to use direct IP"""

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

print("[=== Updating n8n configuration ===]\n")

# Check if n8n is running and on which port
print("[1] Checking n8n process...")
stdin, stdout, stderr = client.exec_command("ps aux | grep n8n | grep -v grep")
print(stdout.read().decode() or "    n8n process not found")

# Check n8n port
print("\n[2] Checking n8n port...")
stdin, stdout, stderr = client.exec_command("sudo netstat -tlnp | grep -E ':(5678|80|443)'")
print(stdout.read().decode() or "    No n8n port found (checking default ports)")

# Check if n8n is behind a proxy
print("\n[3] Checking nginx/apache configuration...")
stdin, stdout, stderr = client.exec_command("sudo cat /etc/nginx/sites-enabled/* 2>/dev/null | grep -E 'server_name|proxy_pass|listen' | head -20")
print(stdout.read().decode() or "    No nginx config found")

print("\n[4] Testing direct IP access...")
# Test different possible n8n ports
ports = ["5678", "80", "443"]
for port in ports:
    print(f"\n    Testing port {port}...")
    stdin, stdout, stderr = client.exec_command(f"curl -s -m 3 -w 'HTTP:%{{http_code}}' http://localhost:{port}/healthz 2>/dev/null || echo 'Failed'")
    result = stdout.read().decode().strip()
    print(f"      Result: {result}")

client.close()
