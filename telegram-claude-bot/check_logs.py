#!/usr/bin/env python3
"""Check bot logs on VPS"""

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

print("[=== Bot Logs ===]")
stdin, stdout, stderr = client.exec_command("sudo journalctl -u claudio-telegram-bot -n 30 --no-pager")
print(stdout.read().decode())

print("\n[=== Current .env file ===]")
stdin, stdout, stderr = client.exec_command("sudo cat /opt/claudio-bot/.env")
print(stdout.read().decode())

client.close()
