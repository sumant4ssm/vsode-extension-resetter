# Contributing to VSCode Extension Resetter

Thank you for your interest in contributing to VSCode Extension Resetter! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Screenshots (if applicable)
6. Your operating system and VSCode version
7. Any additional context

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:

1. A clear, descriptive title
2. A detailed description of the proposed feature
3. Any relevant examples or mockups
4. Why this feature would be useful to most users

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Include comments in your code where necessary
- Update documentation if needed
- Add tests for new features if applicable
- Make sure all tests pass before submitting

## Development Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/vscode-extension-resetter.git
   cd vscode-extension-resetter
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application
   ```bash
   python run_gui.py  # For GUI
   python run_cli.py  # For CLI
   ```

## Project Structure

- `src/core/`: Core functionality
- `src/platforms/`: Platform-specific code
- `src/ui/`: User interfaces (CLI and GUI)
- `docs/`: Documentation
- `tests/`: Test cases

## License

By contributing to VSCode Extension Resetter, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
