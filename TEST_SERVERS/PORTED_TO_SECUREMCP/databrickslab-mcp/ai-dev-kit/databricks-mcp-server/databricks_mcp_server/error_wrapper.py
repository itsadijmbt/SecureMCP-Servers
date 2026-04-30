"""
Post-registration error wrapper for the Databricks MCP server (SecureMCP port).

Replaces the original fastmcp v2 TimeoutHandlingMiddleware
(see middleware.py for the original code -- now unused).

What this does:
  - Walks SecureMCP's internal _tools dict after every @mcp.tool
    decoration has run.
  - Replaces each tool's handler with a wrapper that catches any
    exception during the call and returns a structured JSON dict
    instead of letting the call crash.

What this DOES NOT do (intentionally):
  - No per-tool timeout enforcement. The original used
    @mcp.tool(timeout=N) + asyncio.wait_for. SecureMCP's tool()
    decorator does not accept a timeout kwarg, and we are not
    rebuilding that machinery for the port. See MIGRATION.txt.
  - No structured_content fixup. The original parsed JSON text
    content and populated ToolResult.structured_content; SecureMCP
    has no structured_content concept (mcp.py:815-817 wraps any
    non-dict return as {"result": result}), so there is nothing
    to fix.

Why a post-registration installer instead of middleware:
  SecureMCP exposes no middleware hook. The only stable plug point
  is the _tools dict (handler reference per tool name). Mutating
  the handler reference after registration is the same pattern
  used by snowflake-mcp's install_query_check.
"""

import functools
import inspect


def install_error_handling(server):
    """Wrap every registered tool handler with the error wrapper.

    Call this once, after all @mcp.tool decorations have run, before
    server.run(). Any tool registered after this call will not be
    wrapped.
    """
    for tool_name, info in server._tools.items():
        info["handler"] = _wrap(info["handler"], tool_name)


def _wrap(fn, tool_name):
    """Wrap a tool handler so any exception becomes a structured JSON dict.

    Sync and async handlers are both supported; the wrapper preserves
    the original kind so SecureMCP's call-site (mcp.py:807-813) keeps
    treating the function correctly.
    """
    if inspect.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_wrapped(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                return _error_dict(e, tool_name)

        return async_wrapped

    @functools.wraps(fn)
    def sync_wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            return _error_dict(e, tool_name)

    return sync_wrapped


def _error_dict(e, tool_name):
    """Render an exception as the structured error response shape."""
    return {
        "error": True,
        "error_type": type(e).__name__,
        "tool": tool_name,
        "message": str(e),
    }
