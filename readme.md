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
- **Default Answers and IDs**: All user prompts provide default answers, and IDs are auto-generated if not provided.
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

### Default Answers and IDs

- **Default Answers**: All prompts provide default answers, displayed in square brackets. Press Enter to accept the default.
- **Auto-generated IDs**:
  - **Workflow IDs**: If you don't provide a workflow ID, a default unique ID like `workflow_1` is assigned.
  - **Task IDs**: If you don't provide a task ID, a default unique ID like `task_1` is assigned within the workflow.

### Creating a Workflow

Select option `2` from the main menu.

- **Prompt**: Enter a unique workflow ID `[default: 'workflow_1']`.
- **Action**: Creates a new workflow with the specified or default ID.

### Adding Tasks to a Workflow

Select option `3` from the main menu.

- **Prompt**: Enter the workflow ID `[default: 'workflow_1']`.
- **Task Details**:
  - **Task ID**: Unique identifier for the task `[default: 'task_1']`.
  - **Command**: Batch file or Python script to execute `[default: 'echo']`.
  - **Arguments**: Arguments required by the command `[default: 'Hello World']`.
  - **Expected Exit Codes**: Exit codes indicating successful execution `[default: '0']`.
  - **Output Files**: Paths to output files `[default: none]`.
  - **Retry Count**: Number of times to retry the task upon failure `[default: 0]`.
  - **Retry Delay**: Delay in seconds between retries `[default: 0]`.
  - **Continue on Failure**: Whether to continue executing the workflow if the task fails `[default: 'no']`.

### Scheduling a Workflow

Select option `4` from the main menu.

- **Prompt**: Enter the workflow ID to schedule `[default: 'workflow_1']`.
- **Trigger Type**: Choose from `interval`, `cron`, or `date` `[default: 'interval']`.
  - **Interval**:
    - Enter the interval in minutes `[default: 60]`.
  - **Cron**:
    - Enter day of the week `[default: 'mon-fri']`.
    - Enter hour `[default: 0]`.
    - Enter minute `[default: 0]`.
  - **Date**:
    - Enter date and time in `YYYY-MM-DD HH:MM:SS` format `[default: current time]`.
- **Action**: Schedules the workflow with the specified or default trigger.

### Starting and Stopping the Scheduler

- **Start Scheduler**: Select option `6`.
- **Stop Scheduler**: Select option `7`.

### Listing Workflows and Scheduled Jobs

- **List Workflows**: Select option `1` to view all workflows and the number of tasks in each.
- **List Scheduled Workflows**: Select option `5` to view all scheduled workflows, including next run times.

## Task Configuration

When adding a task to a workflow, provide the following information:

- **Task ID**: A unique identifier for the task `[default: 'task_N']`.
- **Command**: The batch file or Python script to execute `[default: 'echo']`.
- **Arguments**: Any arguments required by the command `[default: 'Hello World']`.
- **Expected Exit Codes**: Exit codes indicating successful execution `[default: '0']`.
- **Output Files**: Paths to files that the task is expected to generate `[default: none]`.
- **Retry Count**: Number of times to retry the task upon failure `[default: 0]`.
- **Retry Delay**: Delay in seconds between retries `[default: 0]`.
- **Continue on Failure**: Whether to continue executing the workflow if the task fails `[default: 'no']`.

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

- **Action**: Create a new workflow. When prompted, accept the default ID `workflow_1`.

#### 2. Add Tasks to the Workflow

##### Task 1: Backup Database

- **Action**: Add a task to `workflow_1`. When prompted:
  - **Task ID**: Accept default `task_1`.
  - **Command**: Enter `backup_database.bat`.
  - **Arguments**: *(leave empty if none)*.
  - **Expected Exit Codes**: Accept default `0`.
  - **Output Files**: Enter `C:\backups\db_backup.sql`.
  - **Retry Count**: Enter `2`.
  - **Retry Delay**: Enter `30`.
  - **Continue on Failure**: Accept default `no`.

##### Task 2: Compress Backup

- **Action**: Add another task to `workflow_1`. When prompted:
  - **Task ID**: Accept default `task_2`.
  - **Command**: Enter `python`.
  - **Arguments**: Enter `compress_backup.py C:\backups\db_backup.sql`.
  - **Expected Exit Codes**: Accept default `0`.
  - **Output Files**: Enter `C:\backups\db_backup.zip`.
  - **Retry Count**: Enter `1`.
  - **Retry Delay**: Enter `15`.
  - **Continue on Failure**: Accept default `no`.

#### 3. Schedule the Workflow

- **Action**: Schedule `workflow_1`. When prompted:
  - **Trigger Type**: Enter `cron`.
  - **Day of Week**: Accept default `mon-fri`.
  - **Hour**: Enter `1`.
  - **Minute**: Enter `0`.

#### 4. Start the Scheduler

- **Action**: Start the scheduler to enable execution of scheduled workflows.

#### 5. Monitor Execution

- **Check Logs**: Review `scheduler.log` for execution details and any errors.
- **Output Files**: Verify that the backup and compressed files are created in `C:\backups\`.

## Additional Notes

- **Default Values**: The application provides sensible defaults for all user inputs to streamline the setup process.
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
- **GitHub**: [https://github.com/yourusername/workflow-scheduler](https://github.com/yourusername/workflow-scheduler)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Disclaimer**: This project is provided "as-is" without any warranties. Use at your own risk.
```

---

### **Explanation**

The updated `scheduler.py` now includes default answers for all user prompts. When an ID is requested, it suggests an available ID by generating one that isn't already in use.

- **Default Workflow ID Generation**: The `generate_default_workflow_id()` function creates a unique workflow ID by incrementing a number until an unused ID is found.

- **Default Task ID Generation**: The `generate_default_task_id(workflow)` function creates a unique task ID within the context of a workflow.

- **User Prompts with Defaults**: All `console.input()` calls now include `[default: ...]` in the prompt, and the code uses the default if the user presses Enter without typing anything.

- **Handling Numeric Inputs**: For inputs like retry count and delay, the code checks if the input is a digit and falls back to the default if it's not provided or invalid.

- **Scheduler Start/Stop Messages**: The code now informs the user if they try to start the scheduler when it's already running or stop it when it's not running.

- **Readme Updates**: The `README.md` has been updated to reflect these changes, informing users about the default answers and auto-generated IDs.

---

### **Next Steps**

- **Testing**: Run the updated application to ensure that default values are correctly applied when the user presses Enter without providing input.

- **Review**: Verify that the auto-generated IDs do not conflict with existing IDs, especially when workflows or tasks are deleted and new ones are created.

- **Enhancements**: Consider adding features like editing existing workflows or tasks, deleting workflows, and better error messages for invalid inputs.
