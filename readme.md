# APScheduler Implementation

This project provides an implementation of APScheduler, offering a robust and flexible foundation for scheduling and managing jobs in Python applications. It includes an interactive interface for adding and managing tasks.

## Features

- Encapsulated scheduler functionality in the `EnhancedAPScheduler` class
- Flexible job addition with support for cron, interval, and date triggers
- Interactive task addition through a command-line interface
- Improved error handling and logging
- Job management capabilities (pause, resume, retrieve job info)
- Configuration through environment variables
- Support for both thread and process pool executors

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/jimmc414/enhanced-apscheduler.git
   cd apscheduler
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install apscheduler python-dotenv sqlalchemy
   ```

## Configuration

Create a `.env` file in the project root directory with the following variables:

```
DB_URL=sqlite:///jobs.sqlite
MAX_THREADS=10
MAX_PROCESSES=5
TIMEZONE=UTC
```

Adjust these values according to your needs.

## Usage

1. Run the scheduler script:
   ```
   python scheduler.py
   ```

2. You will be presented with a menu where you can:
   - Add new tasks by typing 'add'
   - List all current tasks by typing 'list'
   - Start the scheduler by typing 'start'

3. When adding a task, follow the prompts to specify:
   - Task type (python_task or cli_command)
   - Task ID
   - Task arguments or command
   - Trigger type (interval, cron, or date)
   - Trigger details

4. After adding your desired tasks, start the scheduler.

5. The scheduler will run until you interrupt it with Ctrl+C.

## Task Types

1. Python Task:
   - Executes a Python function with two string arguments
   - Example: Logging a message with two parameters

2. CLI Command Task:
   - Executes a command-line instruction
   - Example: Running a shell command or script

## Trigger Types

1. Interval:
   - Runs the job at fixed time intervals
   - Specify the interval in minutes

2. Cron:
   - Runs the job on a cron-like schedule
   - Specify day of week, hour, and minute

3. Date:
   - Runs the job once at a specific date and time
   - Specify the date and time in YYYY-MM-DD HH:MM:SS format

## Example

```python
from scheduler import EnhancedAPScheduler

config = {
    'db_url': 'sqlite:///jobs.sqlite',
    'max_threads': 10,
    'max_processes': 5,
    'timezone': 'UTC'
}

scheduler = EnhancedAPScheduler(config)

# The add_task function will be called automatically when you run scheduler.py
# Follow the prompts to add tasks interactively

scheduler.start()
```

## Advanced Usage

You can also use the `EnhancedAPScheduler` class programmatically:

- Add a job: `scheduler.add_job(func, trigger, **kwargs)`
- Pause a job: `scheduler.pause_job('job_id')`
- Resume a job: `scheduler.resume_job('job_id')`
- Remove a job: `scheduler.remove_job('job_id')`
- Get all jobs: `scheduler.get_jobs()`

## Logging

Logs are written to `scheduler.log` in the project directory. Adjust the logging configuration in the script if needed.
