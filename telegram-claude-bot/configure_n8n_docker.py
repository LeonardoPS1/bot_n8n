#!/usr/bin/env python3
"""Configure n8n access via Docker internal network"""

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

print("[=== Configuring n8n Docker Access ===]\n")

# Find n8n container details
print("[1] Finding n8n container IP...")
stdin, stdout, stderr = client.exec_command("sudo docker inspect n8n_n8n.1.qeull7cf7ced3evfa2nmbhq8r 2>/dev/null | grep -A 3 'IPAddress' | head -5")
print(stdout.read().decode())

# Get n8n container name
print("\n[2] Getting n8n container info...")
stdin, stdout, stderr = client.exec_command("sudo docker inspect n8n_n8n.1.qeull7cf7ced3evfa2nmbhq8r 2>/dev/null | grep -E '\"Name\"|\"IPAddress\"|\"NetworkMode\"' | head -20")
print(stdout.read().decode())

# Test access via Docker network
print("\n[3] Testing access to n8n via Docker network...")
stdin, stdout, stderr = client.exec_command("sudo docker run --rm --network container:n8n_n8n.1.qeull7cf7ced3evfa2nmbhq8r curlimages/curl:latest curl -s -m 5 http://localhost:5678/healthz 2>&1 || echo 'Failed'")
print(stdout.read().decode())

# Check Docker networks
print("\n[4] Available Docker networks...")
stdin, stdout, stderr = client.exec_command("sudo docker network ls")
print(stdout.read().decode())

# Get the network n8n is on
print("\n[5] n8n container network details...")
stdin, stdout, stderr = client.exec_command("sudo docker inspect n8n_n8n.1.qeull7cf7ced3evfa2nmbhq8r 2>/dev/null | grep -A 10 'Networks'")
print(stdout.read().decode())

client.close()
