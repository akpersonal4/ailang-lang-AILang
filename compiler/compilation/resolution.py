"""Module resolution for AILang.

Resolves module paths to file paths and manages the module dependency graph.
"""

from __future__ import annotations

from pathlib import Path


class ModuleResolutionError(Exception):
    """Raised when module resolution fails."""

    pass


class ModuleResolver:
    """Resolves module paths to file paths and builds dependency graphs."""

    def __init__(self, root_dir: Path | str = ".") -> None:
        self.root = Path(root_dir).resolve()
        self._module_cache: dict[str, Path] = {}

    def resolve(self, module_path: tuple[str, ...]) -> Path:
        """Resolve a module path to a file path.

        Args:
            module_path: Tuple of path segments, e.g., ("math", "add")

        Returns:
            Resolved Path to the .ail file

        Raises:
            ModuleResolutionError: If the module cannot be found or path is invalid

        Resolution order for multi-segment paths like ("math", "add"):

        1. Try <root>/math.ail – if it exists, math is the module file
           and add is an exported symbol within it.  This is the
           "module + symbol" interpretation used by import math.add.
        2. Try <root>/math/add.ail – the fully-nested file interpretation.

        Single-segment paths always resolve to <segment>.ail directly.
        """
        if not module_path:
            raise ModuleResolutionError("Empty module path")

        # Prevent path traversal attempts
        for segment in module_path:
            if segment in ("..", "."):
                raise ModuleResolutionError(
                    f"Path traversal attempt in module path: {module_path}"
                )

        module_key = ".".join(module_path)
        if module_key in self._module_cache:
            return self._module_cache[module_key]

        # ------------------------------------------------------------------
        # For multi-segment paths try the "parent module + symbol" strategy
        # first: import math.add → try math.ail before math/add.ail.
        # ------------------------------------------------------------------
        if len(module_path) > 1:
            parent_file = self.root.joinpath(module_path[0]).with_suffix(".ail")
            if parent_file.exists():
                self._module_cache[module_key] = parent_file
                return parent_file

        # Fall back to the fully-nested file path: math/add.ail
        file_path = self.root.joinpath(*module_path).with_suffix(".ail")

        if not file_path.exists():
            raise ModuleResolutionError(f"Module not found: {module_key}")

        self._module_cache[module_key] = file_path
        return file_path
