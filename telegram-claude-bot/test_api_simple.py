import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('51.222.207.250', username='ubuntu', password='Cool220479..@', timeout=10)

print('[1] Testing n8n API...')
stdin, stdout, stderr = client.exec_command("curl -s -H 'X-N8N-API-KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyY2I5MzM0Mi05YTY2LTQxZWYtODJhZi1kM2JlYjExZGViNGMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiMDMxODE0NjYtOTViMi00ZGM1LWFhMjctODlkNzdmM2M2ZDEyIiwiaWF0IjoxNzc1NTc3NTc1fQ.eDKwfVpsqrDUYFCaL8HbcjqgEq5N74ImwTi9RBGfKw4' http://10.11.0.4:5678/api/v1/workflows", timeout=15)
output = stdout.read().decode()
print(output[:500])

print('\n[2] Restarting services...')
stdin, stdout, stderr = client.exec_command('sudo systemctl restart claudio-server', timeout=15)
stdout.read()

stdin, stdout, stderr = client.exec_command('sudo systemctl restart claudio-telegram-bot', timeout=15)
stdout.read()

print('[3] Waiting for services to start...')
import time
time.sleep(5)

print('[4] Checking Claudio health...')
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/health', timeout=10)
print(stdout.read().decode())

client.close()
