# APScheduler Implementation

This project provides an implementation of APScheduler, offering a more robust and flexible foundation for scheduling and managing jobs in Python applications.

## Features

- Encapsulated scheduler functionality in the `EnhancedAPScheduler` class
- Flexible job addition with support for cron, interval, and date triggers
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
   git clone https://github.com/yourusername/enhanced-apscheduler.git
   cd enhanced-apscheduler
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

1. Import the `EnhancedAPScheduler` class:
   ```python
   from enhanced_apscheduler import EnhancedAPScheduler
   ```

2. Create an instance of the scheduler:
   ```python
   config = {
       'db_url': 'sqlite:///jobs.sqlite',
       'max_threads': 10,
       'max_processes': 5,
       'timezone': 'UTC'
   }
   scheduler = EnhancedAPScheduler(config)
   ```

3. Define your job functions:
   ```python
   def my_job(arg1, arg2):
       print(f"Job executed with args: {arg1}, {arg2}")
   ```

4. Add jobs to the scheduler:
   ```python
   scheduler.add_job(
       my_job,
       {'type': 'interval', 'minutes': 5},
       args=['arg1_value', 'arg2_value'],
       id='my_job_id'
   )
   ```

5. Start the scheduler:
   ```python
   scheduler.start()
   ```

6. To shut down the scheduler gracefully:
   ```python
   scheduler.shutdown()
   ```

## Example

```python
from enhanced_apscheduler import EnhancedAPScheduler
import time

def print_hello():
    print("Hello, World!")

scheduler = EnhancedAPScheduler({})
scheduler.add_job(print_hello, {'type': 'interval', 'seconds': 10}, id='hello_job')

try:
    scheduler.start()
    while True:
        time.sleep(1)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
```

This example creates a job that prints "Hello, World!" every 10 seconds.

## Advanced Usage

- Pause a job: `scheduler.pause_job('job_id')`
- Resume a job: `scheduler.resume_job('job_id')`
- Remove a job: `scheduler.remove_job('job_id')`
- Get all jobs: `scheduler.get_jobs()`

## Logging

Logs are written to `scheduler.log` in the project directory. Adjust the logging configuration in the script if needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.