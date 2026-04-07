#!/usr/bin/env python3
"""
Setup n8n-MCP server on VPS
This installs n8n-mcp-server and configures it for use
"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASSWORD = "Cool220479..@"

def setup_mcp():
    try:
        print("[+] Connecting to VPS...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=VPS_HOST,
            username=VPS_USER,
            password=VPS_PASSWORD,
            timeout=30
        )
        print("[+] Connected!")

        # Commands to setup n8n-mcp-server
        commands = [
            # Install Node.js if not present (n8n-mcp-server requires npm)
            "which node || (curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs)",

            # Install n8n-mcp-server globally
            "sudo npm install -g @n8n/n8n-mcp-server || npm install -g @n8n/n8n-mcp-server",

            # Verify installation
            "which n8n-mcp-server || echo 'n8n-mcp-server not found in PATH'",
            "n8n-mcp-server --version || echo 'Version check failed'",
        ]

        for cmd in commands:
            print(f"\n[+] Running: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
            output = stdout.read().decode()
            error = stderr.read().decode()

            if output:
                print(f"    {output.strip()}")
            if error and "npm WARN" not in error and "Warning" not in error:
                print(f"    [!] {error.strip()}")

        # Create MCP configuration directory
        print("\n[+] Creating MCP configuration...")
        commands = [
            "mkdir -p ~/.config/claude",
            "mkdir -p /opt/claudio-bot/mcp"
        ]
        for cmd in commands:
            stdin, stdout, stderr = client.exec_command(cmd)
            stdout.read()

        print("\n[+] MCP setup complete!")
        print("[!] Note: n8n-mcp-server requires proper configuration")
        print("[!] We'll use Python-based MCP client for better integration")

        client.close()
        return True

    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_mcp()
