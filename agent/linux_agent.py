#!/usr/bin/env python3
import os
import socket
import json
import psutil
import platform
import time
from threading import Thread
import re

# Configuration
AGENT_HOST = "localhost"  # Changed from 172.16.17.10 to work on any machine
AGENT_PORT = 9090  # Port to listen for backend queries
AUTH_TOKEN = os.environ.get('AGENT_AUTH_TOKEN', 'changeme')  # Simple token-based auth

# Collect system and network metrics
def collect_metrics():
    metrics = {
        'name': platform.node(),
        'ip': AGENT_HOST,
        'type': platform.system().lower(),
        'os': platform.platform(),
        'uptime': time.time() - psutil.boot_time(),
        'cpu_percent': psutil.cpu_percent(interval=0.5),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('C:\\' if platform.system() == 'Windows' else '/')._asdict(),
        'net_io': psutil.net_io_counters()._asdict(),
        'timestamp': time.time()
    }
    return metrics

def parse_lql(query):
    # Very basic LQL parser for GET metrics\nColumns: ...
    lines = query.strip().split('\n')
    if not lines or not lines[0].startswith('GET'):
        return None, None
    table = lines[0][4:].strip()
    columns = None
    for line in lines[1:]:
        if line.startswith('Columns:'):
            columns = [col.strip() for col in line[8:].strip().split(',')]
    return table, columns

def handle_client(conn):
    try:
        data = b''
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            data += chunk
            if b'\n\n' in data or len(chunk) < 4096:
                break
        text = data.decode(errors='ignore').strip()
        # Optional: check for token in a header line
        auth_match = re.search(r'^Auth:\s*(\S+)', text, re.MULTILINE)
        if auth_match:
            token = auth_match.group(1)
            if token != AUTH_TOKEN:
                conn.sendall(json.dumps({'status': 'error', 'error': 'Unauthorized'}).encode())
                return
        else:
            # For backward compatibility, allow JSON auth
            try:
                req = json.loads(text)
                if req.get('auth') != AUTH_TOKEN:
                    conn.sendall(json.dumps({'status': 'error', 'error': 'Unauthorized'}).encode())
                    return
                if req.get('action') == 'get_metrics':
                    metrics = collect_metrics()
                    # Always include required fields
                    for field in ['name', 'ip', 'type']:
                        if field not in metrics:
                            metrics[field] = ''
                    conn.sendall(json.dumps({'status': 'ok', 'metrics': metrics}).encode())
                    return
            except Exception:
                pass
        # LQL-like protocol
        table, columns = parse_lql(text)
        if table == 'metrics':
            metrics = collect_metrics()
            if columns:
                filtered = {k: metrics[k] for k in columns if k in metrics}
                # Ensure required fields are present
                for field in ['name', 'ip', 'type']:
                    if field not in filtered and field in metrics:
                        filtered[field] = metrics[field]
            else:
                filtered = metrics
                for field in ['name', 'ip', 'type']:
                    if field not in filtered:
                        filtered[field] = ''
            conn.sendall(json.dumps({'status': 'ok', 'metrics': filtered}).encode())
        else:
            conn.sendall(json.dumps({'status': 'error', 'error': 'Unknown action or table'}).encode())
    except Exception as e:
        conn.sendall(json.dumps({'error': str(e)}).encode())
    finally:
        conn.close()

def start_agent():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((AGENT_HOST, AGENT_PORT))
    s.listen(5)
    print(f"Linux Agent running on {AGENT_HOST}:{AGENT_PORT}")
    while True:
        conn, addr = s.accept()
        Thread(target=handle_client, args=(conn,)).start()

if __name__ == '__main__':
    start_agent()
