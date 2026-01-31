# Contributing to FileBrowser Monitor

Thank you for considering contributing to FileBrowser Monitor! All contributions are welcome.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps that reproduce the problem**
* **Provide specific examples to demonstrate those steps**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include your FileBrowser version and configuration**
* **Include your Python version and OS**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python PEP 8 style guide
* Include appropriate test cases if applicable
* Document new code with docstrings
* Add entry to the relevant section of CHANGELOG if applicable

## Development Setup

1. Fork the repository
2. Clone your fork
3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
6. Make your changes
7. Test your changes:
   ```bash
   python monitor.py --once
   ```
8. Commit your changes:
   ```bash
   git commit -am 'Add some feature'
   ```
9. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
10. Create a Pull Request

## Styleguides

### Python Code

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use meaningful variable names
* Add docstrings to all functions
* Keep functions focused and testable

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Documentation

* Use Markdown
* Include code examples where appropriate
* Keep README.md up to date

## Code of Conduct

### Our Pledge

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

### Our Standards

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing opinions, viewpoints, and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a professional setting

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help organize and categorize issues and pull requests.

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

## Questions?

Feel free to open an issue labeled `question` if you have any questions!

Thanks for contributing! 🎉
