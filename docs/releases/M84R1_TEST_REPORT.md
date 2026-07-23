# M84R1 Test Report

**Milestone:** M84R.1 — Final Remediation Before Release
**Date:** 2026-07-22
**Environment:** Windows 11, Python 3.11.15

---

## Test Suite Summary

| Test File | Tests | Pass | Fail | Status |
|-----------|:-----:|:----:|:----:|:------:|
| `tests/test_ail_doctor.py` | 8 | 8 | 0 | ALL PASS |
| `tests/test_dx_improvements.py` | 34 | 34 | 0 | ALL PASS |
| **Total** | **42** | **42** | **0** | **ALL PASS** |

---

## Doctor Tests (`test_ail_doctor.py`)

| # | Test | Description | Result |
|:-:|------|-------------|:------:|
| 1 | `test_doctor_tool_prints_to_stdout` | Tool runs with exit code 0, output contains "AILang Doctor" and "Project Health" | PASS |
| 2 | `test_doctor_is_read_only` | No new files created after running doctor | PASS |
| 3 | `test_doctor_project_mode_sections` | Default mode contains Environment, Standard Library, Project sections | PASS |
| 4 | `test_doctor_repo_mode_sections` | --repo mode contains Repository Health Score, Installation, Components, Warnings, Errors, Recommendations, Version Consistency, Next Steps | PASS |
| 5 | `test_doctor_repo_mode_score_format` | Health score matches `\*\*(\d+)/100\*\*` pattern | PASS |
| 6 | `test_doctor_project_mode_shows_python` | Output includes Python version | PASS |
| 7 | `test_doctor_project_mode_shows_package` | Output includes "ailang-lang" | PASS |
| 8 | `test_doctor_repo_mode_shows_components` | Output includes MCP server, LSP server, Embedded docs, Standard library | PASS |

---

## DX Improvements Tests (`test_dx_improvements.py`)

### Diagnostics Next Steps (5 tests)

| # | Test | Result |
|:-:|------|:------:|
| 1 | `test_diagnostic_has_next_steps_field` | PASS |
| 2 | `test_diagnostic_next_steps_none_by_default` | PASS |
| 3 | `test_formatter_suggest_next_steps_returns_string` | PASS |
| 4 | `test_formatter_format_summary` | PASS |
| 5 | `test_formatter_format_summary_no_issues` | PASS |

### Context Workflow Metadata (4 tests)

| # | Test | Result |
|:-:|------|:------:|
| 6 | `test_json_has_recommended_workflows` | PASS |
| 7 | `test_json_has_dx_tools` | PASS |
| 8 | `test_recommended_workflows_has_new_project` | PASS |
| 9 | `test_dx_tools_has_doctor` | PASS |

### Heal Tool (6 tests)

| # | Test | Description | Result |
|:-:|------|-------------|:------:|
| 10 | `test_heal_lists_topics` | Lists all 9 topics including map_safety, string_concat | PASS |
| 11 | `test_heal_forward_reference_topic` | Output contains "Forward Reference" and bottom-up guidance | PASS |
| 12 | `test_heal_env_setup_topic` | Output contains "pip install ailang-lang" (NOT "pip install -e .") | PASS |
| 13 | `test_heal_map_safety_topic` | Output contains map.has and map.get patterns | PASS |
| 14 | `test_heal_string_concat_topic` | Output contains "string.concat" and "2 arguments" | PASS |
| 15 | `test_heal_unknown_topic_returns_error` | Unknown topic returns exit code 1 | PASS |

### First Run Experience (2 tests)

| # | Test | Result |
|:-:|------|:------:|
| 16 | `test_get_config_dir_returns_path` | PASS |
| 17 | `test_state_file_persistence` | PASS |

### Package Detection (6 tests)

| # | Test | Description | Result |
|:-:|------|-------------|:------:|
| 18 | `test_detect_installation_returns_dict` | Returns dict with method, version, details | PASS |
| 19 | `test_detect_installation_finds_version` | Version is not None when installed | PASS |
| 20 | `test_get_install_recommendation_pypi` | PyPI → "pip install ailang-lang" | PASS |
| 21 | `test_get_install_recommendation_editable` | Editable → "pip install ailang-lang" | PASS |
| 22 | `test_get_install_recommendation_not_installed` | Not installed → "pip install ailang-lang" | PASS |
| 23 | `test_get_install_recommendation_source_checkout` | Source checkout → "pip install -e ." | PASS |

### Path Leakage Prevention (6 tests)

| # | Test | Result |
|:-:|------|:------:|
| 24 | `test_context_json_no_path_leakage` | PASS |
| 25 | `test_context_json_has_retrieval_policy` | PASS |
| 26 | `test_context_markdown_no_path_leakage` | PASS |
| 27 | `test_doctor_no_path_leakage` | PASS |
| 28 | `test_heal_no_path_leakage` | PASS |
| 29 | `test_benchmark_metadata_no_absolute_paths` | PASS |

### Doctor New Checks (5 tests)

| # | Test | Result |
|:-:|------|:------:|
| 30 | `test_check_python_version` | PASS |
| 31 | `test_check_stdlib_available` | PASS |
| 32 | `test_check_mcp_available` | PASS |
| 33 | `test_check_lsp_available` | PASS |
| 34 | `test_check_vscode_extension` | PASS |

---

## Manual Regression Tests

| Command | Expected | Result |
|---------|----------|:------:|
| `ail version` | Prints "AILang v1.1.1" | PASS |
| `ail doctor` | Project Health report with environment, stdlib, project | PASS |
| `ail doctor --repo` | Repository Health report with health score | PASS |
| `ail heal` | Lists 9 topics | PASS |
| `ail heal forward_reference` | Forward reference guidance | PASS |
| `ail heal env_setup` | Recommends `pip install ailang-lang` | PASS |
| `ail heal map_safety` | map.has/map.get guidance | PASS |
| `ail heal string_concat` | string.concat 2-arg guidance | PASS |
| `ail heal nonexistent` | Exit code 1, error message | PASS |
| `ail docs` | Lists 3 documents | PASS |
| `ail docs AGENTS` | Prints AGENTS.md content | PASS |
| `ail new demo` | Creates project with main.ail, README.md, ail.toml, ail.lock | PASS |
| `ail run demo/main.ail` | Prints "Hello, AILang!" | PASS |
| `ail doctor` (from project) | Project Health with ail.toml [OK] | PASS |
| Path leakage check | No developer-specific paths in output | PASS |
