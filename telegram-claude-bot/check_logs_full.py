#!/usr/bin/env python3
"""Check Claudio Server FULL logs"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASSWORD = "Cool220479..@"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=VPS_HOST, username=VPS_USER, password=VPS_PASSWORD)

print("[=== Claudio Server FULL Logs ===]")
stdin, stdout, stderr = client.exec_command("sudo journalctl -u claudio-server -n 50 --no-pager")
print(stdout.read().decode())

print("\n[=== Testing Python syntax ===]")
stdin, stdout, stderr = client.exec_command("cd /opt/claudio-bot && sudo -u claudio venv/bin/python -m py_compile claudio_server_full.py")
print(stdout.read().decode())
print(stderr.read().decode())

client.close()
