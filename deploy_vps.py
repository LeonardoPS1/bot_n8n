#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claudio Bot - Deploy to VPS using SSH
Direct deployment with password authentication
"""

import os
import sys

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

VPS_HOST = "51.222.207.250"
VPS_USER = "ubuntu"
VPS_PASS = "Cool220479..@"
PROJECT_DIR = "/opt/claudio-bot"

def deploy_with_paramiko():
    """Deploy using paramiko library"""
    try:
        import paramiko
        from pathlib import Path

        print("=" * 50)
        print("  Claudio Bot - Deploy to VPS")
        print("=" * 50)
        print(f"VPS: {VPS_HOST}")
        print(f"User: {VPS_USER}")
        print(f"Directory: {PROJECT_DIR}")
        print()

        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print("[Step 1/4] Connecting to VPS...")
        try:
            client.connect(
                hostname=VPS_HOST,
                username=VPS_USER,
                password=VPS_PASS,
                timeout=30
            )
            print("[OK] Connected")
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            print()
            print("Possible causes:")
            print("  - Wrong password")
            print("  - SSH not enabled on VPS")
            print("  - Network/firewall issues")
            return False

        # Files to deploy
        files_to_deploy = [
            "claudio_complete.py",
            "bot_v2.py"
        ]

        # Use SFTP to transfer files
        print()
        print("[Step 2/4] Transferring files...")

        sftp = client.open_sftp()

        for filename in files_to_deploy:
            local_path = Path(__file__).parent / filename
            if not local_path.exists():
                print(f"[SKIP] {filename} not found locally")
                continue

            print(f"  -> {filename}")

            # Upload to /tmp first
            remote_tmp = f"/tmp/{filename}"
            sftp.put(str(local_path), remote_tmp)

            # Move to final location with proper permissions
            stdin, stdout, stderr = client.exec_command(
                f"sudo cp {remote_tmp} {PROJECT_DIR}/ && "
                f"sudo chown claudio:claudio {PROJECT_DIR}/{filename} && "
                f"echo '[OK] {filename} installed'"
            )
            result = stdout.read().decode().strip()
            print(f"     {result}")

        sftp.close()

        print()
        print("[Step 3/4] Restarting services...")

        stdin, stdout, stderr = client.exec_command(
            f"sudo systemctl restart claudio-server claudio-telegram-bot && "
            f"echo '[OK] Services restarted'"
        )
        result = stdout.read().decode().strip()
        print(result)

        # Check status
        stdin, stdout, stderr = client.exec_command(
            f"sudo systemctl status claudio-server --no-pager | head -5"
        )
        result = stdout.read().decode().strip()
        print(result)

        print()
        print("[Step 4/4] Verifying deployment...")

        stdin, stdout, stderr = client.exec_command(
            f"sudo journalctl -u claudio-server -n 3 --no-pager"
        )
        result = stdout.read().decode().strip()
        print(result)

        client.close()

        print()
        print("=" * 50)
        print("  DEPLOYMENT COMPLETE!")
        print("=" * 50)
        print()
        print("What's new:")
        print("  - Dynamic model switching without restart")
        print("  - Auto-fallback when models fail")
        print("  - /switch command in Telegram")
        print()
        print("Next steps:")
        print("  1. Edit .env: sudo nano " + PROJECT_DIR + "/.env")
        print("  2. Set: AI_PROVIDER=multi")
        print("  3. Set: ALLOWED_ADMIN_USERS=your_telegram_id")
        print("  4. Restart: sudo systemctl restart claudio-server")
        print()
        print("Telegram commands:")
        print("  /status - Check current model")
        print("  /switch <provider> - Change model dynamically")
        print("  /models - List all available models")
        print("  /admin - Show admin help")
        print()
        print("Monitor logs:")
        print(f"  ssh {VPS_USER}@{VPS_HOST}")
        print(f"  sudo journalctl -u claudio-telegram-bot -f")
        print()

        return True

    except ImportError:
        print("[ERROR] paramiko not installed")
        print()
        print("Install with: pip install paramiko")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False


def manual_instructions():
    """Print manual deployment instructions"""
    print()
    print("=" * 50)
    print("  MANUAL DEPLOYMENT INSTRUCTIONS")
    print("=" * 50)
    print()
    print("Since automatic deployment failed, here are manual steps:")
    print()
    print("1. Download a SSH client:")
    print("   - Windows: PuTTY (https://www.putty.org/)")
    print("   - Or install: winget install PuTTY.PuTTY")
    print()
    print("2. Connect to VPS:")
    print(f"   Host: {VPS_HOST}")
    print(f"   User: {VPS_USER}")
    print(f"   Pass: {VPS_PASS}")
    print()
    print("3. Copy files (from local machine to VPS):")
    print("   Use SCP or SFTP to transfer:")
    print("   - claudio_complete.py")
    print("   - bot_v2.py")
    print()
    print("4. On VPS, install files:")
    print(f"   sudo cp claudio_complete.py {PROJECT_DIR}/")
    print(f"   sudo cp bot_v2.py {PROJECT_DIR}/")
    print(f"   sudo chown claudio:claudio {PROJECT_DIR}/*.py")
    print()
    print("5. Restart services:")
    print("   sudo systemctl restart claudio-server claudio-telegram-bot")
    print()
    print("6. Check logs:")
    print("   sudo journalctl -u claudio-telegram-bot -f")
    print()


if __name__ == "__main__":
    success = deploy_with_paramiko()
    if not success:
        manual_instructions()
