#!/usr/bin/env python3
"""Test Claudio Server FULL functionality"""

import paramiko
import sys
import json

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

print("[=== Testing Claudio Server FULL ===]")

# Test health endpoint
print("\n[1] Testing /health endpoint...")
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/health')
health_output = stdout.read().decode()
print(health_output)

# Test tools endpoint
print("\n[2] Testing /api/tools endpoint...")
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/api/tools')
tools_output = stdout.read().decode()
print(tools_output)

# Test skills endpoint
print("\n[3] Testing /api/skills endpoint...")
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/api/skills')
skills_output = stdout.read().decode()
print(skills_output)

# Test n8n nodes endpoint
print("\n[4] Testing /api/n8n/nodes endpoint...")
stdin, stdout, stderr = client.exec_command('curl -s "http://localhost:8000/api/n8n/nodes?query=slack"')
nodes_output = stdout.read().decode()
print(nodes_output)

# Test n8n templates endpoint
print("\n[5] Testing /api/n8n/templates endpoint...")
stdin, stdout, stderr = client.exec_command('curl -s "http://localhost:8000/api/n8n/templates?query=webhook"')
templates_output = stdout.read().decode()
print(templates_output)

# Test n8n workflows endpoint
print("\n[6] Testing /api/n8n/workflows endpoint...")
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/api/n8n/workflows')
workflows_output = stdout.read().decode()
print(workflows_output[:500] if len(workflows_output) > 500 else workflows_output)

print("\n[=== Tests Complete ===]")

client.close()
