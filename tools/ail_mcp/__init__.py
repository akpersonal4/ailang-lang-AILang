# AILang MCP Server
# Model Context Protocol server for AILang compiler capabilities

"""AILang MCP Server - exposes compiler capabilities to AI tools via MCP protocol."""

try:
    from compiler._version import __version__
except ImportError:
    __version__ = "1.1.16"
