import logging
from typing import Any, Callable, Dict, List, Optional, Union
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
import subprocess
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)
logger = logging.getLogger(__name__)

class EnhancedAPScheduler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scheduler = self._create_scheduler()

    def _create_scheduler(self) -> BackgroundScheduler:
        jobstores = {
            'default': SQLAlchemyJobStore(url=self.config.get('db_url', 'sqlite:///jobs.sqlite'))
        }
        executors = {
            'default': ThreadPoolExecutor(self.config.get('max_threads', 10)),
            'processpool': ProcessPoolExecutor(self.config.get('max_processes', 5))
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 60
        }
        return BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=self.config.get('timezone', 'UTC')
        )

    def start(self):
        self.scheduler.start()
        logger.info("Scheduler started.")

    def shutdown(self):
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown complete.")

    def add_job(self, func: Callable, trigger: Union[str, Dict[str, Any]], **kwargs):
        job_id = kwargs.get('id', None)
        if isinstance(trigger, dict):
            trigger_type = trigger.pop('type', 'cron')
            if trigger_type == 'cron':
                trigger = CronTrigger(**trigger)
            elif trigger_type == 'interval':
                trigger = IntervalTrigger(**trigger)
            elif trigger_type == 'date':
                trigger = DateTrigger(**trigger)
            else:
                raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        return self.scheduler.add_job(func, trigger, **kwargs)

    def remove_job(self, job_id: str):
        self.scheduler.remove_job(job_id)

    def get_jobs(self) -> List[Dict[str, Any]]:
        return [
            {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run_time': job.next_run_time
            }
            for job in self.scheduler.get_jobs()
        ]

    def pause_job(self, job_id: str):
        self.scheduler.pause_job(job_id)

    def resume_job(self, job_id: str):
        self.scheduler.resume_job(job_id)

    @staticmethod
    def python_task_example(arg1: str, arg2: str):
        logger.info(f"Running Python task with arguments: {arg1}, {arg2}")
        time.sleep(5)  # Simulate a time-consuming task
        logger.info("Python task completed.")

    @staticmethod
    def cli_command_task(command: str):
        logger.info(f"Executing CLI command: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            logger.info(f"Command output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error: {e.stderr}")

def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} raised an exception: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} executed successfully")

if __name__ == '__main__':
    config = {
        'db_url': os.getenv('DB_URL', 'sqlite:///jobs.sqlite'),
        'max_threads': int(os.getenv('MAX_THREADS', 10)),
        'max_processes': int(os.getenv('MAX_PROCESSES', 5)),
        'timezone': os.getenv('TIMEZONE', 'UTC')
    }

    scheduler = EnhancedAPScheduler(config)
    scheduler.scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Example job additions
    scheduler.add_job(
        EnhancedAPScheduler.python_task_example,
        {'type': 'interval', 'minutes': 1},
        args=['arg1_value', 'arg2_value'],
        id='python_task_example'
    )

    scheduler.add_job(
        EnhancedAPScheduler.cli_command_task,
        {'type': 'cron', 'day_of_week': 'mon-fri', 'hour': 9, 'minute': 30},
        args=['echo "Hello from CLI task!"'],
        id='cli_command_task'
    )

    try:
        scheduler.start()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()