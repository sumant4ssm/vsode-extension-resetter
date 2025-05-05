"""
Machine ID handling for VSCode Extension Resetter.
"""

import logging
from pathlib import Path

from .utils import (
    get_machine_id_path,
    backup_file,
    restore_file,
    generate_new_machine_id,
    logger
)

def get_current_machine_id():
    """
    Get the current VSCode machine ID.
    
    Returns:
        str: Current machine ID or None if not found
    """
    machine_id_path = get_machine_id_path()
    if not machine_id_path.exists():
        logger.warning(f"Machine ID file not found at {machine_id_path}")
        return None
    
    try:
        with open(machine_id_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Failed to read machine ID: {e}")
        return None

def reset_machine_id(backup=True):
    """
    Reset the VSCode machine ID.
    
    Args:
        backup (bool): Whether to create a backup before resetting
        
    Returns:
        tuple: (success, backup_id, old_id, new_id)
    """
    machine_id_path = get_machine_id_path()
    old_id = get_current_machine_id()
    backup_id = None
    
    # Create backup if requested
    if backup and machine_id_path.exists():
        backup_id, _ = backup_file(machine_id_path)
    
    # Generate and write new machine ID
    new_id = generate_new_machine_id()
    try:
        # Create parent directories if they don't exist
        machine_id_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(machine_id_path, 'w', encoding='utf-8') as f:
            f.write(new_id)
        logger.info(f"Machine ID reset from {old_id} to {new_id}")
        return True, backup_id, old_id, new_id
    except Exception as e:
        logger.error(f"Failed to reset machine ID: {e}")
        return False, backup_id, old_id, None

def restore_machine_id(backup_id):
    """
    Restore the VSCode machine ID from a backup.
    
    Args:
        backup_id (str): Backup ID to restore from
        
    Returns:
        bool: True if restore was successful, False otherwise
    """
    from .utils import get_backup_dir
    
    machine_id_path = get_machine_id_path()
    backup_path = get_backup_dir() / backup_id / "machineId"
    
    if not backup_path.exists():
        logger.error(f"Backup file {backup_path} does not exist")
        return False
    
    return restore_file(backup_path, machine_id_path)
