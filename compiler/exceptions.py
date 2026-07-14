"""Custom exception types for the AILang compiler.

InternalCompilerError is used for invariants that should never be violated
in normal operation. When raised, the CLI will catch it and emit a CMP001
diagnostic instead of a Python traceback.
"""

class InternalCompilerError(Exception):
    """Exception indicating a bug or invariant violation inside the compiler.

    It should be caught at the CLI boundary and presented to the user as a
    generic internal error (CMP001) with no stack trace.
    """
    pass
