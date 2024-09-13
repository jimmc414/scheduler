# Workflow Scheduler with APScheduler

This project implements a workflow scheduler using [APScheduler](https://apscheduler.readthedocs.io/en/stable/), allowing for the scheduling and management of workflows consisting of sequential tasks with dependencies. It provides a command-line interface (CLI) for creating workflows, adding tasks, scheduling workflows, and monitoring execution.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Creating a Workflow](#creating-a-workflow)
  - [Adding Tasks to a Workflow](#adding-tasks-to-a-workflow)
  - [Scheduling a Workflow](#scheduling-a-workflow)
  - [Starting and Stopping the Scheduler](#starting-and-stopping-the-scheduler)
  - [Listing Workflows and Scheduled Jobs](#listing-workflows-and-scheduled-jobs)
- [Task Configuration](#task-configuration)
- [Workflow Execution](#workflow-execution)
- [Logging](#logging)
- [Example Usage](#example-usage)
- [Additional Notes](#additional-notes)
- [Support](#support)
- [License](#license)

## Features

- **Workflow Management**: Define workflows containing multiple tasks executed in sequence.
- **Task Execution**: Support for executing batch files and Python scripts.
- **Task Monitoring**: Check for the existence and readiness of output files, including handling file locks.
- **Retry Mechanism**: Configurable retries for failed tasks with delays.
- **Error Handling**: Logging of task execution results, including exit codes and output.
- **Scheduling**: Use APScheduler to schedule workflows with interval, cron, or date triggers.
- **CLI Interface**: Interactive menu for managing workflows and scheduler operations.
- **Logging**: Detailed logging to `scheduler.log` for monitoring and debugging.

## Prerequisites

- **Operating System**: Windows 10/11 or Windows Server 2019
- **Python**: Version 3.7 or higher
- **pip**: Python package manager
- **pywin32**: Library for Windows-specific file operations

## Installation

1. **Clone the repository**:


   ```bash
   git clone https://github.com/jimmc414/scheduler.git
   cd scheduler
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Ensure that `pywin32` is included in `requirements.txt`.

## Configuration

Create a `.env` file in the project root directory with the following variables:

```env
DB_URL=sqlite:///jobs.sqlite
MAX_THREADS=10
MAX_PROCESSES=5
TIMEZONE=UTC
```

Adjust these values according to your needs.

## Usage

Run the scheduler script and use the CLI to manage workflows and tasks.

### Running the Scheduler Script

```bash
python scheduler.py
```

### Main Menu Options

1. **List workflows**: View existing workflows.
2. **Create workflow**: Define a new workflow.
3. **Add task to workflow**: Add tasks to a workflow with execution details.
4. **Schedule workflow**: Schedule a workflow using interval, cron, or date triggers.
5. **List scheduled workflows**: View all scheduled workflows.
6. **Start scheduler**: Start APScheduler to begin executing scheduled workflows.
7. **Stop scheduler**: Stop the scheduler if needed.
8. **Quit**: Exit the CLI.

### Creating a Workflow

Select option `2` from the main menu.

- **Prompt**: Enter a unique workflow ID.
- **Action**: Creates a new workflow with the specified ID.

### Adding Tasks to a Workflow

Select option `3` from the main menu.

- **Prompt**: Enter the workflow ID to add a task to.
- **Task Details**:
  - **Task ID**: Unique identifier for the task.
  - **Command**: Batch file or Python script to execute.
  - **Arguments**: Any arguments required by the command.
  - **Expected Exit Codes**: Exit codes indicating successful execution (e.g., `0`).
  - **Output Files**: Paths to files that the task is expected to generate.
  - **Retry Count**: Number of times to retry the task upon failure.
  - **Retry Delay**: Delay in seconds between retries.
  - **Continue on Failure**: Whether to continue executing the workflow if the task fails.

### Scheduling a Workflow

Select option `4` from the main menu.

- **Prompt**: Enter the workflow ID to schedule.
- **Trigger Type**: Choose from `interval`, `cron`, or `date`.
  - **Interval**:
    - Enter the interval in minutes.
  - **Cron**:
    - Enter day of the week (e.g., `mon-fri`, `mon`, `tue`).
    - Enter hour (0-23).
    - Enter minute (0-59).
  - **Date**:
    - Enter date and time in `YYYY-MM-DD HH:MM:SS` format.
- **Action**: Schedules the workflow with the specified trigger.

### Starting and Stopping the Scheduler

- **Start Scheduler**: Select option `6`.
- **Stop Scheduler**: Select option `7`.

### Listing Workflows and Scheduled Jobs

- **List Workflows**: Select option `1` to view all workflows and the number of tasks in each.
- **List Scheduled Workflows**: Select option `5` to view all scheduled workflows, including next run times.

## Task Configuration

When adding a task to a workflow, provide the following information:

- **Task ID**: A unique identifier for the task.
- **Command**: The batch file or Python script to execute.
- **Arguments**: Any arguments required by the command (separated by spaces).
- **Expected Exit Codes**: Exit codes indicating successful execution (e.g., `0`).
- **Output Files**: Paths to files that the task is expected to generate (separated by commas).
- **Retry Count**: Number of times to retry the task upon failure (default is `0`).
- **Retry Delay**: Delay in seconds between retries (default is `0`).
- **Continue on Failure**: Whether to continue executing the workflow if the task fails (`yes` or `no`).

## Workflow Execution

- **Sequential Execution**: Tasks within a workflow are executed in order.
- **Monitoring Output Files**:
  - The scheduler waits for output files to be created and ensures they are not locked.
  - Waits up to 60 seconds for each file before timing out.
- **Error Handling**:
  - If a task fails and retries are exhausted, the workflow stops unless configured to continue.
  - All errors are logged with details, including exit codes and output.

## Logging

- **Log File**: Logs are written to `scheduler.log` in the project directory.
- **Log Details**:
  - Timestamps
  - Workflow and task identifiers
  - Execution status and exit codes
  - Standard output and error messages
- **Log Levels**:
  - `INFO`: General execution information.
  - `ERROR`: Errors during task execution or workflow processing.
  - `EXCEPTION`: Unhandled exceptions.

## Example Usage

### Scenario: Daily Backup Workflow

#### 1. Create a Workflow

- **Workflow ID**: `daily_backup`
- **Action**: Create a new workflow with this ID.

#### 2. Add Tasks to the Workflow

##### Task 1: Backup Database

- **Task ID**: `backup_db`
- **Command**: `backup_database.bat`
- **Arguments**: *(leave empty if none)*
- **Expected Exit Codes**: `0`
- **Output Files**: `C:\backups\db_backup.sql`
- **Retry Count**: `2`
- **Retry Delay**: `30`
- **Continue on Failure**: `no`

##### Task 2: Compress Backup

- **Task ID**: `compress_backup`
- **Command**: `python`
- **Arguments**: `compress_backup.py C:\backups\db_backup.sql`
- **Expected Exit Codes**: `0`
- **Output Files**: `C:\backups\db_backup.zip`
- **Retry Count**: `1`
- **Retry Delay**: `15`
- **Continue on Failure**: `no`

#### 3. Schedule the Workflow

- **Trigger Type**: `cron`
- **Day of Week**: `mon-fri`
- **Hour**: `1`
- **Minute**: `0`
- **Action**: The workflow `daily_backup` is scheduled to run at 1:00 AM from Monday to Friday.

#### 4. Start the Scheduler

- **Action**: Start the scheduler to enable execution of scheduled workflows.

#### 5. Monitor Execution

- **Check Logs**: Review `scheduler.log` for execution details and any errors.
- **Output Files**: Verify that the backup and compressed files are created in `C:\backups\`.

## Additional Notes

- **Windows Compatibility**: Designed for Windows environments, utilizing `pywin32` for file operations.
- **Extensibility**: The codebase is designed to be extensible for future enhancements, such as parallel task execution.
- **Error Handling**:
  - The scheduler handles exceptions and logs detailed error messages.
  - Tasks that time out or fail due to exceptions are considered failed executions.
- **File Locking**:
  - The scheduler checks for file locks to ensure that files are fully written before proceeding.
  - Uses Windows-specific APIs via `pywin32` to detect file locks.

## Support

For any issues, questions, or suggestions, please contact:

- **Email**: [youremail@example.com](mailto:youremail@example.com)
- **GitHub**: https://github.com/jimmc414/scheduler.git

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This project is provided "as-is" without any warranties. Use at your own risk.