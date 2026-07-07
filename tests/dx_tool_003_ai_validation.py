# DX Tool #003 AI Validation
# Validates that the analyzer output provides useful information for AI code generation

from pathlib import Path
import json


def validate_json_for_ai_consumption() -> dict:
    """
    Validate that the JSON report provides useful metrics for AI consumption.
    """
    json_path = Path(__file__).resolve().parent.parent / "generated" / "STATIC_ANALYZER_REPORT.json"
    if not json_path.exists():
        return {"file_exists": False}

    content = json_path.read_text(encoding="utf-8")
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {"valid_json": False}

    checks = {
        "is_list": isinstance(data, list),
        "has_entries": len(data) > 0,
        "has_path": all("path" in entry for entry in data) if data else False,
        "has_total_lines": all("total_lines" in entry for entry in data) if data else False,
        "has_functions": all("functions" in entry for entry in data) if data else False,
        "has_unreachable": all("unreachable_functions" in entry for entry in data) if data else False,
        "has_undocumented": all("undocumented_functions" in entry for entry in data) if data else False,
        "has_max_depth": all("max_depth" in entry for entry in data) if data else False,
    }

    return checks


def validate_markdown_for_human_readability() -> dict:
    """
    Validate that the markdown report is human-readable and useful.
    """
    md_path = Path(__file__).resolve().parent.parent / "generated" / "STATIC_ANALYZER_REPORT.md"
    if not md_path.exists():
        return {"file_exists": False}

    content = md_path.read_text(encoding="utf-8")

    checks = {
        "has_title": "# AILang Static Analyzer Report" in content,
        "has_summary": "## Summary" in content,
        "has_warnings": "## Warnings" in content,
        "has_file_details": "## File Details" in content,
        "auto_generated_note": "Auto-generated" in content,
    }

    return checks


def validate_new_features_present() -> dict:
    """
    Validate that new DX-003 features are present in both reports.
    """
    json_path = Path(__file__).resolve().parent.parent / "generated" / "STATIC_ANALYZER_REPORT.json"
    md_path = Path(__file__).resolve().parent.parent / "generated" / "STATIC_ANALYZER_REPORT.md"

    json_checks = {}
    md_checks = {}

    if json_path.exists():
        data = json.loads(json_path.read_text(encoding="utf-8"))
        if data:
            entry = data[0]
            json_checks["unreachable_metric"] = "unreachable_functions" in entry
            json_checks["documented_metric"] = "undocumented_functions" in entry
            json_checks["depth_metric"] = "max_depth" in entry

    if md_path.exists():
        md_content = md_path.read_text(encoding="utf-8")
        md_checks["unreachable_section"] = "Unreachable" in md_content
        md_checks["documentation_section"] = "Documentation" in md_content
        md_checks["depth_metric"] = "Max call depth" in md_content

    return {"json": json_checks, "markdown": md_checks}


def validate_no_duplicate_analyzer() -> bool:
    """
    Validate that there is only ONE static analyzer application (not v2, enhanced, etc).
    """
    root = Path(__file__).resolve().parent.parent
    apps_dir = root / "apps"

    # Check for unauthorized analyzer variants
    unauthorized = []
    for subdir in apps_dir.iterdir():
        if subdir.is_dir():
            name = subdir.name
            if "static_analyzer" in name and name != "static_analyzer":
                unauthorized.append(name)

    return len(unauthorized) == 0


def main() -> int:
    """Run AI validation tests."""
    print("=" * 60)
    print("DX TOOL #003 AI VALIDATION")
    print("=" * 60)

    print("\nTEST A: JSON for AI Consumption")
    print("-" * 60)
    json_checks = validate_json_for_ai_consumption()
    for key, passed in json_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {key}: {'present' if passed else 'MISSING'}")

    print("\nTEST B: Markdown for Human Readability")
    print("-" * 60)
    md_checks = validate_markdown_for_human_readability()
    for key, passed in md_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {key}: {'present' if passed else 'MISSING'}")

    print("\nTEST C: New Features Present")
    print("-" * 60)
    feature_checks = validate_new_features_present()
    for report_type, checks in feature_checks.items():
        print(f"  {report_type.upper()} report:")
        for key, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"    {status} {key}: {'present' if passed else 'MISSING'}")

    print("\nTEST D: No Duplicate Analyzer")
    print("-" * 60)
    no_dupe = validate_no_duplicate_analyzer()
    status = "✓" if no_dupe else "✗"
    print(f"  {status} Single analyzer: {'verified' if no_dupe else 'DUPLICATE FOUND'}")

    # Summary
    all_json = all(json_checks.values())
    all_md = all(md_checks.values())
    features_json = all(feature_checks.get("json", {}).values())
    features_md = all(feature_checks.get("markdown", {}).values())

    print("\n" + "=" * 60)
    print("AI VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  JSON structure: {'PASS' if all_json else 'FAIL'}")
    print(f"  Markdown structure: {'PASS' if all_md else 'FAIL'}")
    print(f"  New features (JSON): {'PASS' if features_json else 'FAIL'}")
    print(f"  New features (MD): {'PASS' if features_md else 'FAIL'}")
    print(f"  Single analyzer: {'PASS' if no_dupe else 'FAIL'}")

    all_pass = all_json and all_md and features_json and features_md and no_dupe
    print(f"\n  OVERALL: {'PASS - AI friendly output' if all_pass else 'FAIL'}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())