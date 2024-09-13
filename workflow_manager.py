# workflow_manager.py

import subprocess
import time
import logging
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from utils import wait_for_file, check_file_timestamp

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    exit_code: int
    stdout: str
    stderr: str

@dataclass
class Task:
    id: str
    command: str
    args: List[str]
    expected_exit_codes: List[int]
    output_files: List[str]
    retry_count: int
    retry_delay: int
    continue_on_failure: bool
    current_retry: int = 0
    timeout: Optional[int] = None  # Timeout for task execution in seconds

    def execute(self) -> ExecutionResult:
        full_command = ' '.join([self.command] + self.args)
        logger.info(f"Executing task '{self.id}': {full_command}")
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            logger.info(f"Task '{self.id}' executed with exit code {result.returncode}")
            return ExecutionResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except subprocess.TimeoutExpired:
            logger.error(f"Task '{self.id}' timed out after {self.timeout} seconds")
            return ExecutionResult(
                exit_code=-1,
                stdout='',
                stderr='Task timed out'
            )
        except Exception as e:
            logger.exception(f"An error occurred while executing task '{self.id}': {e}")
            return ExecutionResult(
                exit_code=-1,
                stdout='',
                stderr=str(e)
            )

    def monitor_output_files(self) -> bool:
        for file_path in self.output_files:
            logger.info(f"Monitoring output file '{file_path}' for task '{self.id}'")
            file_ready = wait_for_file(file_path, timeout=60)
            if not file_ready:
                logger.error(f"Output file '{file_path}' for task '{self.id}' is not ready after timeout")
                return False
            else:
                logger.info(f"Output file '{file_path}' for task '{self.id}' is ready")
        return True

@dataclass
class Workflow:
    id: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)
        logger.info(f"Task '{task.id}' added to workflow '{self.id}'")

class WorkflowManager:
    def __init__(self):
        self.workflows = {}  # type: Dict[str, Workflow]

    def add_workflow(self, workflow: Workflow):
        self.workflows[workflow.id] = workflow
        logger.info(f"Workflow '{workflow.id}' added to the manager")

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        return self.workflows.get(workflow_id)

    def execute_workflow(self, workflow_id: str):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            logger.error(f"Workflow '{workflow_id}' not found")
            return
        logger.info(f"Starting execution of workflow '{workflow_id}'")
        for task in workflow.tasks:
            success = self.execute_task(task)
            if not success:
                logger.error(f"Task '{task.id}' failed in workflow '{workflow_id}'")
                if not task.continue_on_failure:
                    logger.info(f"Stopping workflow '{workflow_id}' due to task failure")
                    break
                else:
                    logger.info(f"Continuing workflow '{workflow_id}' despite task failure")
        logger.info(f"Workflow '{workflow_id}' execution completed")

    def execute_task(self, task: Task) -> bool:
        while task.current_retry <= task.retry_count:
            result = task.execute()
            if result.exit_code in task.expected_exit_codes:
                logger.info(f"Task '{task.id}' completed successfully")
                if task.output_files:
                    files_ready = task.monitor_output_files()
                    if files_ready:
                        return True
                    else:
                        logger.error(f"Output files for task '{task.id}' not ready")
                        return False
                else:
                    return True
            else:
                logger.error(f"Task '{task.id}' failed with exit code {result.exit_code}")
                logger.error(f"Stdout: {result.stdout}")
                logger.error(f"Stderr: {result.stderr}")
                if task.current_retry < task.retry_count:
                    task.current_retry += 1
                    logger.info(f"Retrying task '{task.id}' ({task.current_retry}/{task.retry_count}) after {task.retry_delay} seconds")
                    time.sleep(task.retry_delay)
                else:
                    logger.error(f"Task '{task.id}' failed after {task.retry_count} retries")
                    return False
        return False  # Should not reach here, but added for clarity
