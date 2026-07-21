"""AILang Dependency Ordering Assistant - Graph analysis."""

from __future__ import annotations

from tools.ail_order.models import FileAnalysis, FunctionInfo, OrderingFinding, Severity


def compute_topological_levels(functions: list[FunctionInfo]) -> dict[int, list[str]]:
    """Compute topological levels for functions.

    Level 0: Functions with no calls to other functions in this file
    Level N: Functions that only call functions at Level < N
    """
    if not functions:
        return {}

    # Build function name set and index
    fn_names = {fn.name for fn in functions}

    # Build call graph (only for internal calls)
    call_graph: dict[str, set[str]] = {}
    for fn in functions:
        internal_calls = set()
        for call in fn.calls:
            if call in fn_names and call != fn.name:  # Exclude self-calls (recursion)
                internal_calls.add(call)
        call_graph[fn.name] = internal_calls

    # Compute levels iteratively
    levels: dict[int, list[str]] = {}
    assigned = set()

    # Level 0: No internal dependencies
    level = 0
    changed = True
    max_iterations = len(functions) + 10  # Safety limit

    while changed and level < max_iterations:
        changed = False
        for fn in functions:
            if fn.name in assigned:
                continue
            # Check if all callees are assigned
            callees = call_graph.get(fn.name, set())
            unassigned_callees = callees - assigned
            if not unassigned_callees:
                fn.level = level
                levels.setdefault(level, []).append(fn.name)
                assigned.add(fn.name)
                changed = True
        level += 1

    # Handle any remaining (cycles)
    for fn in functions:
        if fn.name not in assigned:
            # These are in cycles - assign to last level
            fn.level = level
            levels.setdefault(level, []).append(fn.name)
            assigned.add(fn.name)

    return levels


def detect_forward_references(functions: list[FunctionInfo]) -> list[OrderingFinding]:
    """Detect forward reference violations."""
    findings = []
    fn_names = {fn.name for fn in functions}
    defined_order = {fn.name: i for i, fn in enumerate(functions)}

    for fn in functions:
        for call in fn.calls:
            if call in fn_names and call != fn.name:
                caller_idx = defined_order[fn.name]
                callee_idx = defined_order[call]
                if callee_idx > caller_idx:
                    # Forward reference detected
                    findings.append(
                        OrderingFinding(
                            severity=Severity.ERROR,
                            message=f"Forward reference: '{call}' called before definition",
                            function=fn.name,
                            line=fn.line,
                            suggestion=f"Move '{call}' before '{fn.name}' or call order",
                        )
                    )

    return findings


def detect_cycles(
    functions: list[FunctionInfo],
) -> tuple[list[list[str]], list[OrderingFinding]]:
    """Detect circular function dependencies."""
    cycles = []
    findings = []

    fn_names = {fn.name for fn in functions}
    call_graph: dict[str, set[str]] = {}

    for fn in functions:
        internal_calls = set()
        for call in fn.calls:
            if call in fn_names and call != fn.name:  # Exclude self-calls
                internal_calls.add(call)
        call_graph[fn.name] = internal_calls

    # DFS for cycles with proper path tracking
    visited = set()

    def dfs(node: str, path: list[str], path_set: set[str]) -> bool:
        """Returns True if cycle found."""
        if node in path_set:
            # Found cycle - extract it from path
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return True

        if node in visited:
            return False

        visited.add(node)
        path.append(node)
        path_set.add(node)

        for neighbor in call_graph.get(node, set()):
            if dfs(neighbor, path, path_set):
                return True

        path.pop()
        path_set.remove(node)
        return False

    for fn in functions:
        if fn.name not in visited:
            dfs(fn.name, [], set())

    # Create findings for cycles
    for cycle in cycles:
        cycle_str = " -> ".join(cycle)
        findings.append(
            OrderingFinding(
                severity=Severity.ERROR,
                message=f"Circular dependency detected: {cycle_str}",
                suggestion="Mutual recursion is not supported in AILang - restructure to avoid cycles",
            )
        )

    return cycles, findings


def detect_unreachable(functions: list[FunctionInfo]) -> list[str]:
    """Detect functions not reachable from main()."""
    if not functions:
        return []

    fn_names = {fn.name for fn in functions}

    if "main" not in fn_names:
        return []  # No main function, everything is potentially reachable

    # BFS from main
    reachable = set()
    call_graph: dict[str, set[str]] = {}

    for fn in functions:
        internal_calls = set()
        for call in fn.calls:
            if call in fn_names:
                internal_calls.add(call)
        call_graph[fn.name] = internal_calls

    # BFS
    to_visit = ["main"]
    while to_visit:
        current = to_visit.pop(0)
        if current in reachable:
            continue
        reachable.add(current)
        for callee in call_graph.get(current, set()):
            if callee not in reachable:
                to_visit.append(callee)

    unreachable = [
        fn.name for fn in functions if fn.name not in reachable and fn.name != "main"
    ]
    return unreachable


def analyze_graph(file_analysis: FileAnalysis) -> None:
    """Analyze the call graph and populate findings in file_analysis."""
    functions = file_analysis.functions

    # Compute topological levels
    file_analysis.levels = compute_topological_levels(functions)

    # Detect forward references
    file_analysis.findings.extend(detect_forward_references(functions))

    # Detect cycles
    cycles, cycle_findings = detect_cycles(functions)
    file_analysis.cycles = cycles
    file_analysis.findings.extend(cycle_findings)

    # Detect unreachable functions
    file_analysis.unreachable = detect_unreachable(functions)

    for unreachable_fn in file_analysis.unreachable:
        # Find the function to get line info
        for fn in functions:
            if fn.name == unreachable_fn:
                file_analysis.findings.append(
                    OrderingFinding(
                        severity=Severity.WARNING,
                        message=f"Function '{unreachable_fn}' is not reachable from main()",
                        function=unreachable_fn,
                        line=fn.line,
                        suggestion="Consider removing or adding a call path from main()",
                    )
                )
                break

    # Add duplicate findings
    for dup_name in file_analysis.duplicates:
        file_analysis.findings.append(
            OrderingFinding(
                severity=Severity.ERROR,
                message=f"Duplicate function definition: '{dup_name}'",
                suggestion="Remove duplicate or rename one function",
            )
        )
