"""Built-in generic MCP tools for YDB."""

import json
from enum import Enum
from typing import TYPE_CHECKING, Any

# Securemcp does not need
# from mcp.types import TextContent

from .params import _parse_params_str
from .serialization import serialize_ydb_response

if TYPE_CHECKING:
    from .server import YDBMCPServer


class YDBGenericTool(str, Enum):
    """Names of the built-in generic YDB tools."""

    QUERY = "ydb_query"
    QUERY_WITH_PARAMS = "ydb_query_with_params"
    EXPLAIN = "ydb_explain_query"
    EXPLAIN_WITH_PARAMS = "ydb_explain_query_with_params"
    STATUS = "ydb_status"
    LIST_DIRECTORY = "ydb_list_directory"
    DESCRIBE_PATH = "ydb_describe_path"

# TEXTCONTENT in not requreid MACAW -> json as result = {"result :"}
def register_generic_tools(server: "YDBMCPServer", enabled: set[YDBGenericTool]) -> None:
    """Register the built-in YDB tools with the SecureMCP server.

    :param enabled: set of tools to register; empty set registers nothing.

    PORT: was registering via server.add_tool(fn, name=..., description=...).
    SecureMCP exposes only a decorator factory (.tool()), so we use the
    decorator-as-function form server.mcp.tool(...)(fn). Tool bodies now
    return bare strings; SecureMCP auto-wraps as {"result": <str>}.
    """

    async def ydb_query(sql: str) -> str:
        """Run a SQL query against YDB database."""
        try:
            return serialize_ydb_response({"result_sets": await server.execute(sql)})
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def ydb_query_with_params(sql: str, params: str | dict) -> str:
        """Run a parameterized SQL query with JSON parameters."""
        try:
            result_sets = await server.execute(sql, _parse_params_str(params))
            return serialize_ydb_response({"result_sets": result_sets})
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def ydb_explain_query(sql: str) -> str:
        """Explain a SQL query against YDB."""
        try:
            return serialize_ydb_response(await server.explain(sql))
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def ydb_explain_query_with_params(sql: str, params: str | dict) -> str:
        """Explain a parameterized SQL query against YDB."""
        try:
            result = await server.explain(sql, _parse_params_str(params))
            return serialize_ydb_response(result)
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def ydb_status() -> str:
        """Get the current YDB connection status."""
        status: dict[str, Any] = {
            "status": "running",
            "ydb_endpoint": server.endpoint,
            "ydb_database": server.database,
            "auth_mode": server.auth_mode,
        }
        try:
            await server._ensure_connected()
            assert server._driver is not None
            details = server._driver.discovery_debug_details()
            if details.startswith("Resolved endpoints"):
                status["ydb_connection"] = "connected"
            else:
                status["ydb_connection"] = "error"
                status["error"] = details
        except Exception as e:
            status["ydb_connection"] = "error"
            status["error"] = str(e)
        return serialize_ydb_response(status)

    async def ydb_list_directory(path: str) -> str:
        """List directory contents in YDB."""
        try:
            return serialize_ydb_response(await server.list_directory(path))
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    async def ydb_describe_path(path: str) -> str:
        """Get detailed information about a YDB path (table, directory, etc.)."""
        try:
            return serialize_ydb_response(await server.describe_path(path))
        except Exception as e:
            return json.dumps({"error": str(e)}, indent=2)

    for tool, fn, description in [
        (YDBGenericTool.QUERY, ydb_query, "Run a SQL query against YDB database"),
        (YDBGenericTool.QUERY_WITH_PARAMS, ydb_query_with_params, "Run a parameterized SQL query with JSON parameters"),
        (YDBGenericTool.EXPLAIN, ydb_explain_query, "Explain a SQL query against YDB"),
        (YDBGenericTool.EXPLAIN_WITH_PARAMS, ydb_explain_query_with_params,
         "Explain a parameterized SQL query against YDB"),
        (YDBGenericTool.STATUS, ydb_status, "Get the current YDB connection status"),
        (YDBGenericTool.LIST_DIRECTORY, ydb_list_directory, "List directory contents in YDB"),
        (YDBGenericTool.DESCRIBE_PATH, ydb_describe_path, "Get detailed information about a YDB path"),
    ]:
        if tool in enabled:
            # PORT: was server.add_tool(fn, name=..., description=...).
            # SecureMCP exposes only the decorator-factory form, so we use
            # the decorator-as-function: server.mcp.tool(...)(fn).
            server.mcp.tool(name=tool.value, description=description)(fn)
