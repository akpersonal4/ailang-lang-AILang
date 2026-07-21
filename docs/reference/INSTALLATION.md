# Installation Guide

## Prerequisites

- **Python**: 3.11 or later
- **pip** (Python package installer)
- **git** (for cloning the repository)

Optional but recommended:
- **uv** — fast Python package installer and resolver (alternative to pip)

## Quick Install (all platforms)

```bash
# Clone the repository
git clone https://github.com/akpersonal4/ailang-lang-AILang.git
cd ailang-lang-AILang

# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Install AILang and development tools
pip install -e .
pip install pytest black ruff mypy

# Verify installation
ail --help
```

## Platform-Specific Instructions

### Windows

1. Install Python 3.11+ from [python.org](https://python.org) or the Microsoft Store.
2. Ensure `python` and `pip` are in your PATH.
3. Use PowerShell (recommended) or Command Prompt.

PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

If you encounter execution policy restrictions:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### macOS

```bash
# Using Homebrew
brew install python@3.11 git
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Using uv (alternative — faster)

```bash
pip install uv
uv venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
uv pip install -e .
uv pip install pytest black ruff mypy
```

## Running Your First Program

Create a file named `hello.ail`:

```ail
fn main() {
    print("Hello, AILang!");
    return 0
}
```

Run it:

```bash
ail hello.ail
```

Expected output:
```
Hello, AILang!
```

## Running the Test Suite

```bash
python -m pytest
```

All tests should pass. See `tests/test_validation.py` for example programs.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `python: command not found` | Use `python3` instead, or add Python to PATH |
| `Error: File not found` | Ensure the `.ail` file exists and the path is correct |
| `ModuleNotFoundError: No module named 'compiler'` | Run `pip install -e .` from the project root |
| Import errors after pulling latest code | Re-run `pip install -e .` to pick up new dependencies |
| `Runtime error: to_int expects a string or int` | See `convert.to_int` docs — pass a string or int |
| `pytest` hangs or has teardown errors on Windows | Run with `-p no:cacheprovider` or use WSL |
