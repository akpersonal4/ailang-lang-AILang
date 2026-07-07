# AILang Project Folder Structure

This document defines the official, mandatory folder structure for all AILang projects. All contributors and AI models generating code for AILang **must** follow this structure.

## Canonical Directory Layout

```
project_root/
├── compiler/              # AILang compiler implementation (Python)
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli/              # Command-line interface
│   ├── parser/           # Lexer and parser
│   ├── semantic/         # Semantic analysis
│   ├── ir/               # Intermediate representation
│   └── runtime/          # Runtime interpreter
├── stdlib/               # Standard library modules (.ail files)
├── docs/                 # Documentation (canonical source of truth)
│   ├── FOLDER_STRUCTURE.md   # This file — mandatory reading
│   ├── LANGUAGE_SPEC.md      # Language specification (symbolic link or reference)
│   └── ...                   # Other documentation files
├── examples/             # Example programs demonstrating language features
│   ├── hello_world/
│   ├── variables/
│   ├── functions/
│   └── ...
├── apps/                 # Complete, runnable applications
│   ├── calculator/
│   ├── todo_manager/
│   └── ...
├── ai_benchmarks/        # AI model evaluation benchmarks
│   └── benchmarkNN_name/
│       ├── README.md
│       ├── INPUT.md
│       ├── EXPECTED_OUTPUT.md
│       └── RESULT.md
├── ai_validation/        # AI-generated code validation results
│   └── app_name/
│       └── main.ail
├── archived/             # Legacy specifications and deprecated content
│   └── specifications/
├── tests/                # Test suite
├── scripts/              # Development and utility scripts
├── pyproject.toml        # Python package configuration
├── README.md             # Project README
└── CHANGELOG.md          # Version history
```

## Folder Rules

### Documentation (`docs/`)
- **All benchmark reports must be placed in `docs/`**
- `LANGUAGE_SPEC.md` at project root is the canonical specification
- Documentation files use `.md` extension
- Reference `docs/INDEX.md` for complete documentation map

### Examples (`examples/`)
- Source files (`.ail`) go in `examples/<category>/` or directly in `examples/`
- Each example should be a minimal, focused demonstration of a language feature
- Examples should compile and run successfully

### Applications (`apps/`)
- **Complete applications must be placed in `apps/`**
- Each application gets its own subdirectory: `apps/<app_name>/`
- Application entry point should be `main.ail` or clearly named
- Applications may have supporting files (data, config, etc.)

### AI Benchmarks (`ai_benchmarks/`)
- Each benchmark in its own directory: `ai_benchmarks/benchmarkNN_description/`
- Required files: `README.md`, `INPUT.md`, `EXPECTED_OUTPUT.md`, `RESULT.md`
- Benchmark code (if any) goes in the benchmark directory

### AI Validation (`ai_validation/`)
- Contains AI-generated code that has been validated
- Each validated application in `ai_validation/<app_name>/`
- Keep original working code for reference

### Standard Library (`stdlib/`)
- Contains `.ail` files only
- One module per file: `stdlib/module_name.ail`
- No subdirectories

## Violation Examples

| ❌ WRONG | ✅ CORRECT | Rule |
|---------|-----------|------|
| `library_management_system/BENCHMARK_REPORT.md` | `docs/BENCHMARK_REPORT.md` | Benchmark reports go in docs |
| `apps/calculator/main.ail` mixed with `apps/calculator.js` | All in correct locations | Keep languages separated |
| `benchmark_report.md` at root | `docs/benchmark_report.md` | Documentation consolidation |

## Enforcement

This structure is enforced by:
1. Code review process
2. CI/CD validation scripts
3. Documentation audit checks