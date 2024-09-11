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
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
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

def create_job_table(jobs: List[Dict[str, Any]]) -> Table:
    table = Table(title="Scheduled Tasks", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Trigger", style="green")
    table.add_column("Next Run Time", style="yellow")

    for job in jobs:
        table.add_row(
            job['id'],
            job['name'] or "N/A",
            str(job['trigger']),
            str(job['next_run_time']) if job['next_run_time'] else "N/A"
        )

    return table

def create_menu() -> Panel:
    menu_items = [
        "[a]dd task",
        "[r]emove task",
        "[p]ause task",
        "[c]ontinue task",
        "[q]uit"
    ]
    return Panel("\n".join(menu_items), title="Menu", border_style="bold")

def add_task(scheduler: EnhancedAPScheduler):
    console.print("Adding a new task to the scheduler", style="bold green")
    
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

def main():
    config = {
        'db_url': os.getenv('DB_URL', 'sqlite:///jobs.sqlite'),
        'max_threads': int(os.getenv('MAX_THREADS', 10)),
        'max_processes': int(os.getenv('MAX_PROCESSES', 5)),
        'timezone': os.getenv('TIMEZONE', 'UTC')
    }

    scheduler = EnhancedAPScheduler(config)
    scheduler.scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body"),
        Layout(name="footer")
    )

    layout["body"].split_row(
        Layout(name="jobs"),
        Layout(name="menu")
    )

    with Live(layout, refresh_per_second=1, screen=True):
        while True:
            jobs = scheduler.get_jobs()
            layout["header"].update(Panel("APScheduler Task Manager", style="bold magenta"))
            layout["jobs"].update(create_job_table(jobs))
            layout["menu"].update(create_menu())
            layout["footer"].update(Panel("Press 'q' to quit", border_style="bold"))

            choice = console.input("Enter your choice: ").strip().lower()
            if choice == 'a':
                add_task(scheduler)
            elif choice == 'r':
                job_id = console.input("Enter the ID of the task to remove: ").strip()
                try:
                    scheduler.remove_job(job_id)
                    console.print(f"Task '{job_id}' removed successfully!", style="bold green")
                except Exception as e:
                    console.print(f"Error removing task: {str(e)}", style="bold red")
            elif choice == 'p':
                job_id = console.input("Enter the ID of the task to pause: ").strip()
                try:
                    scheduler.pause_job(job_id)
                    console.print(f"Task '{job_id}' paused successfully!", style="bold green")
                except Exception as e:
                    console.print(f"Error pausing task: {str(e)}", style="bold red")
            elif choice == 'c':
                job_id = console.input("Enter the ID of the task to continue: ").strip()
                try:
                    scheduler.resume_job(job_id)
                    console.print(f"Task '{job_id}' resumed successfully!", style="bold green")
                except Exception as e:
                    console.print(f"Error resuming task: {str(e)}", style="bold red")
            elif choice == 'q':
                break

    scheduler.shutdown()
    console.print("Scheduler shut down.", style="bold yellow")

if __name__ == '__main__':
    main()