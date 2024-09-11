import logging
from typing import Any, Callable, Dict, List, Union
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

def print_jobs(jobs: List[Dict[str, Any]]):
    if not jobs:
        print("No tasks scheduled.")
    else:
        print("\nScheduled Tasks:")
        print("{:<20} {:<20} {:<30} {:<30}".format("ID", "Name", "Trigger", "Next Run Time"))
        print("-" * 100)
        for job in jobs:
            print("{:<20} {:<20} {:<30} {:<30}".format(
                job['id'],
                job['name'] or "N/A",
                str(job['trigger']),
                str(job['next_run_time']) if job['next_run_time'] else "N/A"
            ))
        print()

def add_task(scheduler: EnhancedAPScheduler):
    print("\nAdding a new task to the scheduler")
    
    task_type = input("Enter task type (python_task or cli_command): ").strip()
    task_id = input("Enter a unique task ID: ").strip()
    
    if task_type == "python_task":
        arg1 = input("Enter first argument for the task: ").strip()
        arg2 = input("Enter second argument for the task: ").strip()
        task_func = EnhancedAPScheduler.python_task_example
        task_args = [arg1, arg2]
    elif task_type == "cli_command":
        command = input("Enter the CLI command to execute: ").strip()
        task_func = EnhancedAPScheduler.cli_command_task
        task_args = [command]
    else:
        print("Invalid task type. Please choose 'python_task' or 'cli_command'.")
        return

    trigger_type = input("Enter trigger type (interval, cron, or date): ").strip()
    
    if trigger_type == "interval":
        minutes = int(input("Enter interval in minutes: ").strip())
        trigger = {'type': 'interval', 'minutes': minutes}
    elif trigger_type == "cron":
        day_of_week = input("Enter day of week (mon-fri, mon, tue, etc.): ").strip()
        hour = int(input("Enter hour (0-23): ").strip())
        minute = int(input("Enter minute (0-59): ").strip())
        trigger = {'type': 'cron', 'day_of_week': day_of_week, 'hour': hour, 'minute': minute}
    elif trigger_type == "date":
        run_date = input("Enter date and time (YYYY-MM-DD HH:MM:SS): ").strip()
        trigger = {'type': 'date', 'run_date': run_date}
    else:
        print("Invalid trigger type. Please choose 'interval', 'cron', or 'date'.")
        return

    try:
        scheduler.add_job(task_func, trigger, args=task_args, id=task_id)
        print(f"Task '{task_id}' added successfully!")
    except Exception as e:
        print(f"Error adding task: {str(e)}")

def remove_task(scheduler: EnhancedAPScheduler):
    job_id = input("Enter the ID of the task to remove: ").strip()
    try:
        scheduler.remove_job(job_id)
        print(f"Task '{job_id}' removed successfully!")
    except Exception as e:
        print(f"Error removing task: {str(e)}")

def pause_task(scheduler: EnhancedAPScheduler):
    job_id = input("Enter the ID of the task to pause: ").strip()
    try:
        scheduler.pause_job(job_id)
        print(f"Task '{job_id}' paused successfully!")
    except Exception as e:
        print(f"Error pausing task: {str(e)}")

def resume_task(scheduler: EnhancedAPScheduler):
    job_id = input("Enter the ID of the task to resume: ").strip()
    try:
        scheduler.resume_job(job_id)
        print(f"Task '{job_id}' resumed successfully!")
    except Exception as e:
        print(f"Error resuming task: {str(e)}")

def main():
    config = {
        'db_url': os.getenv('DB_URL', 'sqlite:///jobs.sqlite'),
        'max_threads': int(os.getenv('MAX_THREADS', 10)),
        'max_processes': int(os.getenv('MAX_PROCESSES', 5)),
        'timezone': os.getenv('TIMEZONE', 'UTC')
    }

    scheduler = EnhancedAPScheduler(config)
    scheduler.scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    scheduler.start()
    print("Scheduler started. Use the menu options to manage tasks.")

    while True:
        print("\nMenu:")
        print("1. List tasks")
        print("2. Add task")
        print("3. Remove task")
        print("4. Pause task")
        print("5. Resume task")
        print("6. Quit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == '1':
            print_jobs(scheduler.get_jobs())
        elif choice == '2':
            add_task(scheduler)
        elif choice == '3':
            remove_task(scheduler)
        elif choice == '4':
            pause_task(scheduler)
        elif choice == '5':
            resume_task(scheduler)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

    scheduler.shutdown()
    print("Scheduler shut down.")

if __name__ == '__main__':
    main()