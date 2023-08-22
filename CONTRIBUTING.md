# Contribution Guide for Infr

First off, thank you for considering contributing to Infr! 🎉 Every contribution, from code to documentation, is invaluable to us.

## Getting Started

### Setting Up Your Development Environment

1. **Fork & Clone**: 
   
   Start by forking the repository. Once done, you can clone your fork:

   ```
   git clone https://github.com/<your_username>/server.git
   cd server
   ```

2. **Prerequisites**:

   Ensure you have the following software installed:

   - [Python 3.8 or above](https://www.python.org/downloads/)
   - [NodeJS 14 or above](https://nodejs.org/en/download/)
   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

3. **Setting up Pre-Commit**:

   We use `pre-commit` to ensure code quality and consistency. Install it and set up the hooks:

   ```
   pip install pre-commit
   pre-commit install
   ```

### Coding Standards

- **Python Code**: 
  - We adhere to the PEP 8 style guide. Use tools like `flake8` and `autopep8` to check and format your code, respectively.
  - When in doubt, refer to existing code for guidance on style and organization.

- **Commit Messages**:
  - Write concise yet descriptive commit messages. This helps maintainers and other contributors understand the history and intention of your changes.

### Making Changes

1. Create a branch for your changes:

   ```
   git checkout -b <branch_name>
   ```

2. Make and commit your changes. Remember to regularly pull from the main repository's `main` (or `master`) branch to keep your fork up-to-date.

3. Before pushing, ensure you run:

   ```
   pre-commit run --all-files
   ```

   This will ensure all checks and formatting tools run on your code.

### Submitting Your Changes

1. Push your changes to your fork on GitHub.
   
2. Open a Pull Request (PR) against the main repository. Make sure to provide a detailed description of your changes.

3. Wait for the maintainers to review. Address any comments or requested changes promptly.

## Community

- If you have questions or need help, join us on [Discord](https://discord.gg/ZAejZCzaPe).
- For major features or significant changes, consider discussing them first on Discord or by opening an issue on GitHub.

## Conclusion

Your contributions are a significant part of the open-source community and the evolution of Infr. We appreciate the time and effort you put in and look forward to building amazing things together!
