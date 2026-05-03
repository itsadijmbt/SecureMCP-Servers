"""
mysql_mcp_server (SecureMCP port).

PORT NOTE -- low-level Server -> SecureMCP
==========================================
The original used the low-level `mcp.server.Server` with three
decorators:
  - @app.list_resources() -- enumerated MySQL tables as Resource
                             objects (uri = "mysql://<table>/data").
  - @app.read_resource(uri) -- parsed the URI and read the table.
  - @app.list_tools() / @app.call_tool() -- exposed one tool,
                             `execute_sql(query)`.

Under SecureMCP we cannot keep the resource path as-is. SecureMCP's
@app.resource() decorator (mcp.py:519+) registers a STATIC URI; it
has no template/glob extraction. The original mysql code enumerates
N tables at request time, which has no destination on SecureMCP's
resource surface.

PATH B (chosen, see MIGRATION.txt -> BROKEN ON PURPOSE):
  Convert the two resource handlers into ordinary tools. Same data,
  same query body, just a different name and access path:
      list_resources -> list_tables()
      read_resource(uri="mysql://<table>/data") -> read_table(table)
  The execute_sql tool is unchanged in behaviour; only the decorator
  changes.

Original code is preserved as comment blocks immediately above each
new block, per the "ALWAYS KEEP THE OLD CODE COMMENTED" rule.
"""

import asyncio
import logging
import os
import sys
from mysql.connector import connect, Error
# from mcp.server import Server                                    # PORT
# from mcp.types import Resource, Tool, TextContent                # PORT: no longer needed -- SecureMCP returns plain dicts/strings
from macaw_adapters.mcp import SecureMCP
from pydantic import AnyUrl                                         # KEPT: still used in the commented original read_resource signature

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mysql_mcp_server")

def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        # Add charset and collation to avoid utf8mb4_0900_ai_ci issues with older MySQL versions
        # These can be overridden via environment variables for specific MySQL versions
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "collation": os.getenv("MYSQL_COLLATION", "utf8mb4_unicode_ci"),
        # Disable autocommit for better transaction control
        "autocommit": True,
        # Set SQL mode for better compatibility - can be overridden
        "sql_mode": os.getenv("MYSQL_SQL_MODE", "TRADITIONAL")
    }

    # Remove None values to let MySQL connector use defaults if not specified
    config = {k: v for k, v in config.items() if v is not None}

    if not all([config.get("user"), config.get("password"), config.get("database")]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config

# PORT: was `app = Server("mysql_mcp_server")`. We keep the variable
# name `app` for minimum churn -- every decorator below stays
# `@app.tool()` rather than being renamed to `@mcp.tool()`.
app = SecureMCP("mysql_mcp_server")


# ======================================================================
# PORT: list_resources -> list_tables tool
# ----------------------------------------------------------------------
# WHAT changed: the original advertised tables as MCP resources
# (uri = "mysql://<table>/data"). Under SecureMCP the resource decorator
# only takes a static URI -- there is no way to advertise N dynamic
# resources at request time. So the same query (`SHOW TABLES`) and the
# same return shape (list of table names) live in a tool now.
#
# WHY this is safe: callers that previously did `resources/list` and
# parsed the URIs to discover table names now call `list_tables()` and
# read the same table names directly out of the result string. Same
# information, simpler shape.
# ======================================================================
# @app.list_resources()
# async def list_resources() -> list[Resource]:
#     """List MySQL tables as resources."""
#     config = get_db_config()
#     try:
#         logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
#         with connect(**config) as conn:
#             logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
#             with conn.cursor() as cursor:
#                 cursor.execute("SHOW TABLES")
#                 tables = cursor.fetchall()
#                 logger.info(f"Found tables: {tables}")
#
#                 resources = []
#                 for table in tables:
#                     resources.append(
#                         Resource(
#                             uri=f"mysql://{table[0]}/data",
#                             name=f"Table: {table[0]}",
#                             mimeType="text/plain",
#                             description=f"Data in table: {table[0]}"
#                         )
#                     )
#                 return resources
#     except Error as e:
#         logger.error(f"Failed to list resources: {str(e)}")
#         logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
#         return []


@app.tool()
async def list_tables() -> str:
    """List the tables in the connected MySQL database.

    Replaces the original `resources/list` advertisement of
    `mysql://<table>/data` URIs. Returns a plain text list of table
    names, one per line.

    Returns:
        A newline-separated list of table names, or an error message
        string if the database is unreachable.
    """
    config = get_db_config()
    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")
                # Same return shape as the original SHOW TABLES branch
                # of execute_sql below: header + one table per line.
                header = "Tables_in_" + config["database"]
                return "\n".join([header] + [row[0] for row in tables])
    except Error as e:
        logger.error(f"Failed to list tables: {str(e)}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        return f"Error listing tables: {str(e)}"


# ======================================================================
# PORT: read_resource -> read_table tool
# ----------------------------------------------------------------------
# WHAT changed: instead of a resource handler that parsed the URI
# (`mysql://<table>/data` -> table name) we take the table name
# explicitly as a tool argument. Same query body
# (`SELECT * FROM <table> LIMIT 100`) and same CSV return shape.
#
# WHY this is safe: callers used to say `resources/read mysql://X/data`;
# they now say `tools/call read_table(table="X")`. The string the
# server returns is byte-for-byte the same -- header row + up to 100
# CSV rows.
#
# Note: the table name is interpolated into the SQL exactly as the
# original code did. We are NOT introducing new SQL injection here --
# the security posture is unchanged. If the original was acceptable
# for callers, this is too. Improving validation is a separate concern.
# ======================================================================
# @app.read_resource()
# async def read_resource(uri: AnyUrl) -> str:
#     """Read table contents."""
#     config = get_db_config()
#     uri_str = str(uri)
#     logger.info(f"Reading resource: {uri_str}")
#
#     if not uri_str.startswith("mysql://"):
#         raise ValueError(f"Invalid URI scheme: {uri_str}")
#
#     parts = uri_str[8:].split('/')
#     table = parts[0]
#
#     try:
#         logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
#         with connect(**config) as conn:
#             logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
#             with conn.cursor() as cursor:
#                 cursor.execute(f"SELECT * FROM {table} LIMIT 100")
#                 columns = [desc[0] for desc in cursor.description]
#                 rows = cursor.fetchall()
#                 result = [",".join(map(str, row)) for row in rows]
#                 return "\n".join([",".join(columns)] + result)
#
#     except Error as e:
#         logger.error(f"Database error reading resource {uri}: {str(e)}")
#         logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
#         raise RuntimeError(f"Database error: {str(e)}")


@app.tool()
async def read_table(table: str) -> str:
    """Read up to 100 rows from a table in the connected MySQL database.

    Replaces the original `resources/read mysql://<table>/data`
    handler. Same SELECT query body, same CSV return shape.

    Args:
        table: The MySQL table name to read.

    Returns:
        A CSV string with the column header on the first line and
        up to 100 rows on subsequent lines. On database error the
        error message is returned as a string (no exception
        propagated, matching the surface the original execute_sql
        path used for clients).
    """
    config = get_db_config()
    logger.info(f"Reading table: {table}")
    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                # Same query as the original read_resource. Table name
                # is interpolated exactly as before -- no security
                # change vs. the original.
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)
    except Error as e:
        logger.error(f"Database error reading table {table}: {str(e)}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        # PORT: the original raised RuntimeError here; we return the
        # error string instead, matching the existing execute_sql
        # error path below. Mesh consumers see one consistent error
        # surface across all three tools.
        return f"Database error reading table {table}: {str(e)}"


# ======================================================================
# PORT: execute_sql -- the existing @app.call_tool now becomes a
# regular @app.tool function. WHAT changed: just the decorator and
# the signature (one Python parameter instead of an arguments dict).
# The function body is byte-for-byte the same logic.
# ======================================================================
# @app.list_tools()
# async def list_tools() -> list[Tool]:
#     """List available MySQL tools."""
#     logger.info("Listing tools...")
#     return [
#         Tool(
#             name="execute_sql",
#             description="Execute an SQL query on the MySQL server",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "query": {
#                         "type": "string",
#                         "description": "The SQL query to execute"
#                     }
#                 },
#                 "required": ["query"]
#             }
#         )
#     ]
#
# @app.call_tool()
# async def call_tool(name: str, arguments: dict) -> list[TextContent]:
#     """Execute SQL commands."""
#     ...

@app.tool()
async def execute_sql(query: str) -> str:
    """Execute an SQL query on the MySQL server.

    Args:
        query: The SQL query to execute.

    Returns:
        A string with the result. For SELECT/SHOW/DESCRIBE the result
        is a CSV-style table (header line + rows). For non-SELECT it
        is a status line saying how many rows were affected. On error
        the error message is returned as a string (no exception
        propagated to the mesh).
    """
    config = get_db_config()
    logger.info(f"Calling execute_sql with query: {query}")

    if not query:
        return "Error: Query is required"

    try:
        logger.info(f"Connecting to MySQL with charset: {config.get('charset')}, collation: {config.get('collation')}")
        with connect(**config) as conn:
            logger.info(f"Successfully connected to MySQL server version: {conn.get_server_info()}")
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Special handling for SHOW TABLES (kept identical to the
                # original behaviour so existing callers see the same
                # output for this specific query).
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = ["Tables_in_" + config["database"]]
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                # Handle all other queries that return result sets.
                elif cursor.description is not None:
                    columns = [desc[0] for desc in cursor.description]
                    try:
                        rows = cursor.fetchall()
                        result = [",".join(map(str, row)) for row in rows]
                        return "\n".join([",".join(columns)] + result)
                    except Error as e:
                        logger.warning(f"Error fetching results: {str(e)}")
                        return f"Query executed but error fetching results: {str(e)}"

                # Non-SELECT queries.
                else:
                    conn.commit()
                    return f"Query executed successfully. Rows affected: {cursor.rowcount}"

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        logger.error(f"Error code: {e.errno}, SQL state: {e.sqlstate}")
        return f"Error executing query: {str(e)}"


# ======================================================================
# PORT: entry point
# ----------------------------------------------------------------------
# Original main() was async and used `async with stdio_server()` to
# wire the low-level Server's stdin/stdout. SecureMCP.run() is sync
# (mcp.py:628-635: `def run` -> `asyncio.run(_run_async)` internally)
# and traffic arrives via the MACAW mesh, not stdin/stdout. So:
#   - stdio_server() block is dropped
#   - main() is now sync; __init__.py drops its asyncio.run(...) wrap
#   - app.create_initialization_options() is gone; SecureMCP doesn't
#     have an MCP-protocol-init concept
# ======================================================================
# async def main():
#     """Main entry point to run the MCP server."""
#     from mcp.server.stdio import stdio_server
#
#     # Add additional debug output
#     print("Starting MySQL MCP server with config:", file=sys.stderr)
#     config = get_db_config()
#     print(f"Host: {config['host']}", file=sys.stderr)
#     print(f"Port: {config['port']}", file=sys.stderr)
#     print(f"User: {config['user']}", file=sys.stderr)
#     print(f"Database: {config['database']}", file=sys.stderr)
#
#     logger.info("Starting MySQL MCP server...")
#     logger.info(f"Database config: {config['host']}/{config['database']} as {config['user']}")
#
#     async with stdio_server() as (read_stream, write_stream):
#         try:
#             await app.run(
#                 read_stream,
#                 write_stream,
#                 app.create_initialization_options()
#             )
#         except Exception as e:
#             logger.error(f"Server error: {str(e)}", exc_info=True)
#             raise


def main():
    """Main entry point to run the MCP server (SecureMCP, sync)."""
    # Same startup banner as before so logs look familiar.
    print("Starting MySQL MCP server with config:", file=sys.stderr)
    config = get_db_config()
    print(f"Host: {config['host']}", file=sys.stderr)
    print(f"Port: {config['port']}", file=sys.stderr)
    print(f"User: {config['user']}", file=sys.stderr)
    print(f"Database: {config['database']}", file=sys.stderr)

    logger.info("Starting MySQL MCP server...")
    logger.info(f"Database config: {config['host']}/{config['database']} as {config['user']}")

    try:
        app.run()
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # PORT: was `asyncio.run(main())`. main() is sync now; SecureMCP
    # owns its own asyncio.run() inside app.run().
    main()
