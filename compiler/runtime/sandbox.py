"""Security sandboxing policy for AILang runtime.

AILang programs run in a trusted-code execution model. The sandbox
provides defense-in-depth restrictions on filesystem, environment, and
process access. Programs that need unrestricted access can disable the
sandbox via the --no-sandbox CLI flag.

Default policy:
- File operations restricted to the project working directory and its descendants
- Environment variable access restricted to AILANG_* prefix
- file_write creates directories only within the working directory
- file_read limited to 10MB per read
- Recursion limit set to 2000 (matches the documented default in CHANGELOG v1.1.11)
"""

from __future__ import annotations

import os
from pathlib import Path


class SandboxPolicy:
    """Controls what AILang programs are allowed to access."""

    def __init__(
        self,
        working_dir: str | Path | None = None,
        env_prefix: str = "AILANG_",
        max_read_bytes: int = 10 * 1024 * 1024,  # 10 MB
        max_recursion: int = 2000,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self.working_dir = Path(working_dir).resolve() if working_dir else Path.cwd()
        self.env_prefix = env_prefix
        self.max_read_bytes = max_read_bytes
        self.max_recursion = max_recursion

    def check_path(self, path: str) -> str:
        """Resolve and validate a file path is within the working directory.

        Returns the resolved absolute path if allowed.
        Raises PermissionError if the path escapes the sandbox.
        """
        if not self.enabled:
            return str(Path(path).resolve())

        target = Path(path).resolve()

        # Allow paths that are within or equal to the working directory
        try:
            target.relative_to(self.working_dir)
        except ValueError:
            # Also allow absolute paths that resolve inside working_dir
            # (handles symlinks and .. traversal)
            common = Path(os.path.commonpath([str(target), str(self.working_dir)]))
            if common != self.working_dir:
                raise PermissionError(
                    f"Sandbox violation: '{path}' resolves outside the "
                    f"project directory ({self.working_dir})"
                )

        return str(target)

    def check_env_key(self, key: str) -> bool:
        """Check if an environment variable key is allowed.

        Returns True if the key starts with the allowed prefix or if
        the sandbox is disabled.
        """
        if not self.enabled:
            return True
        return key.startswith(self.env_prefix)

    def check_read_size(self, size: int) -> bool:
        """Check if a read size is within limits."""
        if not self.enabled:
            return True
        return size <= self.max_read_bytes

    def check_parent_creation(self, path: str) -> None:
        """Validate that parent directory creation stays within sandbox.

        Raises PermissionError if the parent would be outside working_dir.
        """
        if not self.enabled:
            return

        parent = Path(path).resolve().parent
        try:
            parent.relative_to(self.working_dir)
        except ValueError:
            raise PermissionError(
                f"Sandbox violation: cannot create directories outside "
                f"the project directory ({self.working_dir})"
            )


# Global policy instance — initialized by CLI before program execution.
# Disabled by default so tests and development work without configuration.
_policy: SandboxPolicy | None = None
_enabled_by_default = False


def get_policy() -> SandboxPolicy:
    """Get the current sandbox policy, creating a default if needed."""
    global _policy
    if _policy is None:
        _policy = SandboxPolicy(enabled=_enabled_by_default)
    return _policy


def set_policy(policy: SandboxPolicy) -> None:
    """Set the global sandbox policy."""
    global _policy
    _policy = policy


def is_enabled() -> bool:
    """Check if sandboxing is currently enabled."""
    return get_policy().enabled
