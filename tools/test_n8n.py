import paramiko
import json

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('51.222.207.250', username='ubuntu', password='Cool220479..@', timeout=10)
    
    stdin, stdout, stderr = client.exec_command('grep N8N_API_KEY /opt/claudio-bot/.env')
    api_key_line = stdout.read().decode().strip()
    api_key = api_key_line.split('=', 1)[1].strip() if '=' in api_key_line else ''
    
    cmd = f'curl -s -X GET https://n8n.aicorebots.com/api/v1/workflows -H "X-N8N-API-KEY: {api_key}" -H "Content-Type: application/json"'
    stdin, stdout, stderr = client.exec_command(cmd)
    result = stdout.read().decode('utf-8', 'ignore')
    
    try:
        data = json.loads(result)
        workflows = data.get('data', data)
        if isinstance(workflows, list):
            print(f'Workflow count: {len(workflows)}')
            for i, w in enumerate(workflows):
                print(f'  {i+1}: {w.get("name", "Unknown")}')
        else:
            print('Returned object is not a list:')
            print(str(data)[:200])
    except Exception as e:
        print('JSON parsing error:', e)
        print('Raw result:', result[:200])
        
    client.close()
except Exception as e:
    print('Error:', e)
