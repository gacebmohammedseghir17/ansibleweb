import os
from crontab import CronTab
from datetime import datetime
import subprocess

class CronManager:
    def __init__(self):
        # Initialize system crontab for the current user
        self.crontab = CronTab(user=True)
        self.job_log_dir = '/var/log/ansible-web/cron'
        os.makedirs(self.job_log_dir, exist_ok=True)

    def run_playbook(self, playbook_name, target_servers):
        playbook_path = f'/etc/ansible/playbooks/{playbook_name}'
        if not os.path.exists(playbook_path):
            raise FileNotFoundError(f"Playbook {playbook_name} not found")

        # Create command for ansible-playbook execution
        command = [
            '/usr/bin/ansible-playbook',
            playbook_path,
            '-i', '/etc/ansible/inventory/hosts.yml',
            '-l', ','.join(target_servers),
            '-vvv',
            '--become'
        ]

        # Set environment variables
        env = os.environ.copy()
        env['ANSIBLE_CONFIG'] = '/etc/ansible/ansible.cfg'

        # Create a log file for this execution
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.job_log_dir, f'{playbook_name}_{timestamp}.log')

        # Redirect output to log file
        with open(log_file, 'w') as f:
            try:
                result = subprocess.run(command, env=env, stdout=f, stderr=subprocess.STDOUT, text=True)
                return {'success': result.returncode == 0, 'log_file': log_file}
            except subprocess.SubprocessError as e:
                f.write(f'Failed to execute playbook: {str(e)}\n')
                return {'success': False, 'log_file': log_file}

    def schedule_playbook(self, playbook_name, target_servers, schedule_type, schedule_params):
        job_id = f"{playbook_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create the job command
        job_script = os.path.join(self.job_log_dir, f'{job_id}.sh')
        with open(job_script, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write(f'export ANSIBLE_CONFIG=/etc/ansible/ansible.cfg\n')
            f.write(f'/usr/bin/ansible-playbook \
')
            f.write(f'    /etc/ansible/playbooks/{playbook_name} \
')
            f.write(f'    -i /etc/ansible/inventory/hosts.yml \
')
            f.write(f'    -l {",".join(target_servers)} \
')
            f.write(f'    -vvv \
')
            f.write(f'    --become')
        
        # Make the script executable
        os.chmod(job_script, 0o755)
        
        # Create new cron job
        job = self.crontab.new(command=job_script)

        if schedule_type == 'once':
            run_date = schedule_params.get('datetime')
            if not run_date:
                raise ValueError("Datetime is required for one-time scheduling")
            
            if isinstance(run_date, str):
                run_date = datetime.strptime(run_date, '%Y-%m-%d %H:%M:%S')
            
            job.setall(run_date.minute, run_date.hour, run_date.day, run_date.month, '*')
        
        elif schedule_type == 'recurring':
            frequency = schedule_params.get('frequency')
            time = schedule_params.get('time')
            if not frequency or not time:
                raise ValueError("Frequency and time are required for recurring scheduling")

            hour, minute = time.split(':')
            
            if frequency == 'daily':
                job.setall(minute, hour, '*', '*', '*')
            elif frequency == 'weekly':
                job.setall(minute, hour, '*', '*', '0')
            elif frequency == 'monthly':
                job.setall(minute, hour, '1', '*', '*')
            else:
                raise ValueError(f"Unsupported frequency: {frequency}")

        # Save the job with a comment for identification
        job.set_comment(job_id)
        self.crontab.write()
        
        return job_id

    def get_scheduled_jobs(self):
        jobs = []
        for job in self.crontab:
            if job.comment:
                jobs.append({
                    'id': job.comment,
                    'schedule': str(job.slices),
                    'command': job.command
                })
        return jobs

    def remove_job(self, job_id):
        for job in self.crontab:
            if job.comment == job_id:
                self.crontab.remove(job)
                # Remove the associated script file
                script_file = os.path.join(self.job_log_dir, f'{job_id}.sh')
                if os.path.exists(script_file):
                    os.remove(script_file)
                self.crontab.write()
                return True
        return False

# Initialize the cron manager
cron_manager = CronManager()