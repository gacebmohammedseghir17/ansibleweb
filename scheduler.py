from datetime import datetime
from cron_manager import cron_manager

class PlaybookScheduler:
    def __init__(self):
        self.cron = cron_manager

    def run_playbook(self, playbook_name, target_servers):
        return self.cron.run_playbook(playbook_name, target_servers)

    def schedule_playbook(self, playbook_name, target_servers, schedule_type, schedule_params):
        return self.cron.schedule_playbook(playbook_name, target_servers, schedule_type, schedule_params)

    def get_scheduled_jobs(self):
        return self.cron.get_scheduled_jobs()

    def remove_job(self, job_id):
        return self.cron.remove_job(job_id)

# Initialize the scheduler
playbook_scheduler = PlaybookScheduler()