# utils.py

import os
import time
from datetime import datetime
from typing import Union
import win32api
import win32con
import win32file
import pywintypes


def is_file_locked(file_path: str) -> bool:
    """
    Check if a file is locked by trying to open it with exclusive access.
    Uses pywin32 to interact with Windows APIs.

    :param file_path: Path to the file
    :return: True if the file is locked, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    try:
        handle = win32file.CreateFile(
            file_path,
            win32con.GENERIC_READ,
            0,  # Deny others access
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        win32file.CloseHandle(handle)
        return False
    except pywintypes.error as e:
        # Error code 32: Sharing violation (file is locked)
        if e.winerror == 32:
            return True
        else:
            print(f"Error checking if file is locked: {e}")
            return False


def wait_for_file(file_path: str, timeout: int = 60) -> bool:
    """
    Wait until the file exists and is not locked, or until timeout is reached.

    :param file_path: Path to the file
    :param timeout: Maximum time to wait in seconds
    :return: True if the file is ready, False if timeout reached
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        if os.path.exists(file_path) and not is_file_locked(file_path):
            return True
        time.sleep(1)
    return False


def check_file_timestamp(file_path: str, comparison_time: datetime, operator: str = '>=') -> Union[bool, None]:
    """
    Check if the file's modification time satisfies the comparison.

    :param file_path: Path to the file
    :param comparison_time: Time to compare against
    :param operator: Can be '>=', '<=', '==', '>', '<'
    :return: Result of the comparison, or None if there was an error
    """
    try:
        if not os.path.isfile(file_path):
            return None
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        if operator == '>=':
            return file_mod_time >= comparison_time
        elif operator == '<=':
            return file_mod_time <= comparison_time
        elif operator == '==':
            return file_mod_time == comparison_time
        elif operator == '>':
            return file_mod_time > comparison_time
        elif operator == '<':
            return file_mod_time < comparison_time
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    except OSError as e:
        print(f"Error checking file timestamp: {e}")
        return None

# Additional utility functions can be added as needed.
