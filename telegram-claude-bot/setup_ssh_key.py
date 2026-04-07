#!/usr/bin/env python3
"""
Setup SSH key on VPS using password authentication
Run: python setup_ssh_key.py
"""

import paramiko
import socket
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# VPS Configuration
VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASSWORD = "Cool220479..@"
SSH_PUB_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMrLxBOtWB03XdZyEfbojiLLV+d+/b+jNi3LMOSVYBN9 claude-bot"

def setup_ssh_key():
    try:
        print(f"[+] Connecting to {VPS_USER}@{VPS_HOST}...")

        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect with password
        client.connect(
            hostname=VPS_HOST,
            username=VPS_USER,
            password=VPS_PASSWORD,
            timeout=30
        )

        print("[+] Connected successfully!")

        # Commands to setup SSH key
        commands = [
            "mkdir -p ~/.ssh",
            "chmod 700 ~/.ssh",
            f"echo '{SSH_PUB_KEY}' >> ~/.ssh/authorized_keys",
            "chmod 600 ~/.ssh/authorized_keys",
            "cat ~/.ssh/authorized_keys"
        ]

        for cmd in commands:
            print(f"[+] Running: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                print(f"    {output.strip()}")
            if error:
                print(f"    [!] {error.strip()}")

        # Test SSH key connection
        print("\n[+] Testing SSH key connection...")
        client.close()

        # Try connecting with key only
        client_key = paramiko.SSHClient()
        client_key.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Try with private key
        try:
            import os
            key_path = os.path.expanduser("~/.ssh/claude_bot")
            if os.path.exists(key_path):
                key = paramiko.Ed25519Key.from_private_key_file(key_path)
                client_key.connect(
                    hostname=VPS_HOST,
                    username=VPS_USER,
                    pkey=key,
                    timeout=10
                )
                print("[+] SSH key connection successful!")
                client_key.close()
            else:
                print("[!] Private key not found at ~/.ssh/claude_bot")
        except Exception as e:
            print(f"[!] SSH key test failed: {e}")
            print("    You may need to use password for first connection")

        print("\n[+] SSH key setup complete!")
        return True

    except socket.timeout:
        print("[-] Connection timeout. Check if VPS is reachable.")
        return False
    except paramiko.AuthenticationException:
        print("[-] Authentication failed. Check username/password.")
        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

if __name__ == "__main__":
    # Check if paramiko is installed
    try:
        import paramiko
    except ImportError:
        print("[-] paramiko not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])
        import paramiko

    setup_ssh_key()
