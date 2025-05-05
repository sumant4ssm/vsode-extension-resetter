# VSCode Extension Resetter Documentation

## Project Summary

VSCode Extension Resetter is a tool designed to completely remove extension tracking in Visual Studio Code, even after uninstallation. It provides both command-line and graphical interfaces to:

- Reset VSCode's machine ID to prevent extension tracking
- Clean extension-specific data from global storage
- Create backups before making changes
- Restore from backups if needed
- Support all major platforms (Windows, macOS, and Linux)

The tool is particularly useful for developers who want to ensure that no tracking data remains after uninstalling extensions, or for those who want to reset extension trials.

## Project Structure

```
vsode-extension-resetter/
├── docs/                       # Documentation
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── machine_id.py       # Machine ID handling
│   │   ├── extension_data.py   # Extension data handling
│   │   ├── storage_cleaner.py  # Global storage cleaning
│   │   └── utils.py            # Utility functions
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── windows.py          # Windows-specific code
│   │   ├── macos.py            # macOS-specific code
│   │   └── linux.py            # Linux-specific code
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── cli.py              # Command-line interface
│   │   └── gui.py              # Graphical user interface
│   ├── __init__.py
│   └── __main__.py
├── tests/                      # Unit tests
├── icon.py                     # Icon generator
├── run_cli.py                  # Script to run CLI
├── run_gui.py                  # Script to run GUI
├── setup.py                    # Package setup
├── requirements.txt            # Dependencies
├── README.md                   # Project documentation
├── LICENSE                     # License file
└── .gitignore                  # Git ignore file
```

## How to Use

### Install Dependencies

Before using the VSCode Extension Resetter, you need to install the required dependencies:

```bash
pip install -r requirements.txt
```

### Generate Icons (Optional)

You can generate application icons using the included script:

```bash
python icon.py
```

This will create `icon.png` and `icon.ico` files that the application will use if available.

### Command Line Interface

The command-line interface provides various commands to manage VSCode extension tracking:

```bash
# Show information about the current VSCode installation
python run_cli.py info

# Reset machine ID
python run_cli.py reset-machine-id

# List installed extensions
python run_cli.py list-extensions

# List extensions with data in the global storage
python run_cli.py list-extension-data

# Reset a specific extension's data
python run_cli.py reset-extension <extension-id>

# Reset data for all extensions
python run_cli.py reset-all-extensions

# Create a backup
python run_cli.py backup

# List available backups
python run_cli.py list-backups

# Restore from a backup
python run_cli.py restore <backup-id>

# Clean all VSCode tracking data
python run_cli.py clean-all
```

### Graphical User Interface

The graphical user interface provides a more user-friendly way to manage VSCode extension tracking:

```bash
python run_gui.py
```

The GUI has five tabs:

1. **Info**: Shows information about the current VSCode installation
2. **Machine ID**: Allows resetting the machine ID
3. **Extensions**: Lists extensions with data and allows resetting them
4. **Backup/Restore**: Allows creating backups and restoring from them
5. **Clean All**: Cleans all VSCode tracking data

## Platform Support

The tool supports all major platforms:

- **Windows**: Handles registry entries and AppData files
- **macOS**: Handles plist files and Application Support
- **Linux**: Handles config files and dconf settings

## Troubleshooting

If you encounter any issues:

1. Check the log output for error messages
2. Make sure VSCode is closed before running the tool
3. Run the tool with administrator/root privileges if needed
4. Create a backup before making changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.
