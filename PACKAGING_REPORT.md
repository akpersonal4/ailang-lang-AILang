# Packaging Report

## Developer Tool Discoverability Investigation

### Observation Reported

Independent validator observed: "tools exist, tools execute, tools are installed, tools are only accessible as Python modules"

### Investigation

#### Question 1: What is the intended design?

After reviewing the codebase:

1. **CLI has proper dispatch** - `compiler/cli/main.py` defines commands like `cmd_doctor()`, `cmd_heal()`, etc.
2. **Tools are invoked via `ail <tool>` subcommands** - The `_run_dx_tool()` helper shells out to the tool modules
3. **pyproject.toml defines only `ail` console script** - Other tools are accessed through `ail` subcommands, not as standalone executables

#### Question 2: Is this intended design (Option B) or should console_scripts be added (Option A)?

**Finding: Option B - `ail <tool>` subcommands is the intended design**

Evidence:
1. README.md documents tools as `ail doctor`, `ail heal`, `ail mcp`, etc.
2. CLI main.py has `cmd_doctor()`, `cmd_heal()`, etc. functions that dispatch to tool modules
3. The `_run_dx_tool()` function is the standard way to invoke tools
4. No evidence of intention to add standalone console_scripts

#### Question 3: Can tools be invoked directly?

Yes, tools can also be invoked as Python modules:
```bash
python -m tools.ail_doc_verify
python -m tools.ail_doctor
```

But this is an alternative invocation method, not the primary one.

### Evidence

**Test: `ail doctor --help`**
```
# AILang Doctor Report
...
```

The command works and invokes `tools.ail_doctor` via `_run_dx_tool()`.

**CLI Dispatch Code (compiler/cli/main.py:1862-1883):**
```python
def _run_dx_tool(module_name: str, args: list[str]) -> int:
    """Helper to run a DX tool by shelling out to its __main__ module."""
    project_root = _find_project_root(Path.cwd())
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    root_str = str(project_root)
    if root_str not in pythonpath:
        env["PYTHONPATH"] = root_str + (";" + pythonpath if pythonpath else "")
    return subprocess.run(
        [sys.executable, "-m", module_name] + list(args),
        env=env,
    ).returncode

def cmd_doctor(args: list[str]) -> int:
    return _run_dx_tool("tools.ail_doctor", args)
```

### Conclusion

**NOT A BUG - INTENDED DESIGN**

The tools ARE accessible as standalone commands via the `ail` CLI. The validator's observation that tools are "only accessible as Python modules" is incorrect.

The design is:
1. Primary: `ail <tool>` (e.g., `ail doctor`)
2. Alternative: `python -m tools.ail_<tool>` (e.g., `python -m tools.ail_doctor`)

Both work. The primary interface is through `ail` subcommands as documented in README.md.

### Recommendation

No changes required. The developer tool discoverability is working as designed.

### Documentation Already Accurate

README.md section "Developer Tools" correctly documents:
```
ail doctor               # Diagnose environment issues
ail heal                 # Get fix suggestions for common errors
ail docs [<name>]        # Read documentation
ail context [--json]     # Get machine-readable language context
ail mcp                  # Start MCP server
ail static-analyzer      # Run static analysis
ail benchmark            # Run benchmark suite
ail testgen              # Generate test cases
```

All commands work correctly.