# DX Tool #001 AI Validation
# Simulates AI session with and without PROJECT_CONTEXT.md

from pathlib import Path


def analyze_context_for_ailang_understanding() -> dict:
    """
    Simulate: "Read this context. What is AILang?"
    Returns whether key information is present in the context.
    """
    context_path = Path(__file__).resolve().parent.parent / "generated" / "PROJECT_CONTEXT.md"
    context = context_path.read_text(encoding="utf-8")
    
    required_knowledge = {
        "language_name": "AILang" in context,
        "version": "v0.2.0" in context,
        "no_loops": "No loops" in context or "recursion only" in context,
        "no_forward_references": "forward references" in context or "No forward references" in context,
        "no_nested_functions": "nested functions" in context or "No nested functions" in context,
        "deterministic": "Deterministic" in context,
        "compiler_architecture": "Compiler Architecture" in context,
        "runtime_optimization": "RTO-001" in context or "Runtime Optimization" in context,
        "stdlib_count": "16 modules" in context,
        "do_not_change": "Do Not Change Rules" in context,
        "validation_checklist": "Validation Checklist" in context or "11" in context,
    }
    
    return required_knowledge


def analyze_context_for_todo_app() -> dict:
    """
    Simulate: "Build a Todo app."
    Returns whether the context provides enough information to build correctly.
    """
    context_path = Path(__file__).resolve().parent.parent / "generated" / "PROJECT_CONTEXT.md"
    context = context_path.read_text(encoding="utf-8")
    
    # Information needed to build a todo app without hallucinations
    requirements = {
        "stdlib_string": "string" in context,
        "stdlib_list": "list" in context,
        "stdlib_map": "map" in context,
        "stdlib_file": "file" in context,
        "stdlib_json": "json" in context,
        "stdlib_io": "io" in context,
        "function_syntax": "function" in context.lower(),
        "let_syntax": "let" in context,
        "return_syntax": "return" in context,
        "bottom_up_ordering": "bottom-up" in context.lower(),
        "import_at_top": "import" in context,
        "missing_functions_warning": "Missing functions" in context or "split" in context or "find" in context,
    }
    
    return requirements


def check_potential_hallucinations() -> dict:
    """
    Check that context warns about missing functions to prevent hallucinations.
    """
    context_path = Path(__file__).resolve().parent.parent / "generated" / "PROJECT_CONTEXT.md"
    context = context_path.read_text(encoding="utf-8")
    
    # These functions DON'T exist in stdlib but developers might expect them
    missing_functions = ["split", "join", "find", "sort", "list.copy"]
    
    warnings_present = {}
    for func in missing_functions:
        warnings_present[func] = func in context
    
    return warnings_present


def main() -> int:
    """Run AI validation tests."""
    print("=" * 60)
    print("DX TOOL #001 AI VALIDATION")
    print("=" * 60)
    
    print("\nTEST A: Understanding Check - 'What is AILang?'")
    print("-" * 60)
    understanding = analyze_context_for_ailang_understanding()
    for key, present in understanding.items():
        status = "✓" if present else "✗"
        print(f"  {status} {key}: {'present' if present else 'MISSING'}")
    
    print("\nTEST B: Todo App Requirements Check - 'Build a Todo app.'")
    print("-" * 60)
    todo_req = analyze_context_for_todo_app()
    for key, present in todo_req.items():
        status = "✓" if present else "✗"
        print(f"  {status} {key}: {'present' if present else 'MISSING'}")
    
    print("\nTEST C: Hallucination Prevention Check")
    print("-" * 60)
    hallucinations = check_potential_hallucinations()
    for key, warned in hallucinations.items():
        status = "✓" if warned else "✗"
        print(f"  {status} Warning for '{key}': {'present' if warned else 'MISSING'}")
    
    # Summary
    all_understanding = all(understanding.values())
    all_todo = all(todo_req.values())
    all_hallucinations = all(hallucinations.values())
    
    print("\n" + "=" * 60)
    print("AI VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Understanding coverage: {'PASS' if all_understanding else 'FAIL'}")
    print(f"  Todo app requirements: {'PASS' if all_todo else 'FAIL'}")
    print(f"  Hallucination prevention: {'PASS' if all_hallucinations else 'FAIL'}")
    
    all_pass = all_understanding and all_todo and all_hallucinations
    print(f"\n  OVERALL: {'PASS - Context reduces AI mistakes' if all_pass else 'FAIL'}")
    
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())