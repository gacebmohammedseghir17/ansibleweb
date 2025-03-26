from flask import Flask, render_template, request
import subprocess
import os
import yaml

app = Flask(__name__)

# Load servers from hosts.yml
def load_servers():
    with open('/etc/ansible/inventory/hosts.yml') as file:
        data = yaml.safe_load(file)

    servers = []
    
    def extract_hosts(group):
        if 'hosts' in group:
            for host, details in group['hosts'].items():
                ip_address = details.get('ansible_host', 'Unknown')
                servers.append({"name": host, "ip": ip_address})
        if 'children' in group:
            for child in group['children'].values():
                extract_hosts(child)

    extract_hosts(data.get('all', {}))
    return servers

# Home Route
@app.route('/')
def home():
    try:
        servers_status = subprocess.getoutput('ansible all -i /etc/ansible/inventory/hosts.yml -m ping -o')
        active_servers = servers_status.count('"ping": "pong"')  # Count active servers
    except Exception:
        active_servers = 0

    playbooks_dir = '/etc/ansible/playbooks'
    try:
        playbooks_list = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
        recent_playbooks = len(playbooks_list)  
    except Exception:
        recent_playbooks = 0

    log_file = '/etc/ansible/ansible.log'
    pending_tasks = 0
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                logs = file.read()
            pending_tasks = logs.upper().count('FAILED')  
    except Exception:
        pending_tasks = 0

    return render_template('index.html', active_servers=active_servers, recent_playbooks=recent_playbooks, pending_tasks=pending_tasks)

# Playbooks Route
@app.route('/playbooks')
def playbooks():
    playbooks_dir = '/etc/ansible/playbooks'
    playbooks_list = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
    servers = load_servers()
    return render_template('playbooks.html', playbooks=playbooks_list, servers=servers)

# Run Playbook Route - Fixed Execution
@app.route('/run_playbook', methods=['POST'])
def run_playbook():
    playbook = request.form['playbook']
    server = request.form['server']
    playbook_path = f'/etc/ansible/playbooks/{playbook}'

    if os.path.exists(playbook_path):
        command = [
            'ansible-playbook', playbook_path,
            '-i', '/etc/ansible/inventory/hosts.yml',
            '-l', server, '-vvv'
        ]
        
        print(f"Executing: {' '.join(command)}")  # ✅ Debug print
        
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        success = result.returncode == 0
    else:
        output = f"Playbook '{playbook}' not found."
        success = False

    playbooks_dir = '/etc/ansible/playbooks'
    playbooks_list = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
    servers = load_servers()

    return render_template('playbooks.html', playbooks=playbooks_list, servers=servers, output=output, success=success)

# Logs Route
@app.route('/logs')
def logs():
    log_file = '/etc/ansible/ansible.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            log_content = file.read()
    else:
        log_content = "Log file not found."
    return render_template('logs.html', logs=log_content)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
