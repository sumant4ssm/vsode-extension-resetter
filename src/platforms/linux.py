"""
Linux-specific implementations for VSCode Extension Resetter.
"""

import os
import shutil
import subprocess
from pathlib import Path

from ..core.utils import logger

def get_vscode_config_paths():
    """
    Get paths to VSCode configuration directories on Linux.
    
    Returns:
        list: List of configuration directory paths
    """
    home = Path.home()
    paths = [
        home / ".config" / "Code",
        home / ".vscode"
    ]
    
    return [p for p in paths if p.exists()]

def clean_vscode_config():
    """
    Clean VSCode configuration directories that might contain tracking information.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    config_paths = get_vscode_config_paths()
    success = True
    
    for path in config_paths:
        if path.exists():
            try:
                # Don't delete the entire directory, just clean specific files
                for item in path.glob("**/machineid"):
                    try:
                        os.remove(item)
                        logger.info(f"Removed {item}")
                    except Exception as e:
                        logger.error(f"Failed to remove {item}: {e}")
                        success = False
            except Exception as e:
                logger.error(f"Failed to clean {path}: {e}")
                success = False
    
    return success

def clean_dconf_settings():
    """
    Clean VSCode-related dconf settings that might contain tracking information.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    try:
        # Check if dconf is available
        result = subprocess.run(["which", "dconf"], capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning("dconf not found, skipping dconf settings cleaning")
            return True
        
        # Check for VSCode-related dconf settings
        result = subprocess.run(["dconf", "list", "/org/gnome/"], capture_output=True, text=True)
        if "vscode/" in result.stdout:
            # Reset VSCode-related dconf settings
            subprocess.run(["dconf", "reset", "-f", "/org/gnome/vscode/"])
            logger.info("Reset VSCode-related dconf settings")
        
        return True
    except Exception as e:
        logger.error(f"Failed to clean dconf settings: {e}")
        return False
