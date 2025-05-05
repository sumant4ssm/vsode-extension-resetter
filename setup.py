"""
Setup script for VSCode Extension Resetter.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

# Get version from src/__init__.py
with open(os.path.join("src", "__init__.py"), "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="vscode-extension-resetter",
    version=version,
    description="A tool to completely remove extension tracking in Visual Studio Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/vscode-extension-resetter",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vscode-resetter=src.ui.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
)
