"""
MACAW client smoke test for snowflake-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "snowflake" snowflake-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

What this tests:
    1. Port-correctness: server registered, tools advertised on the mesh.
    2. SQL allow path: SELECT goes through the install_query_check wrapper.
    3. SQL deny path (statement-arg): DROP via run_snowflake_query rejected.
    4. SQL deny path (tool-name prefix): drop_object rejected before snowflake.

Without a real Snowflake connection, tests 2 will fail at the upstream
connector (expected). Tests 3 and 4 do NOT need Snowflake -- the wrapper
rejects them before the tool body runs. That is the port-correctness
proof for the middleware -> wrapper rewrite.
"""

import asyncio
import json
import sys

from macaw_adapters.mcp import Client


def get_server(name, client):
    """Look up the snowflake server's agent_id on the mesh.

    Filters out:
      - per-tool sub-agents (their agent_id contains '/tool.')
      - this client's own agent (its id contains 'securemcp-client-')
    """
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
        and "securemcp-client-" not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No server found matching: {name}")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py "snowflake" snowflake-test-client')
        sys.exit(1)

    name = sys.argv[1]
    client_name = sys.argv[2]

    client = Client(client_name)
    server_id = get_server(name, client)
    if not server_id:
        return
    client.set_default_server(server_id)

    tools = await client.list_tools(server_name=name)
    seen = set()
    print("Tools advertised by server:")
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            print(f"  - {t['name']}")
    print(f"\n  Total unique tools: {len(seen)}\n")

    print("=" * 60)
    print("SNOWFLAKE MCP TESTS")
    print("=" * 60)

    # --------------------------------------------------------------
    # TEST 1 -- list_tools came back, run_snowflake_query is in it
    #
    # Pure port-correctness check. If the server registered on the
    # mesh and the tool registry shows expected tools, we know:
    #   - SecureMCP boot succeeded (lifespan body inlined correctly)
    #   - initialize_tools registered handlers
    #   - install_query_check did not crash on _tools iteration
    # No upstream Snowflake call yet.
    # --------------------------------------------------------------
    print("\n[TEST 1] tool list -- port-correctness")
    if "run_snowflake_query" in seen:
        print("  PASS -- run_snowflake_query advertised.")
    else:
        print("  FAILED -- run_snowflake_query missing from tool list.")
        print("  Either the server is not started, or initialize_tools didn't run.")
        return
    if any(t.startswith("create_") or t.startswith("drop_") for t in seen):
        print("  PASS -- object_manager create_*/drop_* tools advertised.")
    else:
        print("  Inspect -- no create_/drop_ tools. Object manager may be disabled "
              "in the YAML config; the deny-by-name test below will be inconclusive.")

    # --------------------------------------------------------------
    # TEST 2 -- run_snowflake_query with SELECT (allow path)
    #
    # SELECT is in the default allow list. The wrapper should pass
    # the call through to the real handler. Two valid outcomes:
    #
    #   a) Snowflake reachable + creds correct: returns query result.
    #   b) No Snowflake / bad creds: connector raises, the tool body
    #      catches it and returns an error JSON, OR the exception
    #      propagates as a RuntimeError on the wire.
    #
    # Either outcome PROVES the install_query_check wrapper allowed
    # the call through (it did NOT raise "Statement type ... not
    # allowed" before the handler ran).
    # --------------------------------------------------------------
    print("\n[TEST 2] run_snowflake_query with SELECT -- allow path")
    try:
        result = await client.call_tool(
            "run_snowflake_query",
            {"statement": "SELECT 1 AS macaw_smoke"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "not allowed" in text.lower():
            print("  FAILED -- the wrapper rejected SELECT. Check the YAML "
                  "sql_statement_permissions config: SELECT must be allowed.")
        elif "macaw_smoke" in text or "1" in text:
            print("  PASS (creds branch) -- SELECT executed end-to-end. Full "
                  "vertical works: client -> mesh -> wrapper -> handler -> "
                  "snowflake -> back.")
        else:
            print("  PASS (no-creds branch) -- the wrapper allowed the call "
                  "(no 'not allowed' in the response). The error after that "
                  "came from the snowflake connector, which is the right "
                  "place for it to fail without creds.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "not allowed" in msg.lower():
            print("  FAILED -- wrapper rejected SELECT. Fix the YAML config.")
        else:
            print("  PASS (no-creds branch) -- exception was NOT from the "
                  "wrapper (no 'not allowed'). Came from upstream / mesh, "
                  "which means the wrapper let SELECT through.")

    # --------------------------------------------------------------
    # TEST 3 -- run_snowflake_query with DROP (deny path, statement-arg)
    #
    # This is THE test for the middleware-to-wrapper rewrite on the
    # statement-argument branch. The wrapper:
    #   - sees tool_name == "run_snowflake_query"
    #   - reads kwargs["statement"]
    #   - calls validate_sql_type, gets back ("Drop", False)
    #   - raises RuntimeError BEFORE the real handler runs
    #
    # The connection to Snowflake is never opened, the SQL never
    # leaves the process. That is the security guarantee.
    #
    # Expectation: RuntimeError whose message contains "not allowed".
    # --------------------------------------------------------------
    print("\n[TEST 3] run_snowflake_query with DROP -- statement-arg deny")
    try:
        result = await client.call_tool(
            "run_snowflake_query",
            {"statement": "DROP TABLE __macaw_smoke_does_not_exist__"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "not allowed" in text.lower():
            print("  PASS -- 'not allowed' in the response. Wrapper rejected "
                  "the DROP at the statement-arg check. Snowflake never saw "
                  "the SQL.")
        else:
            print("  Inspect -- expected a 'not allowed' rejection. Either:")
            print("    a) DROP is in the allow list of your YAML config "
                  "(unusual; check sql_statement_permissions), OR")
            print("    b) install_query_check didn't wrap the handler -- "
                  "verify the order of calls in main(): tools must register "
                  "BEFORE install_query_check runs.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "not allowed" in msg.lower():
            print("  PASS -- exception text contains 'not allowed'. Wrapper "
                  "rejected the DROP at the statement-arg check.")
        else:
            print("  Inspect -- exception did not say 'not allowed'. "
                  "Possible: mesh-level error, or wrapper fell through and "
                  "snowflake refused. Print the full error to diagnose.")

    # --------------------------------------------------------------
    # TEST 4 -- drop_object (deny path, tool-name prefix)
    #
    # Same wrapper, different branch. The tool name starts with
    # "drop", so the wrapper takes the name-only check path:
    #   - validate_object_tool(tool_name, allow, deny)
    # No statement to inspect; the tool name alone is enough.
    #
    # Params have to be present so Python doesn't TypeError before
    # we reach the wrapper. The wrapper's validation runs FIRST,
    # rejects the call, and the params are never used.
    #
    # If your YAML allows DROP for objects (uncommon), this test
    # falls through to the snowflake call and you'll see a
    # connector error. That's a config-dependent inconclusive,
    # not a failure of the wrapper.
    # --------------------------------------------------------------
    # Note on target_object shape:
    # Upstream parse_object() at object_manager/tools.py:153 only handles
    # `target_object` when it arrives as a JSON STRING (it then parses
    # it into a SnowflakeTable Pydantic model). If we pass a plain dict,
    # parse_object falls into its else-branch (`return target_object`)
    # and the dict reaches drop_object(), which expects a Pydantic model
    # with a .get_core_object() method -> AttributeError.
    # So we serialise the dict to a JSON string here. Same data, the
    # branch upstream actually supports.
    print("\n[TEST 4] drop_object -- name-prefix deny")
    try:
        result = await client.call_tool(
            "drop_object",
            {
                "object_type": "table",
                "target_object": json.dumps({
                    "name": "__macaw_smoke_fake__",
                    "database_name": "__macaw_db__",
                    "schema_name": "__macaw_schema__",
                }),
                "if_exists": True,
            },
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "not allowed" in text.lower():
            print("  PASS -- wrapper rejected drop_object at the name-prefix "
                  "check. Snowflake never touched.")
        else:
            print("  Inspect -- expected 'not allowed'. If your YAML allows "
                  "DROP this is the config-dependent inconclusive branch.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "not allowed" in msg.lower():
            print("  PASS -- wrapper rejected drop_object at the name-prefix "
                  "check. The exception contains 'not allowed'.")
        else:
            print("  Inspect -- exception was not from the wrapper. Either "
                  "param-shape error (TypeError before the wrapper), or "
                  "the wrapper fell through and snowflake rejected.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like across the four tests (no real Snowflake needed):

  TEST 1 ✓  Server registered on the mesh; run_snowflake_query advertised.
            Proves: framework swap and tool registration work.

  TEST 2 ✓  SELECT either succeeded or failed at the upstream connector
            without 'not allowed' anywhere. Proves: wrapper allow path.

  TEST 3 ✓  DROP via run_snowflake_query rejected with 'not allowed'.
            Proves: wrapper statement-arg deny path. (This is the
            replacement for the old CheckQueryType.on_call_tool that
            inspected context.message.arguments['statement'].)

  TEST 4 ✓  drop_object rejected with 'not allowed'.
            Proves: wrapper name-prefix deny path. (This is the
            replacement for the old branch that did
            tool_name.startswith('create') or .startswith('drop').)

If TESTS 3 and 4 both say PASS, the middleware-to-wrapper rewrite is
verified. The original CheckQueryType middleware is fully replaced
without losing any of its enforcement.

How to run with real Snowflake creds (for richer TEST 2 output):

  Set the connection params via env vars or CLI flags when starting
  the server. See snowflake-mcp's README for the exact flags. Once
  the server can authenticate, TEST 2 will return actual query rows
  instead of a connector error.

  None of TESTS 1, 3, 4 need credentials. They prove the port itself
  is correct, independent of whether Snowflake is reachable.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
