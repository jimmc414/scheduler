# Step-by-Step Guide: Implementing APScheduler for a 3-Step Process

This guide will walk you through implementing the enhanced APScheduler for a specific 3-step process:

1. Run a command line process: `\\mp-cp\bin\acuthin.exe mp-cp f1 stratus`
2. Wait for the process to finish
3. Move the file `output.csv` from `m:\spbw\output.csv` to `\\thinclient\d$\cp\edi\spbw\output.csv`, overwriting any existing file

## Step 1: Set Up the Project

1. Create a new Python file named `scheduler_implementation.py`.
2. Install the required dependencies:
   ```
   pip install apscheduler python-dotenv sqlalchemy
   ```

## Step 2: Import Required Modules

Add the following imports at the top of your `scheduler_implementation.py` file:

```python
import os
import subprocess
import shutil
from typing import Any, Dict
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```

## Step 3: Define the EnhancedAPScheduler Class

Copy the `EnhancedAPScheduler` class from the previous implementation into your file. You can use the full implementation provided earlier.

## Step 4: Define the 3-Step Process Function

Add the following function to handle your specific 3-step process:

```python
def three_step_process():
    try:
        # Step 1: Run command line process
        logger.info("Starting command line process")
        result = subprocess.run(['\\\\mp-cp\\bin\\acuthin.exe', 'mp-cp', 'f1', 'stratus'], 
                                capture_output=True, text=True, check=True)
        logger.info(f"Command output: {result.stdout}")
        
        # Step 2: Wait for the process to finish (already handled by subprocess.run)
        logger.info("Command line process completed")
        
        # Step 3: Move the output file
        source_path = r'm:\spbw\output.csv'
        destination_path = r'\\thinclient\d$\cp\edi\spbw\output.csv'
        
        shutil.copy2(source_path, destination_path)
        logger.info(f"File moved from {source_path} to {destination_path}")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with error: {e.stderr}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
```

## Step 5: Set Up and Run the Scheduler

Add the following code to set up and run the scheduler with your 3-step process:

```python
if __name__ == '__main__':
    config: Dict[str, Any] = {
        'db_url': os.getenv('DB_URL', 'sqlite:///jobs.sqlite'),
        'max_processes': int(os.getenv('MAX_PROCESSES', 5)),
        'timezone': os.getenv('TIMEZONE', 'UTC')
    }

    scheduler = EnhancedAPScheduler(config)

    # Add the 3-step process job
    scheduler.add_job(
        three_step_process,
        {'type': 'interval', 'minutes': 30},  # Run every 30 minutes
        id='three_step_process_job'
    )

    try:
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        # Keep the script running
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully.")
```

## Step 6: Create a .env File

Create a `.env` file in the same directory as your Python script with the following content:

```
DB_URL=sqlite:///jobs.sqlite
MAX_PROCESSES=5
TIMEZONE=UTC
```

Adjust these values as needed for your environment.

## Step 7: Run the Scheduler

Run your script using Python:

```
python scheduler_implementation.py
```

The scheduler will start and run your 3-step process every 30 minutes.

## Additional Notes

1. Ensure that the Python script has the necessary permissions to access the network paths and execute the command-line process.
2. The `shutil.copy2()` function is used instead of `shutil.move()` to overwrite the destination file if it exists.
3. Error handling has been added to catch and log potential issues during the process.
4. You may need to adjust the network paths if they use different conventions in your Python environment.
5. Consider adding more robust error handling and retry mechanisms for production use, especially for network operations.

By following these steps, you'll have implemented the enhanced APScheduler to run your specific 3-step process at regular intervals.



# Step-by-Step Guide: Implementing APScheduler for Multiple Tasks

This guide will walk you through implementing the enhanced APScheduler for multiple tasks, including a specific 3-step process and how to add future tasks.

## Steps 1-6: Initial Setup and 3-Step Process Implementation

[The content for steps 1-6 remains the same as in the previous version of this artifact.]

## Step 7: Adding Future Tasks

To make it easier to add future tasks to your scheduler, let's modify the implementation to support multiple task functions. Update your `scheduler_implementation.py` file as follows:

1. After the `three_step_process()` function, add a new section for task definitions:

```python
# Task Definitions
def three_step_process():
    # [The existing three_step_process code remains here]

def another_example_task():
    logger.info("Running another example task")
    # Add your task logic here

def yet_another_task(arg1, arg2):
    logger.info(f"Running yet another task with args: {arg1}, {arg2}")
    # Add your task logic here

# Add more task functions as needed
```

2. Modify the main execution block to support multiple tasks:

```python
if __name__ == '__main__':
    config: Dict[str, Any] = {
        'db_url': os.getenv('DB_URL', 'sqlite:///jobs.sqlite'),
        'max_processes': int(os.getenv('MAX_PROCESSES', 5)),
        'timezone': os.getenv('TIMEZONE', 'UTC')
    }

    scheduler = EnhancedAPScheduler(config)

    # Add jobs to the scheduler
    jobs = [
        {
            'func': three_step_process,
            'trigger': {'type': 'interval', 'minutes': 30},
            'id': 'three_step_process_job'
        },
        {
            'func': another_example_task,
            'trigger': {'type': 'cron', 'day_of_week': 'mon-fri', 'hour': 9, 'minute': 0},
            'id': 'another_example_task_job'
        },
        {
            'func': yet_another_task,
            'trigger': {'type': 'interval', 'hours': 2},
            'id': 'yet_another_task_job',
            'args': ['arg1_value', 'arg2_value']
        }
        # Add more jobs as needed
    ]

    for job in jobs:
        scheduler.add_job(job['func'], job['trigger'], id=job['id'], args=job.get('args', []))

    try:
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to exit.")
        # Keep the script running
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully.")
```

## Step 8: Adding New Tasks in the Future

To add new tasks to your scheduler in the future, follow these steps:

1. Define your new task function in the "Task Definitions" section of the script:

```python
def new_task_function():
    logger.info("Running new task")
    # Add your new task logic here
```

2. Add the new task to the `jobs` list in the main execution block:

```python
jobs = [
    # ... existing jobs ...
    {
        'func': new_task_function,
        'trigger': {'type': 'interval', 'hours': 1},
        'id': 'new_task_job'
    }
]
```

3. If your new task requires arguments, you can include them like this:

```python
def new_task_with_args(arg1, arg2):
    logger.info(f"Running new task with args: {arg1}, {arg2}")
    # Add your new task logic here

# In the jobs list:
{
    'func': new_task_with_args,
    'trigger': {'type': 'cron', 'day_of_week': 'mon', 'hour': 12},
    'id': 'new_task_with_args_job',
    'args': ['value1', 'value2']
}
```

4. Save the updated `scheduler_implementation.py` file and restart the scheduler for the changes to take effect.

## Additional Notes for Managing Multiple Tasks

1. **Unique Job IDs**: Ensure that each job has a unique `id`. This allows you to manage jobs individually (e.g., pause, resume, or remove specific jobs).

2. **Trigger Types**: The scheduler supports different trigger types:
   - `interval`: Run the job at fixed time intervals.
   - `cron`: Run the job on a cron-like schedule.
   - `date`: Run the job once at a specific date and time.

3. **Resource Management**: As you add more tasks, be mindful of system resources. Adjust the `max_processes` in the config if needed.

4. **Error Handling**: Implement proper error handling for each task to prevent one failing task from affecting others.

5. **Logging**: Consider implementing task-specific logging to easily track the execution of different tasks.

6. **Testing**: Always test new tasks in a non-production environment before adding them to your production scheduler.

By following these steps and guidelines, you can easily add and manage multiple tasks in your APScheduler implementation, allowing for flexible and scalable job scheduling.