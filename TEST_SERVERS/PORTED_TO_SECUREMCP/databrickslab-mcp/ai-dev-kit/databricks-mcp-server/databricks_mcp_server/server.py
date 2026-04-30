"""
Databricks MCP Server (SecureMCP port).

Originally a FastMCP server that exposes Databricks operations as MCP tools.
This file has been ported to SecureMCP. See MIGRATION.txt in this directory
for what changed and why.
"""

import functools
import subprocess
import sys

# PORT: fastmcp v2 -> SecureMCP. Same .tool decorator surface for our
# usage; per-tool kwargs that fastmcp had (timeout=, etc.) are dropped.
# from fastmcp import FastMCP
from macaw_adapters.mcp import SecureMCP

# PORT: TimeoutHandlingMiddleware (fastmcp v2 Middleware class) is gone.
# SecureMCP has no middleware hook. Replaced by a post-registration
# installer that wraps each tool's handler. See error_wrapper.py.
# Original: from .middleware import TimeoutHandlingMiddleware
from .error_wrapper import install_error_handling


# ---------------------------------------------------------------------------
# Windows fix (kept) -- independent of MCP framework
# ---------------------------------------------------------------------------


def _patch_subprocess_stdin():
    """Monkey-patch subprocess so stdin defaults to DEVNULL on Windows.

    When the MCP server runs in stdio mode, stdin IS the JSON-RPC pipe.
    Any subprocess call without explicit stdin lets child processes inherit
    this pipe handle. On Windows the Databricks SDK refreshes auth tokens
    via subprocess.run(["databricks", "auth", "token", ...], shell=True)
    without setting stdin -- the spawned databricks.exe blocks reading from
    the shared pipe, hanging every MCP tool call.

    Fix: default stdin to DEVNULL so child processes never touch the pipe.
    See: https://github.com/modelcontextprotocol/python-sdk/issues/671
    """
    _original_run = subprocess.run

    @functools.wraps(_original_run)
    def _patched_run(*args, **kwargs):
        kwargs.setdefault("stdin", subprocess.DEVNULL)
        return _original_run(*args, **kwargs)

    subprocess.run = _patched_run

    _OriginalPopen = subprocess.Popen

    class _PatchedPopen(_OriginalPopen):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("stdin", subprocess.DEVNULL)
            super().__init__(*args, **kwargs)

    subprocess.Popen = _PatchedPopen


# Apply subprocess patch early -- before any Databricks SDK import (Windows only)
if sys.platform == "win32":
    _patch_subprocess_stdin()


# ---------------------------------------------------------------------------
# PORT: removed FastMCP-internal patches.
#
# The original file monkey-patched mcp.tool to wrap sync functions in
# asyncio.to_thread() and overrode mcp._docket_lifespan to disable
# FastMCP's docket worker on Windows. Both were workarounds for FastMCP
# v2 internals -- they have no equivalent under SecureMCP and would
# either fail (mcp.tool patch) or be no-ops (_docket_lifespan).
#
# Original (kept here as a record of what was removed):
#
#   def _patch_tool_decorator_for_async():
#       """Wrap sync tool functions in asyncio.to_thread() on all platforms."""
#       original_tool = mcp.tool
#       @functools.wraps(original_tool)
#       def patched_tool(fn=None, *args, **kwargs):
#           ...
#       mcp.tool = patched_tool
#
#   _fastmcp_kwargs = {}
#   if sys.platform == "win32":
#       _fastmcp_kwargs["tasks"] = False
#   mcp = FastMCP("Databricks MCP Server", **_fastmcp_kwargs)
#
#   if sys.platform == "win32":
#       @asynccontextmanager
#       async def _noop_lifespan(*args, **kwargs):
#           yield
#       if hasattr(mcp, "_docket_lifespan"):
#           mcp._docket_lifespan = _noop_lifespan
#
#   mcp.add_middleware(TimeoutHandlingMiddleware())
#   _patch_tool_decorator_for_async()
# ---------------------------------------------------------------------------


# Server initialisation
mcp = SecureMCP("Databricks MCP Server")


# Import and register all tools.
# Side-effect imports: each module runs `from ..server import mcp` and then
# decorates its tool functions with @mcp.tool, populating SecureMCP's
# internal _tools dict.
from .tools import (  # noqa: F401, E402
    sql,
    compute,
    file,
    pipelines,
    jobs,
    agent_bricks,
    aibi_dashboards,
    serving,
    unity_catalog,
    volume_files,
    genie,
    manifest,
    vector_search,
    lakebase,
    user,
    apps,
    workspace,
    pdf,
)


# After every @mcp.tool decoration has run, walk _tools and wrap each
# handler with the error-handling wrapper. Order matters: this MUST come
# after the tool imports above.
install_error_handling(mcp)
