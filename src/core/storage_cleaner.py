"""
Storage cleaner for VSCode Extension Resetter.
"""

import os
import json
import shutil
import sqlite3
from pathlib import Path

from .utils import (
    get_vscode_path,
    backup_file,
    restore_file,
    logger
)

def backup_global_storage(backup_id=None):
    """
    Backup the entire global storage directory.
    
    Args:
        backup_id (str, optional): Backup ID. If None, a new ID will be created.
        
    Returns:
        tuple: (backup_id, success)
    """
    from .utils import create_backup_id, get_backup_dir
    
    if backup_id is None:
        backup_id = create_backup_id()
    
    storage_path = get_vscode_path() / "User" / "globalStorage"
    if not storage_path.exists():
        logger.warning(f"Global storage directory not found at {storage_path}")
        return backup_id, False
    
    backup_dir = get_backup_dir() / backup_id / "globalStorage"
    backup_dir.mkdir(exist_ok=True, parents=True)
    
    try:
        # Copy all files from global storage to backup
        for item in storage_path.glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to(storage_path)
                backup_item = backup_dir / rel_path
                backup_item.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy2(item, backup_item)
        
        logger.info(f"Backed up global storage to {backup_dir}")
        return backup_id, True
    except Exception as e:
        logger.error(f"Failed to backup global storage: {e}")
        return backup_id, False

def clean_global_storage(backup=True):
    """
    Clean the entire global storage directory.
    
    Args:
        backup (bool): Whether to create a backup before cleaning
        
    Returns:
        tuple: (success, backup_id)
    """
    storage_path = get_vscode_path() / "User" / "globalStorage"
    backup_id = None
    
    # Create backup if requested
    if backup and storage_path.exists():
        backup_id, _ = backup_global_storage()
    
    try:
        # Remove global storage directory
        if storage_path.exists():
            shutil.rmtree(storage_path)
            logger.info(f"Removed global storage directory")
        
        # Create empty global storage directory
        storage_path.mkdir(exist_ok=True, parents=True)
        
        return True, backup_id
    except Exception as e:
        logger.error(f"Failed to clean global storage: {e}")
        return False, backup_id

def backup_state_db(backup_id=None):
    """
    Backup the VSCode state database.
    
    Args:
        backup_id (str, optional): Backup ID. If None, a new ID will be created.
        
    Returns:
        tuple: (backup_id, success)
    """
    db_path = get_vscode_path() / "User" / "globalStorage" / "state.vscdb"
    if not db_path.exists():
        logger.warning(f"VSCode state database not found at {db_path}")
        return backup_id, False
    
    backup_id, backup_path = backup_file(db_path, backup_id)
    return backup_id, backup_path is not None

def reset_state_db(backup=True):
    """
    Reset the VSCode state database.
    
    Args:
        backup (bool): Whether to create a backup before resetting
        
    Returns:
        tuple: (success, backup_id)
    """
    db_path = get_vscode_path() / "User" / "globalStorage" / "state.vscdb"
    backup_id = None
    
    # Create backup if requested
    if backup and db_path.exists():
        backup_id, _ = backup_state_db()
    
    try:
        # Remove the database file
        if db_path.exists():
            os.remove(db_path)
            logger.info(f"Removed state database")
        
        # Also remove the -journal file if it exists
        journal_path = Path(str(db_path) + "-journal")
        if journal_path.exists():
            os.remove(journal_path)
            logger.info(f"Removed state database journal")
        
        return True, backup_id
    except Exception as e:
        logger.error(f"Failed to reset state database: {e}")
        return False, backup_id

def restore_state_db(backup_id):
    """
    Restore the VSCode state database from a backup.
    
    Args:
        backup_id (str): Backup ID to restore from
        
    Returns:
        bool: True if restore was successful, False otherwise
    """
    from .utils import get_backup_dir
    
    db_path = get_vscode_path() / "User" / "globalStorage" / "state.vscdb"
    backup_path = get_backup_dir() / backup_id / "globalStorage" / "state.vscdb"
    
    if not backup_path.exists():
        logger.error(f"Backup file {backup_path} does not exist")
        return False
    
    return restore_file(backup_path, db_path)

def clean_storage_json():
    """
    Clean the storage.json file which may contain extension tracking data.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    storage_json_path = get_vscode_path() / "User" / "globalStorage" / "storage.json"
    if not storage_json_path.exists():
        logger.warning(f"Storage JSON file not found at {storage_json_path}")
        return False
    
    try:
        # Backup the file first
        backup_file(storage_json_path)
        
        # Read the file
        with open(storage_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Clean extension-related data
        if isinstance(data, dict):
            cleaned_data = {}
            for key, value in data.items():
                # Keep only essential data, remove extension-specific data
                if not any(key.startswith(prefix) for prefix in ["extensionIdentifier", "extensionTracker"]):
                    cleaned_data[key] = value
            
            # Write cleaned data back
            with open(storage_json_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2)
            
            logger.info(f"Cleaned storage.json file")
            return True
        else:
            logger.warning(f"Unexpected format in storage.json")
            return False
    except Exception as e:
        logger.error(f"Failed to clean storage.json: {e}")
        return False
