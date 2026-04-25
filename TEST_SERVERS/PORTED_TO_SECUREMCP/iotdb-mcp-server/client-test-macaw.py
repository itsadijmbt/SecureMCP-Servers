"""
MACAW client smoke test for iotdb-mcp-server (post FastMCP -> SecureMCP port).

Usage:
    python3.11 client-test-macaw.py iotdb_mcp_server iotdb-test-client

The first arg is a substring to match against the server's MACAW agent_id
(server registers as `securemcp-iotdb_mcp_server:<hash>`).  The second arg
is just a name for THIS client process.

This script auto-detects which sql_dialect the server was started in
(`tree` or `table`) by inspecting the registered tool names, and runs
dialect-appropriate tests.
"""

from macaw_adapters.mcp import Client
import asyncio
import sys


def get_server(client, name):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
    ]

    if not server:
        print(f"No server found matching: {name}")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print("Usage: python3 client-test-macaw.py <server_filter_name> <client_name>")
        print("Example: python3 client-test-macaw.py iotdb_mcp_server iotdb-test-client")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]

    client = Client(client_type)
    server_id = get_server(client, name)

    if not server_id:
        return

    client.set_default_server(server_id)

    # List all tools the server registered.
    tools = await client.list_tools(server_name=name)
    seen = set()
    print("Tools advertised by server:")
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            print(f" - {t['name']}")

    # Detect dialect by tool names.
    is_table_dialect = "list_tables" in seen
    is_tree_dialect = "metadata_query" in seen

    print("\n" + "=" * 50)
    print("IOTDB-MCP TOOL TESTS")
    print("=" * 50)
    # ============================================================
    # NOTE: iotdb-mcp-server never had MCP-caller authentication.
    # The upstream relied on IoTDB's own user/password (passed via
    # config) to authenticate the SERVER -> IOTDB connection, but
    # there was no MCP-layer bearer/JWT/OAuth check on incoming
    # tool calls.  The SecureMCP port did not delete an auth layer
    # because there wasn't one to delete.
    #
    # Under MACAW the missing piece is filled in for free: every
    # incoming invocation is cryptographically signed by the caller
    # and validated by the Local Agent before the handler runs.
    # That is a security upgrade the original server didn't have.
    #
    # Every TEST below succeeding is implicitly proof that:
    #   - the caller's MACAW signature was valid,
    #   - MAPL policy did not deny the call,
    #   - the audit entry was written (visible in MACAW console),
    #   - the FastMCP -> SecureMCP port was successful.
    # ============================================================

    if is_table_dialect:
        await run_table_dialect_tests(client)
    elif is_tree_dialect:
        await run_tree_dialect_tests(client)
    else:
        print("\nNo recognized dialect tools found.")
        print("Expected either 'list_tables' (table dialect) or 'metadata_query' (tree dialect).")
        print("Check the server's IOTDB_SQL_DIALECT env variable.")

    print("\nAll tests done.")


# ----------------------------------------------------------------
# TABLE DIALECT TESTS
# Triggered when sql_dialect=table.
# Tools available: read_query, list_tables, describe_table,
#                  export_table_query
# ----------------------------------------------------------------
async def run_table_dialect_tests(client):
    print("\n[Table dialect detected]")

    # TEST 1 — list_tables (zero args).
    # If IoTDB is reachable, returns a CSV string of tables.
    # If not, the handler raises and you'll see the connection error.
    print("\n[TEST 1] list_tables — list every table in the IoTDB database")
    try:
        result = await client.call_tool("list_tables", {})
        preview = str(result)[:300].replace("\n", " | ")
        print(f"  Result: {preview}")
    except Exception as e:
        print(f"  Failed: {e}")

    # TEST 2 — read_query with SELECT 1.
    # Simplest valid SELECT.  Doesn't depend on any specific table.
    print("\n[TEST 2] read_query — SELECT 1 (smoke test, no table required)")
    try:
        result = await client.call_tool("read_query", {"query_sql": "SELECT 1"})
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Failed: {e}")

    # TEST 3 — read_query with SHOW.
    # SHOW is in the allowlist (handler accepts SELECT/DESCRIBE/SHOW).
    print("\n[TEST 3] read_query — SHOW TABLES (allowlisted)")
    try:
        result = await client.call_tool("read_query", {"query_sql": "SHOW TABLES"})
        preview = str(result)[:300].replace("\n", " | ")
        print(f"  Result: {preview}")
    except Exception as e:
        print(f"  Failed: {e}")

    # TEST 4 — read_query with INSERT (read-only enforcement).
    # Handler checks the first SQL keyword against an allowlist
    # (SELECT / SHOW / DESCRIBE / DESC).  An INSERT should be
    # rejected by the handler BEFORE any IoTDB connection happens,
    # which means this test passes even when IoTDB is unreachable.
    # That makes it the cleanest single proof that the port works.
    print("\n[TEST 4] read_query — write attempt (should be rejected)")
    try:
        result = await client.call_tool(
            "read_query",
            {"query_sql": "INSERT INTO root.foo VALUES (1, 'a')"},
        )
        print(f"  Result: {result}")
        result_text = str(result).lower()
        if "only select" in result_text or "not allowed" in result_text:
            print("  PASS: read-only filter is intact, port verified")
        else:
            print("  WARN: write query was not rejected — check handler filter")
    except ValueError as e:
        # Handler raises ValueError("Only SELECT queries are allowed for read_query").
        # MACAW propagates as an exception on the client side.
        msg = str(e).lower()
        if "only select" in msg or "not allowed" in msg:
            print(f"  PASS: rejected with ValueError ({e!s})")
            print("  Read-only filter intact, port verified")
        else:
            print(f"  Unexpected ValueError: {e}")
    except Exception as e:
        print(f"  Failed: {e}")


# ----------------------------------------------------------------
# TREE DIALECT TESTS
# Triggered when sql_dialect=tree (the IoTDB default).
# Tools available: metadata_query, select_query, export_query
# ----------------------------------------------------------------
async def run_tree_dialect_tests(client):
    print("\n[Tree dialect detected]")

    # TEST 1 — metadata_query with SHOW DATABASES root.**.
    # The simplest metadata query.  Returns the list of databases
    # under the root.** path.
    print("\n[TEST 1] metadata_query — SHOW DATABASES root.**")
    try:
        result = await client.call_tool(
            "metadata_query",
            {"query_sql": "SHOW DATABASES root.**"},
        )
        preview = str(result)[:300].replace("\n", " | ")
        print(f"  Result: {preview}")
    except Exception as e:
        print(f"  Failed: {e}")

    # TEST 2 — metadata_query with COUNT TIMESERIES root.**.
    # Returns a count even when no timeseries exist (returns 0).
    # Useful sanity check.
    print("\n[TEST 2] metadata_query — COUNT TIMESERIES root.**")
    try:
        result = await client.call_tool(
            "metadata_query",
            {"query_sql": "COUNT TIMESERIES root.**"},
        )
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Failed: {e}")

    # TEST 3 — select_query with a simple SELECT.
    # IoTDB's tree dialect requires a path; this is a minimal one.
    # Will likely return empty or error if no data exists, which
    # is fine — we're testing dispatch, not data.
    print("\n[TEST 3] select_query — SELECT * FROM root.** LIMIT 1")
    try:
        result = await client.call_tool(
            "select_query",
            {"query_sql": "SELECT * FROM root.** LIMIT 1"},
        )
        preview = str(result)[:300].replace("\n", " | ")
        print(f"  Result: {preview}")
    except Exception as e:
        print(f"  Failed: {e}")

    # TEST 4 — metadata_query with unsupported query (rejection test).
    # The handler accepts only:
    #   SHOW DATABASES, SHOW TIMESERIES, SHOW CHILD PATHS,
    #   SHOW CHILD NODES, SHOW DEVICES,
    #   COUNT TIMESERIES, COUNT NODES, COUNT DEVICES
    # Anything else hits the else-branch and raises:
    #   ValueError("Unsupported metadata query. ...")
    # This proves the handler ran (port verified) without IoTDB.
    print("\n[TEST 4] metadata_query — unsupported query (should be rejected)")
    try:
        result = await client.call_tool(
            "metadata_query",
            {"query_sql": "DESCRIBE root.foo"},
        )
        print(f"  Result: {result}")
        result_text = str(result).lower()
        if "unsupported" in result_text:
            print("  PASS: unsupported-query filter is intact, port verified")
        else:
            print("  WARN: unsupported query was not rejected — check handler filter")
    except ValueError as e:
        msg = str(e).lower()
        if "unsupported" in msg:
            print(f"  PASS: rejected with ValueError ({e!s})")
            print("  Unsupported-query filter intact, port verified")
        else:
            print(f"  Unexpected ValueError: {e}")
    except Exception as e:
        print(f"  Failed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
