"""PostgreSQL MCP Server.

This server exposes PostgreSQL database functionality through MCP:
- Resources: Table schemas and metadata
- Tools: Read-only SQL query execution
- Prompts: Common data analysis tasks
"""

import asyncio
import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import psycopg
from dotenv import load_dotenv
from psycopg import sql
from psycopg.rows import dict_row

# from mcp.server.fastmcp import Context, FastMCP
# from mcp.server.session import ServerSession

from macaw_adapters.mcp import SecureMCP, Context  
# Fix for Windows: psycopg requires SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# @dataclass
# class DatabaseContext:
#     """Database connection context."""

#     conn: psycopg.AsyncConnection[dict[str, Any]]


# @asynccontextmanager
# async def database_lifespan(server: FastMCP) -> AsyncIterator[DatabaseContext]:
#     """Manage database connection lifecycle."""
#     # Try to get DATABASE_URL first, otherwise construct from individual components
#     database_url = os.getenv("DATABASE_URL")

#     if not database_url:
#         # Construct from individual components
#         db_host = os.getenv("DATABASE_HOST", "localhost")
#         db_user = os.getenv("DATABASE_USER", "postgres")
#         db_password = os.getenv("DATABASE_PASSWORD", "")
#         db_port = os.getenv("DATABASE_PORT", "5432")
#         db_name = os.getenv("DATABASE_NAME", "postgres")

#         if not db_password:
#             raise ValueError(
#                 "DATABASE_PASSWORD is required. Set DATABASE_PASSWORD or DATABASE_URL in .env file"
#             )

#         database_url = (
#             f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
#         )
#         logger.info("Constructed database URL from individual components")
#     else:
#         # Remove SQLAlchemy-specific prefix if present
#         database_url = database_url.replace("postgresql+psycopg://", "postgresql://")

#     logger.info(
#         f"Connecting to PostgreSQL database at {os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}..."
#     )
#     conn: psycopg.AsyncConnection[dict[str, Any]] | None = None
#     try:
#         conn = await psycopg.AsyncConnection.connect(
#             database_url,
#             row_factory=dict_row,  # type: ignore[arg-type]
#             autocommit=True,
#         )
#         if conn is None:
#             raise RuntimeError("Failed to establish database connection")
#         logger.info("✓ Connected to PostgreSQL database successfully")
#         yield DatabaseContext(conn=conn)
#     except psycopg.OperationalError as e:
#         logger.error(f"Database connection error: {e}")
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error during database connection: {e}")
#         raise
#     finally:
#         if conn is not None:
#             await conn.close()
#             logger.info("Database connection closed")


# Initialize FastMCP server with database lifespan
# mcp = FastMCP("PostgreSQL Server", lifespan=database_lifespan)

def get_database_url() -> str:

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_user = os.getenv("DATABASE_USER", "postgres")
        db_password = os.getenv("DATABASE_PASSWORD", "")
        db_port = os.getenv("DATABASE_PORT", "5432")
        db_name = os.getenv("DATABASE_NAME", "postgres")

        if not db_password:
            raise ValueError("DATABASE_PASSWORD is required in .env file")
        
        database_url=f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        database_url = database_url.replace("postgresql+psycopg://", "postgresql://")

    return database_url

@asynccontextmanager
async def get_db_connection() -> AsyncIterator[psycopg.AsyncConnection[dict[str,Any]]]:
    url  = get_database_url()
    conn = None
    try:
        conn = await psycopg.AsyncConnection.connect(
            url,
            row_factory=dict_row,
            autocommit=True,
        )
        yield conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn is not None:
            # clean agter tool 
            await conn.close()

mcp = SecureMCP("securemcp-postgreSql")

# Simple test resource to verify resources work
@mcp.resource(
    "postgres://info",

    description="PostgreSQL server information",
)
def server_info() -> str:
    """Get server information."""
    return """# PostgreSQL MCP Server

This server provides access to your PostgreSQL database through MCP.

## Available Operations:
- **Resources**: Browse table schemas
- **Tools**: Execute read-only queries and get statistics
- **Prompts**: Data analysis workflows

## Database: matchmaking_db
## Tables: projects, staff, students, users
"""


# Convert database operations to tools (resources don't support async + Context)


@mcp.tool()
async def list_tables(
    # ctx: Context[ServerSession, DatabaseContext]
    ) -> dict[str, Any]:
    """List all tables in the database.

    Returns:
        Dictionary with list of tables and their types
    """



    query = """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                tables = await cur.fetchall()

                if tables:
                    return tables
    except Exception as e:
        logger.exception("Failed to list tables")
        raise




@mcp.tool()
async def get_table_schema(
    table_name: str,
    # ctx: Context[ServerSession, DatabaseContext],
) -> dict[str, Any]:
    """Get the schema for a specific table.

    Args:
        table_name: Name of the table to describe

    Returns:
        Dictionary with table schema information
    """
    # db = ctx.request_context.lifespan_context.conn

    query = """
        SELECT
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position;
    """


    try:
      async with get_db_connection() as db: 
        async with db.cursor() as cur:
            await cur.execute(query, (table_name,))
            columns = await cur.fetchall()

        if not columns:
            return {
                "error": f"Table '{table_name}' not found",
                "table_name": table_name,
                "columns": [],
            }

        return {
            "table_name": table_name,
            "columns": columns,
            "column_count": len(columns),
        }
    except Exception:
        logger.exception("Failed to get table schema for %s", table_name)
        raise


@mcp.tool()
async def execute_query(
    query: str,
    # ctx: Context[ServerSession, DatabaseContext],
) -> dict[str, Any]:
    """Execute a read-only SQL query and return results.

    Args:
        query: SQL query to execute (must be SELECT, WITH, or SHOW statement)

    Returns:
        Dictionary containing rows and metadata
    """
    # db = ctx.request_context.lifespan_context.conn

    # Ensure query is read-only
    query_upper = query.strip().upper()
    if not any(query_upper.startswith(prefix) for prefix in ("SELECT", "WITH", "SHOW")):
        return {
            "error": "Only SELECT, WITH, and SHOW queries are allowed",
            "rows": [],
            "row_count": 0,
        }

    try:
      async with get_db_connection() as db:
        async with db.cursor() as cur:
            await cur.execute(sql.SQL(query))  # type: ignore[arg-type]
            rows = await cur.fetchall()
        for row in rows:
                    for key, value in row.items():
                        # If it's not a standard JSON-friendly type, force it to be a string
                        if not isinstance(value, (str, int, float, bool, type(None))):
                            row[key] = str(value)

        return {
            "rows": rows,
            "row_count": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
        }
    except Exception:
        logger.exception("Failed to execute query")
        raise


@mcp.tool()
async def get_table_stats(
    table_name: str,
    # ctx: Context[ServerSession, DatabaseContext],
) -> dict[str, Any]:
    """Get statistics for a table.

    Args:
        table_name: Name of the table to analyze

    Returns:
        Dictionary containing table statistics
    """
    # db = ctx.request_context.lifespan_context.conn

    try:
      async with get_db_connection() as db:
        async with db.cursor() as cur:
            count_query = sql.SQL("SELECT COUNT(*) as count FROM {}").format(
                sql.Identifier(table_name)
            )
            await cur.execute(count_query)  # type: ignore[arg-type]
            count_result = await cur.fetchone()
            row_count = count_result["count"] if count_result else 0

       
        async with db.cursor() as cur:
            await cur.execute(
                sql.SQL(
                    """
                SELECT
                    pg_size_pretty(pg_total_relation_size(%s)) as total_size,
                    pg_size_pretty(pg_relation_size(%s)) as table_size,
                    pg_size_pretty(pg_indexes_size(%s)) as indexes_size
                """
                ),  # type: ignore[arg-type]
                (table_name, table_name, table_name),
            )
            size_result = await cur.fetchone()

        return {
            "table_name": table_name,
            "row_count": row_count,
            "total_size": size_result["total_size"] if size_result else "Unknown",
            "table_size": size_result["table_size"] if size_result else "Unknown",
            "indexes_size": size_result["indexes_size"] if size_result else "Unknown",
        }
    except Exception:
        logger.exception("Failed to get table stats for %s", table_name)
        raise


@mcp.prompt()
def analyze_table(table_name: str) -> str:
    """Generate a prompt for analyzing a table.

    Args:
        table_name: Name of the table to analyze
    """
    return f"""Please analyze the table '{table_name}' in the database.

1. First, get the table schema to understand its structure
2. Get table statistics to understand its size and distribution
3. Examine a sample of rows to understand the data
4. Provide insights about:
   - Data quality
   - Potential issues or anomalies
   - Interesting patterns or trends
   - Suggestions for optimization

Use the available tools to gather this information."""


@mcp.prompt()
def find_relationships() -> str:
    """Generate a prompt for finding table relationships."""
    return """Please analyze the database to find relationships between tables.

1. List all tables in the database
2. Examine the schemas of each table
3. Look for:
   - Foreign key columns (typically ending in _id)
   - Common column names across tables
   - Potential join conditions
4. Create a summary of the database structure showing:
   - How tables relate to each other
   - The data model hierarchy
   - Any missing relationships that should exist

Use the available tools to gather this information."""


@mcp.prompt()
def data_quality_check() -> str:
    """Generate a prompt for checking data quality."""
    return """Please perform a comprehensive data quality check on the database.

For each table:
1. Check for NULL values in important columns
2. Look for duplicate records
3. Verify data types are appropriate
4. Check for outliers or anomalous values
5. Examine value distributions

Provide a summary report highlighting any data quality issues found
and recommendations for improvement.

Use the available tools to gather this information."""


def main() -> None:
    """Run the MCP server."""
    logger.info("Starting PostgreSQL MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
