# Enhanced APScheduler Implementation

This project provides an implementation of APScheduler, for scheduling and managing jobs in Python applications. It includes an interactive interface for adding, managing, and monitoring tasks, and uses utility functions to verify prerequisites for task execution.

## Features

- Encapsulated scheduler functionality in the `EnhancedAPScheduler` class
- Flexible job addition with support for cron, interval, and date triggers
- Interactive task addition, management, and monitoring through a command-line interface
- Improved error handling and logging with a dedicated `job_listener`
- Job management capabilities (pause, resume, remove, retrieve job info)
- Configuration through environment variables
- Support for both thread and process pool executors
- Task persistence using SQLAlchemyJobStore (SQLite database)
- Rich console output for improved user experience
- Utility functions for common prerequisite checks, encapsulated in `utils.py`
- New task types utilizing utility functions for file and date checks

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/enhanced-apscheduler.git
   cd enhanced-apscheduler
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
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
   ```bash
   python scheduler.py
   ```

2. You will be presented with an interactive menu where you can:
   - List all scheduled tasks
   - Add new tasks
   - Remove existing tasks
   - Pause or resume tasks
   - Start or stop the scheduler

3. Follow the prompts to perform the desired actions.

## Task Types

1. Python Task:
   - Executes a Python function with two string arguments
   - Example: Logging a message with two parameters

2. CLI Command Task:
   - Executes a command-line instruction
   - Example: Running a shell command or script

3. File Check Task:
   - Checks if a file exists, is locked, and compares its modification time
   - Uses utility functions from `utils.py`

4. Date Check Task:
   - Checks if the current date matches an expected date
   - Uses utility functions from `utils.py`

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

## Utility Functions

The `utils.py` file contains several utility functions for common file and date operations:

1. `check_file_exists(file_path: str) -> bool`:
   - Checks if a file exists at the given path

2. `check_file_absent(file_path: str) -> bool`:
   - Checks if a file does not exist at the given path

3. `check_file_timestamp(file_path: str, comparison_time: datetime, operator: str = '>=') -> Union[bool, None]`:
   - Compares the file's modification time with a given datetime
   - Supports operators: '>=', '<=', '==', '>', '<'

4. `check_file_locked(file_path: str) -> Union[bool, None]`:
   - Checks if a file is currently locked by another process

5. `check_current_date(expected_date: datetime) -> bool`:
   - Checks if the current date matches the expected date

6. `check_file_size(file_path: str, expected_size: int, operator: str = '==') -> Union[bool, None]`:
   - Compares the file size with an expected size
   - Supports operators: '==', '>=', '<=', '>', '<'

7. `check_file_permission(file_path: str, permission: str) -> Union[bool, None]`:
   - Checks if the file has the specified permission ('read', 'write', or 'execute')

These utility functions include error handling and return `None` in case of errors.

## Example Usage Scenarios

1. Daily Backup (using cron trigger):
   - Task Type: cli_command
   - Command: `backup_script.sh`
   - Trigger: cron, every day at 1:00 AM

2. Hourly File Check (using interval trigger):
   - Task Type: file_check
   - Arguments: "/path/to/file.txt", "2023-05-01 00:00:00"
   - Trigger: interval, every 60 minutes

3. Monthly Date Check (using cron trigger):
   - Task Type: date_check
   - Arguments: "2023-05-01" (first day of the month)
   - Trigger: cron, on the 1st of every month at 9:00 AM

## Logging

Logs are written to `scheduler.log` in the project directory. Adjust the logging configuration in the script if needed.

## Additional Notes

- The scheduler persists tasks to a SQLite database, allowing them to survive restarts.
- The `job_listener` provides feedback on job execution and errors.
- The Rich library enhances the console output for better readability.
- Utility functions in `utils.py` include error handling and return `None` for file system errors.
