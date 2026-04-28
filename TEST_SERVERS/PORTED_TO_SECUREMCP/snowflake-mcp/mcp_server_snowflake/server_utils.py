# PORT: SecureMCP has no middleware system. The original CheckQueryType
# middleware (commented below) ran before every tool call, looked at the
# tool name + the `statement` argument, and rejected disallowed SQL types.
#
# Replacement: install_query_check() runs ONCE after tool registration.
# It walks SecureMCP's internal _tools dict and wraps the handlers of the
# tools the middleware would have intercepted. The check now runs inside
# each affected tool's handler instead of at a framework hook.
#
# Same dispatch rules as the original middleware:
#   - run_snowflake_query: read kwargs["statement"], validate via validate_sql_type
#   - create_*, drop_*:    validate via validate_object_tool by tool name only

import functools

# was: from fastmcp import FastMCP
# was: from fastmcp.exceptions import ToolError
# was: from fastmcp.server.middleware import Middleware, MiddlewareContext

from mcp_server_snowflake.object_manager.tools import validate_object_tool
from mcp_server_snowflake.query_manager.tools import validate_sql_type


# class CheckQueryType(Middleware):
#     """Middleware that checks SQL statement to ensure it is of an approved type."""
#
#     def __init__(self, sql_allow_list: list[str], sql_disallow_list: list[str]):
#         self.sql_allow_list = sql_allow_list
#         self.sql_disallow_list = sql_disallow_list
#
#     async def on_call_tool(self, context: MiddlewareContext, call_next):
#         """Called for all MCP tool calls."""
#         tool_name = context.message.name
#
#         if tool_name.lower() == "run_snowflake_query" and context.message.arguments.get(
#             "statement", None
#         ):
#             statement_type, valid = validate_sql_type(
#                 context.message.arguments.get("statement", None),
#                 self.sql_allow_list,
#                 self.sql_disallow_list,
#             )
#         elif tool_name.lower().startswith("create") or tool_name.lower().startswith(
#             "drop"
#         ):
#             statement_type, valid = validate_object_tool(
#                 tool_name, self.sql_allow_list, self.sql_disallow_list
#             )
#         else:
#             valid = True
#
#         if valid:
#             return await call_next(context)
#         else:
#             raise ToolError(
#                 f"Statement type of {statement_type} is not allowed. Please review sql statement permissions in configuration file."
#             )
#
#
# def initialize_middleware(server: FastMCP, snowflake_service):
#     server.add_middleware(
#         CheckQueryType(
#             sql_allow_list=snowflake_service.sql_statement_allowed,
#             sql_disallow_list=snowflake_service.sql_statement_disallowed,
#         )
#     )


def install_query_check(server, sql_allow_list, sql_disallow_list):
    """Wrap already-registered SQL-touching tools with the allow/deny check.

    Call this AFTER initialize_tools(). Iterates server._tools (SecureMCP's
    internal registry) and replaces the handler of any tool that the original
    CheckQueryType middleware would have intercepted.

    Mirrors the middleware's dispatch:
      - "run_snowflake_query" -> check kwargs["statement"]
      - tool name starts with "create" or "drop" -> check by tool name only
      - everything else: untouched
    """
    for tool_name, info in server._tools.items():
        lname = tool_name.lower()
        original = info["handler"]

        if lname == "run_snowflake_query":
            info["handler"] = _wrap_statement_check(
                original, tool_name, sql_allow_list, sql_disallow_list
            )
        elif lname.startswith("create") or lname.startswith("drop"):
            info["handler"] = _wrap_object_check(
                original, tool_name, sql_allow_list, sql_disallow_list
            )


def _wrap_statement_check(fn, tool_name, allow, deny):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        statement = kwargs.get("statement")
        if statement:
            statement_type, valid = validate_sql_type(statement, allow, deny)
            if not valid:
                raise RuntimeError(
                    f"Statement type of {statement_type} is not allowed. "
                    "Please review sql statement permissions in configuration file."
                )
        return fn(*args, **kwargs)
    return wrapped


def _wrap_object_check(fn, tool_name, allow, deny):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        statement_type, valid = validate_object_tool(tool_name, allow, deny)
        if not valid:
            raise RuntimeError(
                f"Statement type of {statement_type} is not allowed. "
                "Please review sql statement permissions in configuration file."
            )
        return fn(*args, **kwargs)
    return wrapped
