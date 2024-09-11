import os
from datetime import datetime
from typing import Union

def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists at the given path.
    
    :param file_path: Path to the file
    :return: True if the file exists, False otherwise
    """
    try:
        return os.path.isfile(file_path)
    except OSError as e:
        print(f"Error checking if file exists: {e}")
        return False

def check_file_absent(file_path: str) -> bool:
    """
    Check if a file does not exist at the given path.
    
    :param file_path: Path to the file
    :return: True if the file does not exist, False if it does
    """
    try:
        return not os.path.isfile(file_path)
    except OSError as e:
        print(f"Error checking if file is absent: {e}")
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

def check_file_locked(file_path: str) -> Union[bool, None]:
    """
    Check if a file is currently locked by another process.
    A simple implementation that attempts to open the file.
    
    :param file_path: Path to the file
    :return: True if the file is locked, False if it's not, None if there was an error
    """
    try:
        with open(file_path, 'a'):
            return False  # File is not locked
    except IOError:
        return True  # File is locked
    except OSError as e:
        print(f"Error checking if file is locked: {e}")
        return None

def check_current_date(expected_date: datetime) -> bool:
    """
    Check if the current date matches the expected date.
    
    :param expected_date: The date to compare against
    :return: True if the current date matches the expected date, False otherwise
    """
    try:
        return datetime.now().date() == expected_date.date()
    except Exception as e:
        print(f"Error checking current date: {e}")
        return False

def check_file_size(file_path: str, expected_size: int, operator: str = '==') -> Union[bool, None]:
    """
    Check if the file size satisfies the comparison.
    
    :param file_path: Path to the file
    :param expected_size: Size to compare against (in bytes)
    :param operator: Can be '==', '>=', '<=', '>', '<'
    :return: Result of the comparison, or None if there was an error
    """
    try:
        if not os.path.isfile(file_path):
            return None
        file_size = os.path.getsize(file_path)
        if operator == '==':
            return file_size == expected_size
        elif operator == '>=':
            return file_size >= expected_size
        elif operator == '<=':
            return file_size <= expected_size
        elif operator == '>':
            return file_size > expected_size
        elif operator == '<':
            return file_size < expected_size
        else:
            raise ValueError(f"Unsupported operator: {operator}")
    except OSError as e:
        print(f"Error checking file size: {e}")
        return None

def check_file_permission(file_path: str, permission: str) -> Union[bool, None]:
    """
    Check if the file has the specified permission.
    
    :param file_path: Path to the file
    :param permission: Permission to check ('read', 'write', or 'execute')
    :return: True if the file has the permission, False if not, None if there was an error
    """
    try:
        if not os.path.exists(file_path):
            return None
        if permission == 'read':
            return os.access(file_path, os.R_OK)
        elif permission == 'write':
            return os.access(file_path, os.W_OK)
        elif permission == 'execute':
            return os.access(file_path, os.X_OK)
        else:
            raise ValueError(f"Unsupported permission: {permission}")
    except OSError as e:
        print(f"Error checking file permission: {e}")
        return None