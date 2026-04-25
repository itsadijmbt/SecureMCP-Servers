"""
Global Singleton Accessor for the RdsMCP Instance.

This module provides a controlled, application-wide access point to the single
RdsMCP instance. It implements a singleton-like pattern to ensure that all
components, such as tools and prompts, can interact with the same central engine.

    All other modules (e.g., tool or prompt definition files) MUST use the
    `global_mcp_instance()` function to retrieve the shared instance. This is
    the only approved way to access the central MCP engine from a component.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .mcp import RdsMCP

_mcp_instance: Optional["RdsMCP"] = None

def set_mcp_instance(mcp: "RdsMCP") -> None:
    """Sets the global instance of the RdsMCP server."""
    global _mcp_instance
    if _mcp_instance is not None:
        print("Warning: RdsMCP instance is being reset.")
    _mcp_instance = mcp

def global_mcp_instance() -> "RdsMCP":
    """Retrieves the globally available RdsMCP server instance."""
    if _mcp_instance is None:
        raise RuntimeError("The RdsMCP instance has not been set yet.")
    return _mcp_instance