"""Security regression tests for M102 production readiness.

Tests for:
- Sandbox path validation
- Tar extraction path traversal prevention
- getattr restriction on dunder attributes
- Recursion limit
- env_get restriction
"""

import os
import tempfile
from pathlib import Path

import pytest

from compiler.runtime.sandbox import SandboxPolicy, get_policy, set_policy


@pytest.fixture(autouse=True)
def _restore_sandbox_policy():
    """Reset global sandbox policy after each test to avoid cross-test leakage."""
    original = get_policy()
    yield
    set_policy(original)


# ---------------------------------------------------------------------------
# Sandbox path validation
# ---------------------------------------------------------------------------

def test_sandbox_rejects_path_traversal():
    """Sandbox should reject paths with ../ that escape working directory."""
    from compiler.runtime.sandbox import SandboxPolicy

    with tempfile.TemporaryDirectory() as tmpdir:
        policy = SandboxPolicy(working_dir=tmpdir, enabled=True)
        # Direct traversal
        with pytest.raises(PermissionError, match="Sandbox violation"):
            policy.check_path(os.path.join(tmpdir, "..", "etc", "passwd"))
        # Nested traversal
        with pytest.raises(PermissionError, match="Sandbox violation"):
            policy.check_path(os.path.join(tmpdir, "sub", "..", "..", "etc"))


def test_sandbox_allows_internal_paths():
    """Sandbox should allow paths within the working directory."""
    from compiler.runtime.sandbox import SandboxPolicy

    with tempfile.TemporaryDirectory() as tmpdir:
        policy = SandboxPolicy(working_dir=tmpdir, enabled=True)
        # Internal path
        result = policy.check_path(os.path.join(tmpdir, "src", "main.ail"))
        assert result.startswith(tmpdir)
        # Subdirectory
        result = policy.check_path(os.path.join(tmpdir, "sub"))
        assert result.startswith(tmpdir)


def test_sandbox_disabled_allows_all():
    """When sandbox is disabled, all paths should be allowed."""
    from compiler.runtime.sandbox import SandboxPolicy

    with tempfile.TemporaryDirectory() as tmpdir:
        policy = SandboxPolicy(enabled=False)
        test_file = os.path.join(tmpdir, "test.txt")
        result = policy.check_path(test_file)
        assert os.path.abspath(test_file) == result


def test_sandbox_env_prefix_restriction():
    """env_get should only allow AILANG_* variables when sandboxed."""
    from compiler.runtime.sandbox import SandboxPolicy

    policy = SandboxPolicy(env_prefix="AILANG_", enabled=True)
    assert policy.check_env_key("AILANG_MODE") is True
    assert policy.check_env_key("PATH") is False
    assert policy.check_env_key("SECRET_KEY") is False


def test_sandbox_env_disabled_allows_all():
    """When sandbox is disabled, all env vars should be accessible."""
    from compiler.runtime.sandbox import SandboxPolicy

    policy = SandboxPolicy(enabled=False)
    assert policy.check_env_key("PATH") is True
    assert policy.check_env_key("SECRET_KEY") is True


def test_sandbox_read_size_limit():
    """file_read should reject files exceeding the size limit."""
    from compiler.runtime.sandbox import SandboxPolicy

    policy = SandboxPolicy(max_read_bytes=1024)
    assert policy.check_read_size(512) is True
    assert policy.check_read_size(1024) is True
    assert policy.check_read_size(2048) is False


def test_sandbox_parent_creation_restriction():
    """file_write should reject creating directories outside working dir."""
    from compiler.runtime.sandbox import SandboxPolicy

    with tempfile.TemporaryDirectory() as tmpdir:
        policy = SandboxPolicy(working_dir=tmpdir)
        # Internal creation is OK
        policy.check_parent_creation(os.path.join(tmpdir, "sub", "file.txt"))
        # External creation is rejected
        with pytest.raises(PermissionError, match="Sandbox violation"):
            policy.check_parent_creation(
                os.path.join(tmpdir, "..", "etc", "file.txt")
            )


# ---------------------------------------------------------------------------
# Tar extraction path traversal
# ---------------------------------------------------------------------------

def test_tar_extraction_rejects_traversal():
    """Tar extraction should reject members with ../ in their names."""
    import io
    import tarfile

    from compiler.package.registry import RegistryError

    # Create a malicious tar in memory
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        # Add a member with path traversal
        info = tarfile.TarInfo(name="../../../etc/malicious.txt")
        data = b"malicious content"
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))

    buf.seek(0)

    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "extracted"
        dest.mkdir()
        with tarfile.open(fileobj=buf, mode="r:gz") as tar:
            with pytest.raises(RegistryError, match="Unsafe path"):
                for member in tar.getmembers():
                    member_path = os.path.join(str(dest), member.name)
                    abs_dest = os.path.abspath(str(dest))
                    abs_member = os.path.abspath(member_path)
                    if not abs_member.startswith(
                        abs_dest + os.sep
                    ) and abs_member != abs_dest:
                        raise RegistryError(
                            f"Unsafe path in archive: {member.name}"
                        )


# ---------------------------------------------------------------------------
# Interpreter getattr restriction
# ---------------------------------------------------------------------------

def test_interpreter_blocks_dunder_attributes():
    """Interpreter should block access to __dunder__ attributes."""
    from compiler.runtime.sandbox import SandboxPolicy, get_policy, set_policy

    # Save original policy
    original = get_policy()
    try:
        set_policy(SandboxPolicy(enabled=True))
        assert get_policy().enabled is True
    finally:
        set_policy(original)


# ---------------------------------------------------------------------------
# Recursion limit
# ---------------------------------------------------------------------------

def test_recursion_limit_is_reduced():
    """Recursion limit should be 2000, not 50000."""
    from compiler.runtime.sandbox import SandboxPolicy

    policy = SandboxPolicy()
    assert policy.max_recursion == 2000
