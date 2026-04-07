#!/usr/bin/env python3
"""Check if n8n is running in Docker"""

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

print("[=== Checking if n8n is in Docker ===]\n")

# Check Docker containers
print("[1] Docker containers...")
stdin, stdout, stderr = client.exec_command("sudo docker ps -a")
docker_output = stdout.read().decode()
print(docker_output)

# Check docker-compose
print("\n[2] Docker compose services...")
stdin, stdout, stderr = client.exec_command("sudo docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null || echo 'No compose found'")
print(stdout.read().decode())

# Check if n8n container is running and its port mapping
if "n8n" in docker_output.lower():
    print("\n[3] n8n container details...")
    stdin, stdout, stderr = client.exec_command("sudo docker inspect $(sudo docker ps -q -f name=n8n) 2>/dev/null | grep -E 'PortBindings|IpAddress' | head -20")
    print(stdout.read().decode())

    print("\n[4] Testing n8n API from within Docker network...")
    stdin, stdout, stderr = client.exec_command("sudo docker exec $(sudo docker ps -q -f name=n8n) curl -s http://localhost:5678/healthz 2>/dev/null || echo 'Cannot reach n8n from container'")
    print(stdout.read().decode())

print("\n[5] Finding n8n port mapping...")
stdin, stdout, stderr = client.exec_command("sudo docker port $(sudo docker ps -q -f name=n8n) 2>/dev/null || echo 'No port mapping found'")
print(stdout.read().decode())

client.close()
