"""
Command-line interface for VSCode Extension Resetter.
"""

import os
import sys
import click
import inquirer
from pathlib import Path

from ..core.utils import (
    get_platform,
    get_extension_list,
    list_backups,
    logger
)
from ..core.machine_id import (
    get_current_machine_id,
    reset_machine_id,
    restore_machine_id
)
from ..core.extension_data import (
    list_extension_data,
    reset_extension_data,
    restore_extension_data
)
from ..core.storage_cleaner import (
    backup_global_storage,
    clean_global_storage,
    backup_state_db,
    reset_state_db,
    restore_state_db,
    clean_storage_json
)

# Import platform-specific modules
if get_platform() == "windows":
    from ..platforms.windows import clean_vscode_registry, clean_appdata_local
elif get_platform() == "macos":
    from ..platforms.macos import clean_vscode_plist, clean_application_support
else:  # linux
    from ..platforms.linux import clean_vscode_config, clean_dconf_settings

@click.group()
def cli():
    """VSCode Extension Resetter - Remove extension tracking completely."""
    pass

@cli.command("info")
def info():
    """Show information about the current VSCode installation."""
    click.echo("VSCode Extension Resetter")
    click.echo("------------------------")
    click.echo(f"Platform: {get_platform()}")
    
    machine_id = get_current_machine_id()
    click.echo(f"Machine ID: {machine_id or 'Not found'}")
    
    extensions = get_extension_list()
    click.echo(f"Installed extensions: {len(extensions)}")
    
    extension_data = list_extension_data()
    click.echo(f"Extensions with data: {len(extension_data)}")
    
    backups = list_backups()
    click.echo(f"Available backups: {len(backups)}")

@cli.command("reset-machine-id")
@click.option("--no-backup", is_flag=True, help="Don't create a backup before resetting")
def reset_machine_id_cmd(no_backup):
    """Reset the VSCode machine ID."""
    success, backup_id, old_id, new_id = reset_machine_id(backup=not no_backup)
    
    if success:
        click.echo(f"Machine ID reset successfully!")
        click.echo(f"Old ID: {old_id or 'Not found'}")
        click.echo(f"New ID: {new_id}")
        if backup_id:
            click.echo(f"Backup created with ID: {backup_id}")
    else:
        click.echo("Failed to reset machine ID.")

@cli.command("list-extensions")
def list_extensions_cmd():
    """List installed VSCode extensions."""
    extensions = get_extension_list()
    
    if not extensions:
        click.echo("No extensions found.")
        return
    
    click.echo(f"Found {len(extensions)} installed extensions:")
    for i, ext in enumerate(extensions, 1):
        click.echo(f"{i}. {ext['name']} ({ext['id']}) - v{ext['version']}")

@cli.command("list-extension-data")
def list_extension_data_cmd():
    """List extensions with data in the global storage."""
    extension_data = list_extension_data()
    
    if not extension_data:
        click.echo("No extension data found.")
        return
    
    click.echo(f"Found {len(extension_data)} extensions with data:")
    for i, ext_id in enumerate(extension_data, 1):
        click.echo(f"{i}. {ext_id}")

@cli.command("reset-extension")
@click.argument("extension_id", required=False)
@click.option("--no-backup", is_flag=True, help="Don't create a backup before resetting")
def reset_extension_cmd(extension_id, no_backup):
    """Reset a specific extension's data."""
    if not extension_id:
        # Interactive mode: let the user select an extension
        extension_data = list_extension_data()
        
        if not extension_data:
            click.echo("No extension data found.")
            return
        
        questions = [
            inquirer.List(
                "extension_id",
                message="Select an extension to reset",
                choices=extension_data
            )
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        extension_id = answers["extension_id"]
    
    success, backup_id = reset_extension_data(extension_id, backup=not no_backup)
    
    if success:
        click.echo(f"Extension data for {extension_id} reset successfully!")
        if backup_id:
            click.echo(f"Backup created with ID: {backup_id}")
    else:
        click.echo(f"Failed to reset extension data for {extension_id}.")

@cli.command("reset-all-extensions")
@click.option("--no-backup", is_flag=True, help="Don't create a backup before resetting")
@click.option("--force", is_flag=True, help="Don't ask for confirmation")
def reset_all_extensions_cmd(no_backup, force):
    """Reset data for all extensions."""
    extension_data = list_extension_data()
    
    if not extension_data:
        click.echo("No extension data found.")
        return
    
    if not force:
        click.echo(f"This will reset data for {len(extension_data)} extensions:")
        for i, ext_id in enumerate(extension_data, 1):
            click.echo(f"{i}. {ext_id}")
        
        if not click.confirm("Do you want to continue?"):
            return
    
    backup_id = None
    if not no_backup:
        backup_id, _ = backup_global_storage()
        if backup_id:
            click.echo(f"Backup created with ID: {backup_id}")
    
    success_count = 0
    for ext_id in extension_data:
        success, _ = reset_extension_data(ext_id, backup=False)  # Already backed up
        if success:
            success_count += 1
    
    click.echo(f"Reset data for {success_count}/{len(extension_data)} extensions.")

@cli.command("backup")
@click.option("--include-extensions", is_flag=True, help="Include extension data in the backup")
def backup_cmd(include_extensions):
    """Create a backup of VSCode configuration."""
    from ..core.utils import create_backup_id
    
    backup_id = create_backup_id()
    
    # Backup machine ID
    machine_id_path = Path(get_current_machine_id())
    if machine_id_path.exists():
        from ..core.utils import backup_file
        _, backup_path = backup_file(machine_id_path, backup_id)
        if backup_path:
            click.echo(f"Backed up machine ID to {backup_path}")
    
    # Backup global storage
    _, success = backup_global_storage(backup_id)
    if success:
        click.echo("Backed up global storage")
    
    # Backup state database
    _, success = backup_state_db(backup_id)
    if success:
        click.echo("Backed up state database")
    
    # Backup extension data
    if include_extensions:
        extension_data = list_extension_data()
        for ext_id in extension_data:
            _, success = backup_extension_data(ext_id, backup_id)
            if success:
                click.echo(f"Backed up extension data for {ext_id}")
    
    click.echo(f"Backup created with ID: {backup_id}")

@cli.command("list-backups")
def list_backups_cmd():
    """List available backups."""
    backups = list_backups()
    
    if not backups:
        click.echo("No backups found.")
        return
    
    click.echo(f"Found {len(backups)} backups:")
    for i, backup_id in enumerate(backups, 1):
        click.echo(f"{i}. {backup_id}")

@cli.command("restore")
@click.argument("backup_id", required=False)
def restore_cmd(backup_id):
    """Restore from a backup."""
    if not backup_id:
        # Interactive mode: let the user select a backup
        backups = list_backups()
        
        if not backups:
            click.echo("No backups found.")
            return
        
        questions = [
            inquirer.List(
                "backup_id",
                message="Select a backup to restore",
                choices=backups
            )
        ]
        answers = inquirer.prompt(questions)
        
        if not answers:
            return
        
        backup_id = answers["backup_id"]
    
    # Restore machine ID
    success = restore_machine_id(backup_id)
    if success:
        click.echo("Restored machine ID")
    
    # Restore state database
    success = restore_state_db(backup_id)
    if success:
        click.echo("Restored state database")
    
    # Restore extension data
    from ..core.utils import get_backup_dir
    backup_dir = get_backup_dir() / backup_id / "extensions"
    if backup_dir.exists():
        extension_data = [d.name for d in backup_dir.iterdir() if d.is_dir()]
        for ext_id in extension_data:
            success = restore_extension_data(ext_id, backup_id)
            if success:
                click.echo(f"Restored extension data for {ext_id}")
    
    click.echo(f"Restore from backup {backup_id} completed.")

@cli.command("clean-all")
@click.option("--no-backup", is_flag=True, help="Don't create a backup before cleaning")
@click.option("--force", is_flag=True, help="Don't ask for confirmation")
def clean_all_cmd(no_backup, force):
    """Clean all VSCode tracking data."""
    if not force:
        click.echo("This will clean all VSCode tracking data, including:")
        click.echo("- Machine ID")
        click.echo("- Extension data")
        click.echo("- Global storage")
        click.echo("- State database")
        
        if get_platform() == "windows":
            click.echo("- Registry entries")
            click.echo("- AppData\\Local files")
        elif get_platform() == "macos":
            click.echo("- Plist files")
            click.echo("- Application Support files")
        else:  # linux
            click.echo("- Config files")
            click.echo("- dconf settings")
        
        if not click.confirm("Do you want to continue?"):
            return
    
    backup_id = None
    if not no_backup:
        from ..core.utils import create_backup_id
        backup_id = create_backup_id()
        
        # Backup machine ID
        machine_id_path = Path(get_current_machine_id())
        if machine_id_path.exists():
            from ..core.utils import backup_file
            _, backup_path = backup_file(machine_id_path, backup_id)
            if backup_path:
                click.echo(f"Backed up machine ID")
        
        # Backup global storage
        _, success = backup_global_storage(backup_id)
        if success:
            click.echo("Backed up global storage")
        
        # Backup state database
        _, success = backup_state_db(backup_id)
        if success:
            click.echo("Backed up state database")
        
        click.echo(f"Backup created with ID: {backup_id}")
    
    # Reset machine ID
    success, _, _, _ = reset_machine_id(backup=False)  # Already backed up
    if success:
        click.echo("Reset machine ID")
    
    # Clean global storage
    success, _ = clean_global_storage(backup=False)  # Already backed up
    if success:
        click.echo("Cleaned global storage")
    
    # Reset state database
    success, _ = reset_state_db(backup=False)  # Already backed up
    if success:
        click.echo("Reset state database")
    
    # Clean storage.json
    success = clean_storage_json()
    if success:
        click.echo("Cleaned storage.json")
    
    # Platform-specific cleaning
    if get_platform() == "windows":
        success = clean_vscode_registry()
        if success:
            click.echo("Cleaned registry entries")
        
        success = clean_appdata_local()
        if success:
            click.echo("Cleaned AppData\\Local files")
    elif get_platform() == "macos":
        success = clean_vscode_plist()
        if success:
            click.echo("Cleaned plist files")
        
        success = clean_application_support()
        if success:
            click.echo("Cleaned Application Support files")
    else:  # linux
        success = clean_vscode_config()
        if success:
            click.echo("Cleaned config files")
        
        success = clean_dconf_settings()
        if success:
            click.echo("Cleaned dconf settings")
    
    click.echo("Cleaning completed.")

def main():
    """Entry point for the command-line interface."""
    cli()

if __name__ == "__main__":
    main()
