# Building and Distributing VSCode Extension Resetter

This document provides instructions for building and distributing the VSCode Extension Resetter in various formats.

## Prerequisites

Before building the application, make sure you have the following installed:

- Python 3.6 or higher
- pip (Python package installer)
- Git (for version control)

## Setup Development Environment

1. Clone the repository (if you haven't already):
   ```bash
   git clone https://github.com/sumant4ssm/vsode-extension-resetter.git
   cd vsode-extension-resetter
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install build twine pyinstaller
   ```

## Distribution Methods

You can distribute VSCode Extension Resetter in several ways:

1. **Python Package (PyPI)**: For Python users who want to install via pip
2. **Standalone Executables**: For end-users who don't have Python installed
3. **Source Code**: For developers who want to modify the code

## 1. Building a Python Package

### Update Package Information

Before building, make sure to update the package information in `setup.py`:

```python
setup(
    name="vscode-extension-resetter",
    version=version,
    description="A tool to completely remove extension tracking in Visual Studio Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",  # Update with your name
    author_email="your.email@example.com",  # Update with your email
    url="https://github.com/sumant4ssm/vsode-extension-resetter",  # Update with your repository URL
    # ... rest of the setup configuration
)
```

### Create a MANIFEST.in File

Create a `MANIFEST.in` file in the root directory to include non-Python files:

```
include LICENSE
include README.md
include requirements.txt
include icon.py
recursive-include docs *
```

### Build the Package

1. Build the distribution packages:
   ```bash
   python -m build
   ```

   This will create both source distribution (`.tar.gz`) and wheel (`.whl`) files in the `dist/` directory.

2. Test the package locally (optional):
   ```bash
   pip install dist/vscode_extension_resetter-0.1.0-py3-none-any.whl
   ```

### Upload to PyPI

1. Register an account on [PyPI](https://pypi.org/) if you don't have one.

2. Upload the package to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

   You'll be prompted for your PyPI username and password.

3. After uploading, users can install your package with:
   ```bash
   pip install vscode-extension-resetter
   ```

## 2. Building Standalone Executables with PyInstaller

PyInstaller can create standalone executables for Windows, macOS, and Linux.

### Create a PyInstaller Spec File

Create a file named `vscode_resetter.spec` in the root directory:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_gui.py'],  # Main script to execute
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add icon and README files
a.datas += [('icon.png', 'icon.png', 'DATA')]
a.datas += [('icon.ico', 'icon.ico', 'DATA')]
a.datas += [('README.md', 'README.md', 'DATA')]
a.datas += [('LICENSE', 'LICENSE', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VSCodeExtensionResetter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for CLI version
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Icon for the executable
)
```

### Generate Icons

Before building, generate the icon files:

```bash
python icon.py
```

### Build the Executable

1. Build the GUI version:
   ```bash
   pyinstaller --clean vscode_resetter.spec
   ```

2. Build the CLI version (optional):
   ```bash
   pyinstaller --clean --onefile --console run_cli.py --name VSCodeExtensionResetterCLI
   ```

The executables will be created in the `dist/` directory.

### Creating Installers (Optional)

For a more professional distribution, you can create installers:

- **Windows**: Use [NSIS](https://nsis.sourceforge.io/) or [Inno Setup](https://jrsoftware.org/isinfo.php)
- **macOS**: Create a DMG file using [create-dmg](https://github.com/sindresorhus/create-dmg)
- **Linux**: Create DEB or RPM packages using [fpm](https://github.com/jordansissel/fpm)

## 3. Distributing Source Code

For open-source distribution, you can simply share your GitHub repository URL:

```
https://github.com/sumant4ssm/vsode-extension-resetter
```

Make sure your repository includes:

- Clear installation instructions in the README.md
- License information
- Contributing guidelines

## Release Process

When releasing a new version:

1. Update the version number in `src/__init__.py`
2. Update the CHANGELOG.md (if you have one)
3. Create a new tag in Git:
   ```bash
   git tag -a v0.1.0 -m "Version 0.1.0"
   git push origin v0.1.0
   ```
4. Build and upload the new package to PyPI
5. Create a new release on GitHub with release notes
6. Attach the built executables to the GitHub release

## Continuous Integration (Optional)

Consider setting up GitHub Actions to automate the build and release process. Create a `.github/workflows/build.yml` file to:

1. Run tests
2. Build packages for different platforms
3. Upload artifacts to GitHub releases

## Distribution Checklist

Before distributing, ensure:

- [ ] All tests pass
- [ ] Version number is updated
- [ ] Documentation is up-to-date
- [ ] License file is included
- [ ] README contains clear installation and usage instructions
- [ ] Icons and other assets are included
- [ ] The application works on all supported platforms
