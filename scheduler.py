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
from datetime import datetime, timedelta
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import box

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)
logger = logging.getLogger(__name__)

console = Console()

class EnhancedAPScheduler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scheduler = self._create_scheduler()
        self.is_running = False
        self.jobs = []  # Store jobs here when scheduler is stopped
        self.job_status = {}  # Store job status (pass/fail) and last run time

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
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            # Restore jobs if any
            for job in self.jobs:
                self.scheduler.add_job(**job)
            self.jobs = []  # Clear the temporary storage
            logger.info("Scheduler started.")
            console.print("Scheduler started.", style="bold green")
        else:
            console.print("Scheduler is already running.", style="yellow")

    def stop(self):
        if self.is_running:
            # Store current jobs before shutting down
            self.jobs = [
                {
                    'func': job.func,
                    'trigger': job.trigger,
                    'id': job.id,
                    'name': job.name,
                    'args': job.args,
                    'kwargs': job.kwargs
                }
                for job in self.scheduler.get_jobs()
            ]
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped.")
            console.print("Scheduler stopped.", style="bold red")
        else:
            console.print("Scheduler is not running.", style="yellow")

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
        
        job = self.scheduler.add_job(func, trigger, **kwargs)
        self.job_status[job.id] = {'status': 'Not run yet', 'last_run': None}
        return job

    def remove_job(self, job_id: str):
        self.scheduler.remove_job(job_id)
        if job_id in self.job_status:
            del self.job_status[job_id]

    def get_jobs(self) -> List[Dict[str, Any]]:
        if self.is_running:
            return [
                {
                    'id': job.id,
                    'name': job.name,
                    'trigger': str(job.trigger),
                    'next_run_time': job.next_run_time,
                    'status': self.job_status.get(job.id, {'status': 'Not run yet', 'last_run': None})
                }
                for job in self.scheduler.get_jobs()
            ]
        else:
            return [
                {
                    'id': job['id'],
                    'name': job['name'],
                    'trigger': str(job['trigger']),
                    'next_run_time': None,
                    'status': self.job_status.get(job['id'], {'status': 'Not run yet', 'last_run': None}),
                    'scheduler_status': 'Inactive (Scheduler Stopped)'
                }
                for job in self.jobs
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

    def update_job_status(self, job_id: str, status: str):
        self.job_status[job_id] = {'status': status, 'last_run': datetime.now()}

def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} raised an exception: {event.exception}")
        scheduler.update_job_status(event.job_id, 'Failed')
    else:
        logger.info(f"Job {event.job_id} executed successfully")
        scheduler.update_job_status(event.job_id, 'Passed')

def print_jobs(scheduler: EnhancedAPScheduler):
    jobs = scheduler.get_jobs()
    if not jobs:
        console.print("No tasks scheduled.", style="yellow")
    else:
        table = Table(title="Scheduled Tasks", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Trigger", style="blue")
        table.add_column("Next Run", style="yellow")
        table.add_column("Countdown", style="green")
        table.add_column("Last Run Status", style="bold")
        table.add_column("Scheduler Status", style="bold")

        now = datetime.now(scheduler.scheduler.timezone)
        for job in jobs:
            next_run = job['next_run_time']
            countdown = "N/A"
            if next_run:
                time_diff = next_run - now
                countdown = str(timedelta(seconds=int(time_diff.total_seconds())))

            status = job['status']['status']
            status_style = "green" if status == 'Passed' else "red" if status == 'Failed' else "yellow"

            if scheduler.is_running:
                scheduler_status = "Active" if next_run is not None else "Inactive"
                scheduler_status_style = "green" if next_run is not None else "grey70"
            else:
                scheduler_status = job.get('scheduler_status', 'Scheduler Stopped')
                scheduler_status_style = "red"
            
            table.add_row(
                job['id'],
                job['name'] or "N/A",
                str(job['trigger']),
                str(next_run) if next_run else "N/A",
                countdown,
                status,
                scheduler_status,
                style=scheduler_status_style
            )
        
        console.print(table)

def add_task(scheduler: EnhancedAPScheduler):
    console.print("\nAdding a new task to the scheduler", style="bold green")
    
    task_type = console.input("[bold cyan]Enter task type (python_task or cli_command): [/bold cyan]").strip()
    task_id = console.input("[bold cyan]Enter a unique task ID: [/bold cyan]").strip()
    
    if task_type == "python_task":
        arg1 = console.input("[bold cyan]Enter first argument for the task: [/bold cyan]").strip()
        arg2 = console.input("[bold cyan]Enter second argument for the task: [/bold cyan]").strip()
        task_func = EnhancedAPScheduler.python_task_example
        task_args = [arg1, arg2]
    elif task_type == "cli_command":
        command = console.input("[bold cyan]Enter the CLI command to execute: [/bold cyan]").strip()
        task_func = EnhancedAPScheduler.cli_command_task
        task_args = [command]
    else:
        console.print("Invalid task type. Please choose 'python_task' or 'cli_command'.", style="bold red")
        return

    trigger_type = console.input("[bold cyan]Enter trigger type (interval, cron, or date): [/bold cyan]").strip()
    
    if trigger_type == "interval":
        minutes = int(console.input("[bold cyan]Enter interval in minutes: [/bold cyan]").strip())
        trigger = {'type': 'interval', 'minutes': minutes}
    elif trigger_type == "cron":
        day_of_week = console.input("[bold cyan]Enter day of week (mon-fri, mon, tue, etc.): [/bold cyan]").strip()
        hour = int(console.input("[bold cyan]Enter hour (0-23): [/bold cyan]").strip())
        minute = int(console.input("[bold cyan]Enter minute (0-59): [/bold cyan]").strip())
        trigger = {'type': 'cron', 'day_of_week': day_of_week, 'hour': hour, 'minute': minute}
    elif trigger_type == "date":
        run_date = console.input("[bold cyan]Enter date and time (YYYY-MM-DD HH:MM:SS): [/bold cyan]").strip()
        trigger = {'type': 'date', 'run_date': run_date}
    else:
        console.print("Invalid trigger type. Please choose 'interval', 'cron', or 'date'.", style="bold red")
        return

    try:
        scheduler.add_job(task_func, trigger, args=task_args, id=task_id)
        console.print(f"Task '{task_id}' added successfully!", style="bold green")
    except Exception as e:
        console.print(f"Error adding task: {str(e)}", style="bold red")

def remove_task(scheduler: EnhancedAPScheduler):
    job_id = console.input("[bold cyan]Enter the ID of the task to remove: [/bold cyan]").strip()
    try:
        scheduler.remove_job(job_id)
        console.print(f"Task '{job_id}' removed successfully!", style="bold green")
    except Exception as e:
        console.print(f"Error removing task: {str(e)}", style="bold red")

def pause_task(scheduler: EnhancedAPScheduler):
    job_id = console.input("[bold cyan]Enter the ID of the task to pause: [/bold cyan]").strip()
    try:
        scheduler.pause_job(job_id)
        console.print(f"Task '{job_id}' paused successfully!", style="bold green")
    except Exception as e:
        console.print(f"Error pausing task: {str(e)}", style="bold red")

def resume_task(scheduler: EnhancedAPScheduler):
    job_id = console.input("[bold cyan]Enter the ID of the task to resume: [/bold cyan]").strip()
    try:
        scheduler.resume_job(job_id)
        console.print(f"Task '{job_id}' resumed successfully!", style="bold green")
    except Exception as e:
        console.print(f"Error resuming task: {str(e)}", style="bold red")

def main():
    config = {
        'db_url': os.getenv('DB_URL', 'sqlite:///jobs.sqlite'),
        'max_threads': int(os.getenv('MAX_THREADS', 10)),
        'max_processes': int(os.getenv('MAX_PROCESSES', 5)),
        'timezone': os.getenv('TIMEZONE', 'UTC')
    }

    global scheduler
    scheduler = EnhancedAPScheduler(config)
    scheduler.scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    console.print("Welcome to the Enhanced APScheduler CLI", style="bold magenta")

    while True:
        console.print("\nMenu:", style="bold cyan")
        console.print("1. List tasks")
        console.print("2. Add task")
        console.print("3. Remove task")
        console.print("4. Pause task")
        console.print("5. Resume task")
        console.print("6. Start scheduler")
        console.print("7. Stop scheduler")
        console.print("8. Quit")

        choice = console.input("[bold cyan]Enter your choice (1-8): [/bold cyan]").strip()

        if choice == '1':
            print_jobs(scheduler)
        elif choice == '2':
            add_task(scheduler)
        elif choice == '3':
            remove_task(scheduler)
        elif choice == '4':
            pause_task(scheduler)
        elif choice == '5':
            resume_task(scheduler)
        elif choice == '6':
            scheduler.start()
        elif choice == '7':
            scheduler.stop()
        elif choice == '8':
            if scheduler.is_running:
                scheduler.stop()
            break
        else:
            console.print("Invalid choice. Please enter a number between 1 and 8.", style="bold red")

    console.print("Thank you for using the Enhanced APScheduler CLI. Goodbye!", style="bold magenta")

if __name__ == '__main__':
    main()