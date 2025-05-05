"""
Windows-specific implementations for VSCode Extension Resetter.
"""

import os
import winreg
import shutil
from pathlib import Path

from ..core.utils import logger

def get_vscode_registry_keys():
    """
    Get VSCode-related registry keys.
    
    Returns:
        list: List of registry keys
    """
    keys = []
    
    try:
        # Check HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Uninstall
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall") as key:
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            if "Visual Studio Code" in display_name:
                                keys.append((winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\\" + subkey_name))
                        except:
                            pass
                    i += 1
                except WindowsError:
                    break
    except Exception as e:
        logger.error(f"Failed to get VSCode registry keys: {e}")
    
    return keys

def clean_vscode_registry():
    """
    Clean VSCode-related registry entries that might contain tracking information.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    keys = get_vscode_registry_keys()
    success = True
    
    for hkey, key_path in keys:
        try:
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                # Remove tracking-related values
                for value_name in ["InstallDate", "InstallLocation", "InstallTime"]:
                    try:
                        winreg.DeleteValue(key, value_name)
                        logger.info(f"Removed registry value {value_name} from {key_path}")
                    except:
                        pass
        except Exception as e:
            logger.error(f"Failed to clean registry key {key_path}: {e}")
            success = False
    
    return success

def clean_appdata_local():
    """
    Clean VSCode-related files in AppData\Local that might contain tracking information.
    
    Returns:
        bool: True if cleaning was successful, False otherwise
    """
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        logger.error("LOCALAPPDATA environment variable not found")
        return False
    
    paths_to_clean = [
        Path(local_appdata) / "Microsoft" / "VSCode",
        Path(local_appdata) / "VSCode",
        Path(local_appdata) / "Programs" / "Microsoft VS Code"
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
