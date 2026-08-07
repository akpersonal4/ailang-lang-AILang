# AILang Benchmark Runner: Discovery
# Auto-discovers benchmark applications from the repository

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from ail_platform.project import bundled_apps_dir


@dataclass
class Benchmark:
    """Structured metadata for a single benchmark application."""

    name: str
    path: Path
    suite: str
    description: str = ""
    args: list[str] | None = None


SUITE_DEFINITIONS: dict[str, list[str]] = {
    "quick": [
        "dice_roller",
        "hangman_game",
    ],
    "canonical": [
        "dice_roller",
        "hangman_game",
        "inventory_mgmt",
        "kanban",
        "static_analyzer",
    ],
}

# Args for the static_analyzer benchmark are relative to the app's own
# directory (the runner sets cwd to the benchmark app's parent), so the
# analyzer analyzes its own main.ail. This stays correct both in a source
# checkout (apps/static_analyzer/) and on a wheel install (bundled data).
BENCHMARK_ARGS: dict[str, list[str]] = {
    "static_analyzer": ["main.ail"],
}


def benchmark_apps_dir(root: Path) -> Path:
    """Return the directory holding benchmark apps (apps/<name>/main.ail).

    In a source checkout this is ``<root>/apps`` (live app sources). On a
    wheel install there is no ``apps/`` tree under site-packages, so fall
    back to the apps bundled with the package under
    ``ail_platform/data/apps``. This makes `ail benchmark` usable after a
    plain ``pip install ailang-lang``.
    """
    live = root / "apps"
    if live.is_dir():
        return live
    return bundled_apps_dir()


def discover_all_apps(root: Path) -> list[Benchmark]:
    """Auto-discover all benchmark applications in apps/*/main.ail."""
    apps_dir = benchmark_apps_dir(root)
    if not apps_dir.is_dir():
        return []

    benchmarks: list[Benchmark] = []
    for entry in sorted(apps_dir.iterdir()):
        if entry.is_dir():
            main_ail = entry / "main.ail"
            if main_ail.is_file():
                benchmarks.append(
                    Benchmark(
                        name=entry.name,
                        path=main_ail,
                        suite="full",
                    )
                )
    return benchmarks


def _add_args(benchmarks: list[Benchmark]) -> list[Benchmark]:
    """Attach extra CLI arguments from BENCHMARK_ARGS to matching benchmarks."""
    for bm in benchmarks:
        if bm.name in BENCHMARK_ARGS:
            bm.args = BENCHMARK_ARGS[bm.name]
    return benchmarks


def discover_benchmarks(
    root: Path,
    suite: str = "canonical",
    app_name: str | None = None,
) -> list[Benchmark]:
    """Discover benchmarks based on suite and optional app filter.

    Args:
        root: Project root path.
        suite: Suite name ('quick', 'canonical', 'full').
        app_name: If set, return only the single matching app.

    Returns:
        List of Benchmark objects.

    Raises:
        ValueError: If the suite name is unknown.
    """
    if app_name:
        # Single app mode: return just that one app
        app_path = benchmark_apps_dir(root) / app_name / "main.ail"
        if not app_path.is_file():
            raise ValueError(
                f"Benchmark app '{app_name}' not found at apps/{app_name}/main.ail"
            )
        return _add_args(
            [
                Benchmark(
                    name=app_name,
                    path=app_path,
                    suite="app",
                )
            ]
        )

    if suite == "full":
        return _add_args(discover_all_apps(root))

    if suite not in SUITE_DEFINITIONS:
        valid = ", ".join(sorted(SUITE_DEFINITIONS.keys()) + ["full"])
        raise ValueError(f"Unknown suite '{suite}'. Valid suites: {valid}")

    apps_dir = benchmark_apps_dir(root)
    app_names = SUITE_DEFINITIONS[suite]
    benchmarks: list[Benchmark] = []
    for app_name in app_names:
        app_path = apps_dir / app_name / "main.ail"
        if not app_path.is_file():
            print(
                f"Warning: Expected benchmark '{app_name}' not found at "
                f"apps/{app_name}/main.ail — skipping",
                file=sys.stderr,
            )
            continue
        benchmarks.append(
            Benchmark(
                name=app_name,
                path=app_path,
                suite=suite,
            )
        )
    # Fallback: a named suite (quick/canonical) that resolves to zero
    # benchmarks is unusable. Fall back to the 'full' suite (auto-discover
    # every app under apps/) so the command is usable on any checkout,
    # not only the dev repo where the canonical apps live.
    if not benchmarks and suite != "full":
        print(
            f"Note: suite '{suite}' found no apps; falling back to 'full' "
            f"(auto-discover apps/*/main.ail).",
            file=sys.stderr,
        )
        benchmarks = discover_all_apps(root)
    return _add_args(benchmarks)
