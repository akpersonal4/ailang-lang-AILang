# Troubleshooting

**"Command not found" after pip install**

```bash
# Ensure the Python Scripts directory is on your PATH:
python -m site --user-site
# Usually: ~/AppData/Roaming/Python/Python311/Scripts (Windows)
# Or: ~/.local/bin (Linux/macOS)
```

**"Module not found" when running from outside project**

```bash
# AILang v1.1.5+ resolves stdlib from the installed package automatically.
# If you still see MOD003, try reinstalling:
pip install --force-reinstall ailang-lang
```

**"Unexpected character" on Windows**

```bash
# The file may have a BOM marker. Save without BOM (UTF-8 without signature):
# In VS Code: File → Save with Encoding → UTF-8
# Then re-run: ail run <file>
```

**"Running this file outside a project tree" warning**

```bash
# This is informational — the file will still run. Create a project for
# full package management support:
ail new myproject && cd myproject
# Then copy your .ail file into myproject/
```

**"Forward reference" error**

```bash
# Functions must be defined before they are called.
# Run to see the exact ordering issue:
ail check <file>
# Then move the called function above its caller.
```

> For detailed error explanations: `ail explain <ERROR_CODE>`
> For environment diagnostics: `ail doctor`
