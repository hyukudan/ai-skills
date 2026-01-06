# Contributing, to Ai Skills

First off, thank you for considering contributing to **Ai Skills**! It's people like you that make this tool faster, easier, and more powerful for everyone.

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs
This section guides you through submitting a bug report.
- **Use the GitHub Issues search** — check if the issue has already been reported.
- **Check if the issue has been fixed** — try to reproduce it using the latest `main` or development branch in the repository.
- **Isolate the problem** — ideally create a reduced test case.

### 💡 Suggesting Enhancements
This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.
- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as much detail as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why.

### 💻 Pull Requests
The process is straightforward:
1.  Fork the repo and create your branch from `main`.
2.  If you've added code that should be tested, add tests.
3.  If you've changed APIs, update the documentation.
4.  Ensure the test suite passes.
5.  Make sure your code lints.
6.  Issue that pull request!

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/ai-skills.git
cd ai-skills

# Set up environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[all,dev]"

# Run tests
pytest
```

## 🎨 Style Guide
-   **Python:** We use `black` for formatting and `ruff` for linting.
-   **Commits:** Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: add new search filter`, `fix: resolve crash on startup`).

## 📜 License
By contributing, you agree that your contributions will be licensed under its AGPL-3.0 License.
