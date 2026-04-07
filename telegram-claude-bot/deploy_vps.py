#!/usr/bin/env python3
"""
Deploy Claudio Server + Telegram Bot to VPS
Run: python deploy_vps.py
"""

import paramiko
import sys
import os

# Set UTF-8 encoding for Windows console
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
    "claudio_server.py",
    "bot_v2.py",
    "requirements.txt",
    ".env.example"
]

def run_commands(client, commands):
    """Run multiple commands on VPS"""
    for cmd in commands:
        print(f"[+] Running: {cmd}")
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"    {output.strip()}")
        if error and "Warning" not in error:
            print(f"    [!] {error.strip()}")

def upload_file(client, local_path, remote_path):
    """Upload file to VPS via SFTP"""
    try:
        sftp = client.open_sftp()
        print(f"[+] Uploading: {local_path} -> {remote_path}")
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"    [+] Upload complete")
        return True
    except Exception as e:
        print(f"    [-] Upload failed: {e}")
        return False

def deploy():
    try:
        print(f"[+] Connecting to {VPS_USER}@{VPS_HOST}...")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=VPS_HOST,
            username=VPS_USER,
            password=VPS_PASSWORD,
            timeout=30
        )
        print("[+] Connected successfully!")

        # Step 1: Prepare VPS
        print("\n[=== Step 1: Prepare VPS ===]")
        commands = [
            # Update system
            "sudo apt-get update",

            # Install dependencies
            "sudo apt-get install -y python3 python3-pip python3-venv git",

            # Create service user
            f"sudo useradd -m -s /bin/bash {SERVICE_USER} || true",

            # Create app directory
            f"sudo mkdir -p {APP_DIR}",
            f"sudo chown -R {SERVICE_USER}:{SERVICE_USER} {APP_DIR}",

            # Create log directory
            "sudo mkdir -p /var/log/claudio-bot",
            "sudo chown -R {SERVICE_USER}:{SERVICE_USER} /var/log/claudio-bot"
        ]
        run_commands(client, commands)

        # Step 2: Upload files
        print("\n[=== Step 2: Upload files ===]")
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # First upload to /tmp
        for filename in FILES_TO_UPLOAD:
            local_path = os.path.join(base_dir, filename)
            if os.path.exists(local_path):
                remote_tmp = f"/tmp/{filename}"
                if upload_file(client, local_path, remote_tmp):
                    # Move to final destination
                    run_commands(client, [
                        f"sudo mv {remote_tmp} {APP_DIR}/{filename}",
                        f"sudo chown {SERVICE_USER}:{SERVICE_USER} {APP_DIR}/{filename}"
                    ])

        # Step 3: Setup Python environment
        print("\n[=== Step 3: Setup Python environment ===]")
        run_commands(client, [
            f"cd {APP_DIR}",
            f"sudo -u {SERVICE_USER} python3 -m venv {APP_DIR}/venv",
            f"sudo -u {SERVICE_USER} {APP_DIR}/venv/bin/pip install -r {APP_DIR}/requirements.txt"
        ])

        # Step 4: Configure environment
        print("\n[=== Step 4: Configure environment ===]")
        run_commands(client, [
            f"cd {APP_DIR}",
            f"if [ ! -f {APP_DIR}/.env ]; then sudo cp {APP_DIR}/.env.example {APP_DIR}/.env; fi",
            f"sudo chown {SERVICE_USER}:{SERVICE_USER} {APP_DIR}/.env"
        ])

        # Step 5: Create systemd services
        print("\n[=== Step 5: Create systemd services ===]")

        # Claudio Server service
        cladio_server_service = f"""[Unit]
Description=Claudio Server (Claude with n8n-MCP)
After=network.target

[Service]
Type=simple
User={SERVICE_USER}
WorkingDirectory={APP_DIR}
EnvironmentFile={APP_DIR}/.env
ExecStart={APP_DIR}/venv/bin/python {APP_DIR}/claudio_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"""

        commands = [
            f"echo '{cladio_server_service}' | sudo tee /etc/systemd/system/claudio-server.service > /dev/null"
        ]
        run_commands(client, commands)

        # Telegram Bot service
        telegram_bot_service = f"""[Unit]
Description=Claudio Telegram Bot
After=network.target claudio-server.service

[Service]
Type=simple
User={SERVICE_USER}
WorkingDirectory={APP_DIR}
EnvironmentFile={APP_DIR}/.env
ExecStart={APP_DIR}/venv/bin/python {APP_DIR}/bot_v2.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"""

        commands = [
            f"echo '{telegram_bot_service}' | sudo tee /etc/systemd/system/claudio-telegram-bot.service > /dev/null",
            "sudo systemctl daemon-reload",
            "sudo systemctl enable claudio-server.service",
            "sudo systemctl enable claudio-telegram-bot.service"
        ]
        run_commands(client, commands)

        # Step 6: Start services
        print("\n[=== Step 6: Start services ===]")
        run_commands(client, [
            "sudo systemctl start claudio-server.service",
            "sleep 3",
            "sudo systemctl start claudio-telegram-bot.service"
        ])

        # Check status
        print("\n[=== Service Status ===]")
        run_commands(client, [
            "sudo systemctl status claudio-server.service --no-pager -l",
            "sudo systemctl status claudio-telegram-bot.service --no-pager -l"
        ])

        print("\n[+] Deployment complete!")
        print("\n[!] IMPORTANT: Edit the .env file with your API keys:")
        print(f"    ssh {VPS_USER}@{VPS_HOST} 'sudo nano {APP_DIR}/.env'")
        print("\n[!] Then restart services:")
        print("    sudo systemctl restart claudio-server claudio-telegram-bot")

        client.close()
        return True

    except Exception as e:
        print(f"[-] Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    deploy()
