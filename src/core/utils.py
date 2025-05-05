"""
Utility functions for VSCode Extension Resetter.
"""

import os
import sys
import platform
import json
import shutil
import uuid
import logging
from datetime import datetime
from pathlib import Path

# Constants
VSCODE_STANDARD = "Code"
VSCODE_INSIDERS = "Code - Insiders"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("vscode_resetter")

def get_platform():
    """
    Determine the current operating system.

    Returns:
        str: 'windows', 'macos', or 'linux'
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"

def get_vscode_path(use_insiders=False):
    """
    Get the path to VSCode installation based on the platform.

    Args:
        use_insiders (bool): Whether to use VSCode Insiders paths

    Returns:
        Path: Path to VSCode installation directory
    """
    platform_name = get_platform()
    home = Path.home()

    code_dir = VSCODE_INSIDERS if use_insiders else VSCODE_STANDARD

    if platform_name == "windows":
        return Path(os.environ.get("APPDATA")) / code_dir
    elif platform_name == "macos":
        return home / "Library" / "Application Support" / code_dir
    else:  # linux
        return home / ".config" / code_dir

def get_machine_id_path():
    """
    Get the path to the VSCode machine ID file.

    Returns:
        Path: Path to the machine ID file
    """
    return get_vscode_path() / "machineId"

def get_extensions_path():
    """
    Get the path to the VSCode extensions directory.

    Returns:
        Path: Path to the extensions directory
    """
    return get_vscode_path() / "User" / "globalStorage"

def get_backup_dir():
    """
    Get the directory for storing backups.

    Returns:
        Path: Path to the backup directory
    """
    backup_dir = get_vscode_path() / "resetter_backups"
    backup_dir.mkdir(exist_ok=True, parents=True)
    return backup_dir

def create_backup_id():
    """
    Create a unique backup ID based on the current timestamp.

    Returns:
        str: Unique backup ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"backup_{timestamp}"

def backup_file(file_path, backup_id=None):
    """
    Create a backup of a file.

    Args:
        file_path (Path): Path to the file to backup
        backup_id (str, optional): Backup ID. If None, a new ID will be created.

    Returns:
        tuple: (backup_id, backup_path) or (None, None) if backup failed
    """
    if not file_path.exists():
        logger.warning(f"File {file_path} does not exist, cannot backup.")
        return None, None

    if backup_id is None:
        backup_id = create_backup_id()

    backup_dir = get_backup_dir() / backup_id
    backup_dir.mkdir(exist_ok=True, parents=True)

    # Create relative path structure in backup
    rel_path = file_path.relative_to(get_vscode_path()) if file_path.is_relative_to(get_vscode_path()) else Path(file_path.name)
    backup_path = backup_dir / rel_path

    # Create parent directories if they don't exist
    backup_path.parent.mkdir(exist_ok=True, parents=True)

    try:
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up {file_path} to {backup_path}")
        return backup_id, backup_path
    except Exception as e:
        logger.error(f"Failed to backup {file_path}: {e}")
        return None, None

def restore_file(backup_path, original_path):
    """
    Restore a file from backup.

    Args:
        backup_path (Path): Path to the backup file
        original_path (Path): Path to restore the file to

    Returns:
        bool: True if restore was successful, False otherwise
    """
    if not backup_path.exists():
        logger.warning(f"Backup file {backup_path} does not exist, cannot restore.")
        return False

    try:
        # Create parent directories if they don't exist
        original_path.parent.mkdir(exist_ok=True, parents=True)

        shutil.copy2(backup_path, original_path)
        logger.info(f"Restored {original_path} from {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to restore {original_path}: {e}")
        return False

def list_backups():
    """
    List all available backups.

    Returns:
        list: List of backup IDs
    """
    backup_dir = get_backup_dir()
    if not backup_dir.exists():
        return []

    return [d.name for d in backup_dir.iterdir() if d.is_dir()]

def _get_possible_extension_paths():
    """
    Get a list of possible extension paths.

    Returns:
        list: List of possible extension paths
    """
    possible_paths = [
        get_vscode_path() / "extensions",  # Standard path
        get_vscode_path(use_insiders=True) / "extensions",  # Insiders path
        Path(os.environ.get("USERPROFILE", "")) / ".vscode" / "extensions",  # User profile path
    ]

    # Add local installation paths
    if get_platform() == "windows":
        possible_paths.extend([
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "resources" / "app" / "extensions",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code Insiders" / "resources" / "app" / "extensions"
        ])

    return possible_paths

def _parse_extension_package_json(package_json):
    """
    Parse an extension's package.json file.

    Args:
        package_json (Path): Path to the package.json file

    Returns:
        dict: Extension information or None if parsing failed
    """
    if not package_json.exists():
        return None

    try:
        with open(package_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "name" in data and "publisher" in data:
                ext_id = f"{data['publisher']}.{data['name']}"
                return {
                    "id": ext_id,
                    "name": data.get("displayName", data["name"]),
                    "version": data.get("version", "unknown"),
                    "path": str(package_json.parent)
                }
    except Exception as e:
        logger.error(f"Failed to parse {package_json}: {e}")

    return None

def get_extension_list():
    """
    Get a list of installed VSCode extensions.

    Returns:
        list: List of extension IDs
    """
    extensions = []

    # Try each possible path
    for extensions_path in _get_possible_extension_paths():
        if not extensions_path.exists():
            continue

        logger.info(f"Found extensions directory at {extensions_path}")

        # Process each extension directory
        for ext_dir in extensions_path.glob("*"):
            if not ext_dir.is_dir():
                continue

            package_json = ext_dir / "package.json"
            ext_info = _parse_extension_package_json(package_json)

            if ext_info and ext_info not in extensions:
                extensions.append(ext_info)

    if not extensions:
        logger.warning("No extensions found in any of the possible directories.")

    return extensions

def generate_new_machine_id():
    """
    Generate a new random machine ID.

    Returns:
        str: New machine ID
    """
    return str(uuid.uuid4())
