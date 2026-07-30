# CLI Command Reference

| Command | Action |
|---------|--------|
| `ail run <file>` | Compile and run an AILang program |
| `ail build <file>` | Compile and check for errors (no execution) |
| `ail check <file>` | Check for forward references and ordering violations |
| `ail fmt <file\|dir>` | Format AILang source file(s) |
| `ail test [<file\|dir>]` | Run test_*.ail files |
| `ail new <project>` | Create a new AILang project scaffold |
| `ail rename <old> <new>` | Rename identifier repository-wide |
| `ail order <target>` | Analyze dependency ordering of .ail files |
| `ail watch [<file>]` | Watch for changes, recompile incrementally |
| `ail install` | Install dependencies from ail.toml |
| `ail add <package>` | Add a dependency to ail.toml |
| `ail remove <package>` | Remove a dependency from ail.toml |
| `ail update` | Re-resolve all dependencies |
| `ail list` | List installed dependencies |
| `ail publish` | Publish project to package registry |
| `ail doctor` | Diagnose environment issues |
| `ail heal` | Get fix suggestions for common errors |
| `ail explain <CODE>` | Explain a compiler error code in detail |
| `ail docs [<name>]` | Read documentation offline |
| `ail context [--json]` | Get machine-readable language context |
| `ail mcp` | Start MCP server for AI tool integration |
| `ail lsp` | Start the LSP server (stdin/stdout) |
| `ail --version` | Print version information |
