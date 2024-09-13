# scheduler.py

import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from workflow_manager import WorkflowManager, Workflow, Task
from utils import wait_for_file
from rich.console import Console
from rich.table import Table
from rich import box

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='scheduler.log'
)
logger = logging.getLogger(__name__)

console = Console()
workflow_manager = WorkflowManager()

# Load environment variables
load_dotenv()

def job_listener(event):
    if event.exception:
        logger.error(f"Job {event.job_id} raised an exception: {event.exception}")
    else:
        logger.info(f"Job {event.job_id} executed successfully")

def scheduled_workflow_job(workflow_id: str):
    workflow_manager.execute_workflow(workflow_id)

def create_scheduler():
    jobstores = {
        'default': SQLAlchemyJobStore(url=os.getenv('DB_URL', 'sqlite:///jobs.sqlite'))
    }
    executors = {
        'default': ThreadPoolExecutor(int(os.getenv('MAX_THREADS', 10))),
        'processpool': ProcessPoolExecutor(int(os.getenv('MAX_PROCESSES', 5)))
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 60
    }
    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=os.getenv('TIMEZONE', 'UTC')
    )
    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    return scheduler

scheduler = create_scheduler()

def print_workflows():
    if not workflow_manager.workflows:
        console.print("No workflows available.", style="yellow")
    else:
        table = Table(title="Workflows", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Number of Tasks", style="magenta")
        for workflow_id, workflow in workflow_manager.workflows.items():
            table.add_row(
                workflow_id,
                str(len(workflow.tasks))
            )
        console.print(table)

def create_workflow():
    console.print("\nCreating a new workflow", style="bold green")
    workflow_id = console.input("[bold cyan]Enter a unique workflow ID: [/bold cyan]").strip()
    if workflow_id in workflow_manager.workflows:
        console.print(f"Workflow '{workflow_id}' already exists.", style="bold red")
        return
    workflow = Workflow(id=workflow_id)
    workflow_manager.add_workflow(workflow)
    console.print(f"Workflow '{workflow_id}' created successfully.", style="bold green")

def add_task_to_workflow():
    console.print("\nAdding a task to a workflow", style="bold green")
    workflow_id = console.input("[bold cyan]Enter the workflow ID: [/bold cyan]").strip()
    workflow = workflow_manager.get_workflow(workflow_id)
    if not workflow:
        console.print(f"Workflow '{workflow_id}' not found.", style="bold red")
        return
    task_id = console.input("[bold cyan]Enter a unique task ID: [/bold cyan]").strip()
    command = console.input("[bold cyan]Enter the command or script to execute: [/bold cyan]").strip()
    args_input = console.input("[bold cyan]Enter arguments for the command (separated by spaces): [/bold cyan]").strip()
    args = args_input.split() if args_input else []
    exit_codes_input = console.input("[bold cyan]Enter expected exit codes (e.g., 0 1): [/bold cyan]").strip()
    expected_exit_codes = [int(code) for code in exit_codes_input.split()] if exit_codes_input else [0]
    output_files_input = console.input("[bold cyan]Enter output file paths to monitor (separated by commas): [/bold cyan]").strip()
    output_files = [path.strip() for path in output_files_input.split(',')] if output_files_input else []
    retry_count = int(console.input("[bold cyan]Enter the number of retries (default 0): [/bold cyan]").strip() or 0)
    retry_delay = int(console.input("[bold cyan]Enter retry delay in seconds (default 0): [/bold cyan]").strip() or 0)
    continue_on_failure_input = console.input("[bold cyan]Continue workflow on failure? (yes/no): [/bold cyan]").strip().lower()
    continue_on_failure = continue_on_failure_input == 'yes'
    task = Task(
        id=task_id,
        command=command,
        args=args,
        expected_exit_codes=expected_exit_codes,
        output_files=output_files,
        retry_count=retry_count,
        retry_delay=retry_delay,
        continue_on_failure=continue_on_failure
    )
    workflow.add_task(task)
    console.print(f"Task '{task_id}' added to workflow '{workflow_id}'.", style="bold green")

def schedule_workflow():
    console.print("\nScheduling a workflow", style="bold green")
    workflow_id = console.input("[bold cyan]Enter the workflow ID to schedule: [/bold cyan]").strip()
    workflow = workflow_manager.get_workflow(workflow_id)
    if not workflow:
        console.print(f"Workflow '{workflow_id}' not found.", style="bold red")
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
        run_date_input = console.input("[bold cyan]Enter date and time (YYYY-MM-DD HH:MM:SS): [/bold cyan]").strip()
        run_date = datetime.strptime(run_date_input, "%Y-%m-%d %H:%M:%S")
        trigger = {'type': 'date', 'run_date': run_date}
    else:
        console.print("Invalid trigger type. Please choose 'interval', 'cron', or 'date'.", style="bold red")
        return
    job_id = f"workflow_{workflow_id}"
    try:
        scheduler.add_job(
            func=scheduled_workflow_job,
            trigger=trigger,
            args=[workflow_id],
            id=job_id,
            name=f"Workflow {workflow_id}"
        )
        console.print(f"Workflow '{workflow_id}' scheduled successfully.", style="bold green")
    except Exception as e:
        console.print(f"Error scheduling workflow: {str(e)}", style="bold red")

def start_scheduler():
    scheduler.start()
    console.print("Scheduler started.", style="bold green")

def stop_scheduler():
    scheduler.shutdown()
    console.print("Scheduler stopped.", style="bold red")

def list_scheduled_jobs():
    jobs = scheduler.get_jobs()
    if not jobs:
        console.print("No workflows scheduled.", style="yellow")
    else:
        table = Table(title="Scheduled Workflows", box=box.ROUNDED)
        table.add_column("Job ID", style="cyan")
        table.add_column("Workflow ID", style="magenta")
        table.add_column("Trigger", style="blue")
        table.add_column("Next Run Time", style="yellow")
        for job in jobs:
            table.add_row(
                job.id,
                job.args[0],
                str(job.trigger),
                str(job.next_run_time)
            )
        console.print(table)

def main_menu():
    console.print("Welcome to the Workflow Scheduler CLI", style="bold magenta")
    while True:
        console.print("\nMenu:", style="bold cyan")
        console.print("1. List workflows")
        console.print("2. Create workflow")
        console.print("3. Add task to workflow")
        console.print("4. Schedule workflow")
        console.print("5. List scheduled workflows")
        console.print("6. Start scheduler")
        console.print("7. Stop scheduler")
        console.print("8. Quit")
        choice = console.input("[bold cyan]Enter your choice (1-8): [/bold cyan]").strip()
        if choice == '1':
            print_workflows()
        elif choice == '2':
            create_workflow()
        elif choice == '3':
            add_task_to_workflow()
        elif choice == '4':
            schedule_workflow()
        elif choice == '5':
            list_scheduled_jobs()
        elif choice == '6':
            start_scheduler()
        elif choice == '7':
            stop_scheduler()
        elif choice == '8':
            if scheduler.running:
                scheduler.shutdown()
            console.print("Exiting Workflow Scheduler CLI. Goodbye!", style="bold magenta")
            sys.exit(0)
        else:
            console.print("Invalid choice. Please enter a number between 1 and 8.", style="bold red")

if __name__ == '__main__':
    try:
        main_menu()
    except (KeyboardInterrupt, SystemExit):
        if scheduler.running:
            scheduler.shutdown()
        console.print("\nScheduler stopped due to interruption. Goodbye!", style="bold red")
