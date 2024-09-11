# APScheduler Implementation

This project provides an implementation of APScheduler, offering a foundation for scheduling and managing jobs in Python applications. It includes an interactive interface for adding, managing, and monitoring tasks.

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

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone this repository:
   ```
   git clone [https://github.com/jimmc414/scheduler.git](https://github.com/jimmc414/scheduler.git)
   cd scheduler
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install scheduler python-dotenv sqlalchemy rich
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

## Example Usage Scenarios

1. Daily Backup (using cron trigger):
   - Task Type: cli_command
   - Command: `backup_script.sh`
   - Trigger: cron, every day at 1:00 AM

2. Hourly System Check (using interval trigger):
   - Task Type: python_task
   - Arguments: "system_check" "hourly"
   - Trigger: interval, every 60 minutes

3. One-time Database Cleanup (using date trigger):
   - Task Type: cli_command
   - Command: `python database_cleanup.py`
   - Trigger: date, specific time in the future

## Logging

Logs are written to `scheduler.log` in the project directory. Adjust the logging configuration in the script if needed.

## Additional Notes

- The scheduler persists tasks to a SQLite database, allowing them to survive restarts.
- The `job_listener` provides feedback on job execution and errors.
- The Rich library enhances the console output for better readability.

Please refer to the in-code comments and examples for more detailed usage instructions.

```

**Key changes reflected in the updated readme:**

- **Enhanced Features:** Highlighted the interactive task management, improved logging, task persistence, and Rich console output.
- **Installation:** Added `rich` to the required dependencies.
- **Usage:** Emphasized the interactive menu-driven approach.
- **Additional Notes:** Included information about task persistence, the `job_listener`, and the use of Rich.

Feel free to ask if you have any further questions or modifications!
