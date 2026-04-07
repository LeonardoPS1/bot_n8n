#!/usr/bin/env python3
"""
Deploy Claudio Server FULL version to VPS
Replaces basic version with full n8n-MCP integration
"""

import paramiko
import sys
import os

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# VPS Configuration
VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASSWORD = "Cool220479..@"
APP_DIR = "/opt/claudio-bot"
SERVICE_USER = "claudio"

# Files to upload
FILES_TO_UPLOAD = [
    "claudio_server_full.py",
    "n8n_mcp_tools.py",
    "bot_v2.py",
    "requirements.txt",
    ".env.example"
]


def run_commands(client, commands):
    """Run multiple commands on VPS"""
    for cmd in commands:
        print(f"[+] {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"    {output.strip()}")
        if error and "Warning" not in error and "npm WARN" not in error:
            print(f"    [!] {error.strip()}")


def upload_file(client, local_path, remote_path):
    """Upload file to VPS via SFTP"""
    try:
        sftp = client.open_sftp()
        print(f"[+] Uploading: {os.path.basename(local_path)}")
        sftp.put(local_path, remote_path)
        sftp.close()
        return True
    except Exception as e:
        print(f"    [-] Upload failed: {e}")
        return False


def deploy():
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

        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Stop services
        print("\n[=== Stopping services ===]")
        run_commands(client, [
            "sudo systemctl stop claudio-telegram-bot.service",
            "sudo systemctl stop claudio-server.service"
        ])

        # Upload new files
        print("\n[=== Uploading FULL version ===]")
        for filename in FILES_TO_UPLOAD:
            local_path = os.path.join(base_dir, filename)
            if os.path.exists(local_path):
                remote_tmp = f"/tmp/{filename}"
                if upload_file(client, local_path, remote_tmp):
                    run_commands(client, [
                        f"sudo mv {remote_tmp} {APP_DIR}/{filename}",
                        f"sudo chown {SERVICE_USER}:{SERVICE_USER} {APP_DIR}/{filename}"
                    ])

        # Update systemd service to use full version
        print("\n[=== Updating systemd service ===]")
        cladio_server_service = f"""[Unit]
Description=Claudio Server FULL (Claude with n8n-MCP)
After=network.target

[Service]
Type=simple
User={SERVICE_USER}
WorkingDirectory={APP_DIR}
EnvironmentFile={APP_DIR}/.env
ExecStart={APP_DIR}/venv/bin/python {APP_DIR}/claudio_server_full.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"""

        run_commands(client, [
            f"echo '{cladio_server_service}' | sudo tee /etc/systemd/system/claudio-server.service > /dev/null",
            "sudo systemctl daemon-reload"
        ])

        # Start services
        print("\n[=== Starting services ===]")
        run_commands(client, [
            "sudo systemctl start claudio-server.service",
            "sleep 3",
            "sudo systemctl start claudio-telegram-bot.service"
        ])

        # Check status
        print("\n[=== Service Status ===]")
        stdin, stdout, stderr = client.exec_command(
            "sudo systemctl status claudio-server.service --no-pager | head -15"
        )
        print(stdout.read().decode())

        stdin, stdout, stderr = client.exec_command(
            "sudo systemctl status claudio-telegram-bot.service --no-pager | head -15"
        )
        print(stdout.read().decode())

        print("\n[+] FULL version deployed!")
        print("[!] Features now available:")
        print("    - Real n8n API access")
        print("    - Workflow search and creation")
        print("    - Node search (1396 nodes)")
        print("    - Template search (2709+ templates)")
        print("    - Workflow validation")
        print("    - Specialized skills")

        client.close()
        return True

    except Exception as e:
        print(f"[-] Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    deploy()
