# Workflow Scheduler with APScheduler

This project implements a workflow scheduler using APScheduler, allowing for the scheduling and management of workflows consisting of sequential tasks with dependencies. It includes a command-line interface (CLI) for creating workflows, adding tasks, scheduling workflows, and monitoring execution.

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

- Python 3.7+
- pip (Python package manager)
- pywin32 library (for Windows-specific file operations)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/jimmc414/scheduler.git
   cd workflow-scheduler
