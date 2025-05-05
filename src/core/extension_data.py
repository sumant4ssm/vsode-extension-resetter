"""
Extension data handling for VSCode Extension Resetter.
"""

import shutil
import sqlite3
from pathlib import Path

from .utils import (
    get_vscode_path,
    get_extensions_path,
    backup_file,
    restore_file,
    logger
)

def get_extension_storage_path(extension_id):
    """
    Get the path to an extension's storage directory.

    Args:
        extension_id (str): Extension ID (publisher.name)

    Returns:
        Path: Path to the extension's storage directory
    """
    extensions_path = get_extensions_path()
    return extensions_path / extension_id

def backup_extension_data(extension_id, backup_id=None):
    """
    Backup an extension's data.

    Args:
        extension_id (str): Extension ID (publisher.name)
        backup_id (str, optional): Backup ID. If None, a new ID will be created.

    Returns:
        tuple: (backup_id, success)
    """
    from .utils import create_backup_id, get_backup_dir

    if backup_id is None:
        backup_id = create_backup_id()

    extension_path = get_extension_storage_path(extension_id)
    if not extension_path.exists():
        logger.warning(f"Extension storage for {extension_id} not found at {extension_path}")
        return backup_id, False

    backup_dir = get_backup_dir() / backup_id / "extensions" / extension_id
    backup_dir.mkdir(exist_ok=True, parents=True)

    try:
        # Copy all files from extension storage to backup
        for item in extension_path.glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to(extension_path)
                backup_item = backup_dir / rel_path
                backup_item.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy2(str(item), str(backup_item))

        logger.info(f"Backed up extension data for {extension_id} to {backup_dir}")
        return backup_id, True
    except Exception as e:
        logger.error(f"Failed to backup extension data for {extension_id}: {e}")
        return backup_id, False

def reset_extension_data(extension_id, backup=True):
    """
    Reset an extension's data.

    Args:
        extension_id (str): Extension ID (publisher.name)
        backup (bool): Whether to create a backup before resetting

    Returns:
        tuple: (success, backup_id)
    """
    extension_path = get_extension_storage_path(extension_id)
    backup_id = None

    # Create backup if requested
    if backup and extension_path.exists():
        backup_id, _ = backup_extension_data(extension_id)

    try:
        # Remove extension storage directory
        if extension_path.exists():
            shutil.rmtree(str(extension_path))
            logger.info(f"Removed extension data for {extension_id}")

        # Also check for extension state in SQLite database
        reset_extension_state_in_db(extension_id)

        return True, backup_id
    except Exception as e:
        logger.error(f"Failed to reset extension data for {extension_id}: {e}")
        return False, backup_id

def reset_extension_state_in_db(extension_id):
    """
    Reset an extension's state in the VSCode SQLite database.

    Args:
        extension_id (str): Extension ID (publisher.name)

    Returns:
        bool: True if reset was successful, False otherwise
    """
    db_path = get_vscode_path() / "User" / "globalStorage" / "state.vscdb"
    if not db_path.exists():
        logger.warning(f"VSCode state database not found at {db_path}")
        return False

    try:
        # Backup the database first
        backup_file(db_path)

        # Connect to the database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Find and delete extension-related entries
        cursor.execute("SELECT key FROM ItemTable WHERE key LIKE ?", (f"%{extension_id}%",))
        keys = cursor.fetchall()

        if keys:
            for key in keys:
                cursor.execute("DELETE FROM ItemTable WHERE key = ?", (key[0],))

            conn.commit()
            logger.info(f"Removed {len(keys)} entries for {extension_id} from state database")
        else:
            logger.info(f"No entries found for {extension_id} in state database")

        conn.close()
        return True
    except Exception as e:
        logger.error(f"Failed to reset extension state in database for {extension_id}: {e}")
        return False

def restore_extension_data(extension_id, backup_id):
    """
    Restore an extension's data from a backup.

    Args:
        extension_id (str): Extension ID (publisher.name)
        backup_id (str): Backup ID to restore from

    Returns:
        bool: True if restore was successful, False otherwise
    """
    from .utils import get_backup_dir

    extension_path = get_extension_storage_path(extension_id)
    backup_dir = get_backup_dir() / backup_id / "extensions" / extension_id

    if not backup_dir.exists():
        logger.error(f"Backup directory {backup_dir} does not exist")
        return False

    try:
        # Remove existing extension data
        if extension_path.exists():
            shutil.rmtree(str(extension_path))

        # Create extension directory
        extension_path.mkdir(exist_ok=True, parents=True)

        # Copy all files from backup to extension storage
        for item in backup_dir.glob("**/*"):
            if item.is_file():
                rel_path = item.relative_to(backup_dir)
                restore_item = extension_path / rel_path
                restore_item.parent.mkdir(exist_ok=True, parents=True)
                shutil.copy2(str(item), str(restore_item))

        logger.info(f"Restored extension data for {extension_id} from {backup_dir}")
        return True
    except Exception as e:
        logger.error(f"Failed to restore extension data for {extension_id}: {e}")
        return False

def _get_possible_storage_paths():
    """
    Get a list of possible extension storage paths.

    Returns:
        list: List of possible storage paths
    """
    # Try standard and insiders paths
    possible_paths = [
        get_extensions_path(),  # Standard globalStorage
        get_vscode_path() / "User" / "workspaceStorage",  # Standard workspaceStorage
        get_vscode_path(use_insiders=True) / "User" / "globalStorage",  # Insiders globalStorage
        get_vscode_path(use_insiders=True) / "User" / "workspaceStorage",  # Insiders workspaceStorage
    ]

    return possible_paths

def list_extension_data():
    """
    List all extensions with data in the global storage.

    Returns:
        list: List of extension IDs with data
    """
    extension_dirs = []

    # Try each path
    for path in _get_possible_storage_paths():
        if path.exists():
            logger.info(f"Found extension data directory at {path}")
            extension_dirs.extend([d.name for d in path.iterdir() if d.is_dir()])

    if not extension_dirs:
        logger.warning("No extension data found in any of the possible directories.")

    return extension_dirs
