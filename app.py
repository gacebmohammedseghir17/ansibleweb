from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import subprocess
import os
import yaml
import time
from datetime import datetime
from user_management import login_manager, User, login_user, login_required, logout_user, current_user, role_required
from scheduler import playbook_scheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
login_manager.init_app(app)
login_manager.login_view = 'login'

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
@app.route('/health_check')
def health_check():
    try:
        # Check system services status using service command
        services = ['ansible', 'ssh']
        service_status = {}
        for service in services:
            try:
                status = subprocess.getoutput(f'service {service} status')
                service_status[service] = 'running' in status.lower()
            except:
                service_status[service] = False
        
        # Check disk space using df command
        disk_space = subprocess.getoutput('df -h /').split('\n')[1].split()
        disk_usage = int(disk_space[4].strip('%'))
        
        # Check memory usage using free command
        memory = subprocess.getoutput('free -m').split('\n')[1].split()
        memory_usage = round((int(memory[2]) / int(memory[1])) * 100, 2)
        
        return jsonify({
            'success': True,
            'services': service_status,
            'disk_usage': disk_usage,
            'memory_usage': memory_usage
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear_cache')
def clear_cache():
    try:
        # Clear system cache using sync and echo
        subprocess.run('sync', shell=True, check=True)
        subprocess.run('echo 3 > /proc/sys/vm/drop_caches', shell=True, check=True)
        
        # Clear application cache
        cache_dir = '/var/cache/ansible'
        if os.path.exists(cache_dir):
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                try:
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception as e:
                    print(f'Error while deleting {item_path}: {e}')
        
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return render_template('login.html', error='Please provide both username and password')
            
        user = User.get_by_username(username)
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        
        return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Cache for system status data
_system_status_cache = {
    'active_servers': 0,
    'recent_playbooks': 0,
    'pending_tasks': 0,
    'last_update': 0
}

def update_system_status():
    try:
        servers_status = subprocess.getoutput('ansible all -i /etc/ansible/inventory/hosts.yml -m ping -o')
        _system_status_cache['active_servers'] = servers_status.count('"ping": "pong"')
    except Exception:
        _system_status_cache['active_servers'] = 0

    try:
        playbooks_dir = '/etc/ansible/playbooks'
        playbooks_list = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
        _system_status_cache['recent_playbooks'] = len(playbooks_list)
    except Exception:
        _system_status_cache['recent_playbooks'] = 0

    try:
        log_file = '/etc/ansible/ansible.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                logs = file.read()
            _system_status_cache['pending_tasks'] = logs.upper().count('FAILED')
    except Exception:
        _system_status_cache['pending_tasks'] = 0

    _system_status_cache['last_update'] = time.time()

@app.route('/')
@login_required
def home():
    # Update cache if it's older than 5 minutes
    if time.time() - _system_status_cache['last_update'] > 300:
        update_system_status()

    return render_template('index.html',
                         active_servers=_system_status_cache['active_servers'],
                         recent_playbooks=_system_status_cache['recent_playbooks'],
                         pending_tasks=_system_status_cache['pending_tasks'])

# Playbooks Route
@app.route('/schedule')
@login_required
def schedule():
    playbooks_dir = '/etc/ansible/playbooks'
    playbooks_list = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
    servers = load_servers()
    return render_template('schedule.html', playbooks=playbooks_list, servers=servers)

@app.route('/api/schedule_playbook', methods=['POST'])
@login_required
@role_required('admin')
def schedule_playbook():
    try:
        playbook = request.form['playbook']
        servers = request.form.getlist('servers')
        schedule_type = request.form['schedule_type']
        
        schedule_params = {}
        if schedule_type == 'once':
            try:
                schedule_datetime = request.form['schedule_datetime']
                if not schedule_datetime:
                    return jsonify({'success': False, 'error': 'Datetime is required for one-time scheduling'})
                # Parse datetime from frontend format and convert to required format
                parsed_datetime = datetime.strptime(schedule_datetime, '%Y-%m-%dT%H:%M')
                schedule_params['datetime'] = parsed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                return jsonify({'success': False, 'error': 'Invalid datetime format. Please use YYYY-MM-DDTHH:MM format'})
        else:
            schedule_params['frequency'] = request.form['frequency']
            schedule_params['time'] = request.form['schedule_time']
        
        job_id = playbook_scheduler.schedule_playbook(playbook, servers, schedule_type, schedule_params)
        return jsonify({'success': True, 'job_id': job_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/scheduled_playbooks')
@login_required
def get_scheduled_playbooks():
    jobs = playbook_scheduler.get_scheduled_jobs()
    events = [{
        'id': job['id'],
        'title': job['args'][0],  # playbook name
        'start': job['next_run_time'],
        'allDay': False
    } for job in jobs]
    return jsonify(events)

@app.route('/docs')
@login_required
def docs():
    return render_template('docs.html')

@app.route('/playbooks')
@login_required
def playbooks():
    playbooks_dir = '/etc/ansible/playbooks'
    playbooks_list = [f for f in os.listdir(playbooks_dir) if f.endswith('.yml')]
    servers = load_servers()
    return render_template('playbooks.html', playbooks=playbooks_list, servers=servers)

@app.route('/create_playbook', methods=['POST'])
@login_required
@role_required('admin')
def create_playbook():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        tags = data.get('tags', '')

        if not name:
            return jsonify({'success': False, 'error': 'Playbook name is required'})

        playbooks_dir = '/etc/ansible/playbooks'
        if not os.path.exists(playbooks_dir):
            os.makedirs(playbooks_dir)

        playbook_path = os.path.join(playbooks_dir, name)
        if os.path.exists(playbook_path):
            return jsonify({'success': False, 'error': 'Playbook with this name already exists'})

        # Create a basic playbook structure
        playbook_content = [
            '---',
            '# ' + description if description else '',
            '# Tags: ' + tags if tags else '',
            '- name: ' + name.replace('.yml', '').replace('.yaml', ''),
            '  hosts: all',
            '  tasks:',
            '    - name: Example task',
            '      debug:',
            '        msg: "This is an example task"'
        ]

        with open(playbook_path, 'w') as f:
            f.write('\n'.join(line for line in playbook_content if line))

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Run Playbook Route - Fixed Execution
@app.route('/run_playbook', methods=['POST'])
@login_required
@role_required('admin')
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
@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'})

        # Configure LM Studio API endpoint
        lmstudio_url = 'http://localhost:1234/v1/chat/completions'
        
        # Prepare the chat message for LM Studio
        payload = {
            'messages': [
                {'role': 'system', 'content': 'You are an Ansible expert AI assistant. Help users with Ansible-related questions, playbook creation, and automation tasks.'},
                {'role': 'user', 'content': message}
            ],
            'temperature': 0.7,
            'max_tokens': 500
        }

        # Send request to LM Studio
        response = requests.post(lmstudio_url, json=payload)
        response.raise_for_status()
        
        # Extract the assistant's response
        result = response.json()
        bot_response = result['choices'][0]['message']['content']
        
        return jsonify({'success': True, 'response': bot_response})
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': 'Failed to connect to LM Studio. Please ensure it is running.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/logs')
@login_required
def logs():
    log_file = '/etc/ansible/ansible.log'
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            ansible_log_content = file.read()
    else:
        ansible_log_content = "Log file not found."

    # Parse log entries for structured display
    log_entries = []
    if ansible_log_content != "Log file not found.":
        for line in ansible_log_content.split('\n'):
            if line.strip():
                # Basic log parsing - can be enhanced based on actual log format
                try:
                    # Assuming format: timestamp source [level] message
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        timestamp, source, level, message = parts
                        level = level.strip('[]').lower()
                        log_entries.append({
                            'timestamp': timestamp,
                            'source': source,
                            'level': level,
                            'message': message
                        })
                except Exception:
                    # Fallback for lines that don't match expected format
                    log_entries.append({
                        'timestamp': '',
                        'source': 'system',
                        'level': 'info',
                        'message': line
                    })

    return render_template('logs.html', logs=log_entries, ansible_log_content=ansible_log_content)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
