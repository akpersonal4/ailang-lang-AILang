# Contributing to AILang

Thank you for your interest in contributing! Please see our full contributor guide:

**[Contributor Guide](docs/governance/CONTRIBUTING.md)**

## Quick Start

```bash
git clone https://github.com/akpersonal4/ailang-lang-AILang.git
cd ailang-lang-AILang
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest black ruff mypy
```

## Quality Gates

All PRs must pass:

```bash
python -m pytest    # All 894 tests pass
black --check .     # Formatting
ruff check .        # Linting
mypy                # Type checking
```

## License

By contributing, you agree that your contribution is licensed under the Apache License 2.0.
