"""
macOS-specific implementations for VSCode Extension Resetter.
"""

import os
import plistlib
import shutil
from pathlib import Path

from ..core.utils import logger

def get_vscode_plist_paths():
    """
    Get paths to VSCode-related plist files.
    
    Returns:
        list: List of plist file paths
    """
    home = Path.home()
    paths = [
        home / "Library" / "Preferences" / "com.microsoft.VSCode.plist",
        home / "Library" / "Caches" / "com.microsoft.VSCode"
    ]
    
    return [p for p in paths if p.exists()]

def clean_vscode_plist():
    """
    Clean VSCode-related plist files that might contain tracking information.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    plist_paths = get_vscode_plist_paths()
    success = True
    
    for path in plist_paths:
        if path.is_file() and path.suffix == ".plist":
            try:
                # Read plist file
                with open(path, 'rb') as f:
                    data = plistlib.load(f)
                
                # Remove tracking-related keys
                tracking_keys = [
                    "NSNavLastRootDirectory",
                    "NSNavLastCurrentDirectory",
                    "NSNavPanelExpandedSizeForOpenMode",
                    "NSNavPanelExpandedSizeForSaveMode"
                ]
                
                modified = False
                for key in tracking_keys:
                    if key in data:
                        del data[key]
                        modified = True
                
                if modified:
                    # Write modified plist file
                    with open(path, 'wb') as f:
                        plistlib.dump(data, f)
                    
                    logger.info(f"Cleaned plist file {path}")
            except Exception as e:
                logger.error(f"Failed to clean plist file {path}: {e}")
                success = False
        elif path.is_dir():
            try:
                # Clean cache directory
                for item in path.glob("**/machineid"):
                    try:
                        os.remove(item)
                        logger.info(f"Removed {item}")
                    except Exception as e:
                        logger.error(f"Failed to remove {item}: {e}")
                        success = False
            except Exception as e:
                logger.error(f"Failed to clean directory {path}: {e}")
                success = False
    
    return success

def clean_application_support():
    """
    Clean VSCode-related files in Application Support that might contain tracking information.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    home = Path.home()
    paths_to_clean = [
        home / "Library" / "Application Support" / "Code",
        home / "Library" / "Application Support" / "Visual Studio Code"
    ]
    
    success = True
    for path in paths_to_clean:
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
