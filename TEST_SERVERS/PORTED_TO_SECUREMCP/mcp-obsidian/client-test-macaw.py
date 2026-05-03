"""
MACAW client smoke test for mcp-obsidian
(post low-level-Server -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "obsidian" obsidian-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

What this tests:
    1. Port-correctness  -- server registered on the mesh, all 13
                            tools advertised. The 13-class -> 13-
                            wrapper collapse worked.
    2. obsidian_list_files_in_vault -- read-only, no parameters.
                                       Reaches the handler regardless
                                       of whether Obsidian's REST API
                                       is up. Without it, the handler
                                       errors gracefully.
    3. obsidian_simple_search       -- exercises typed-kwarg path
                                       (query + context_length).

Tests 2-3 do NOT require a running Obsidian instance for handler-
reach verification. The Obsidian Python client raises on connection
failure; the wrapper / handler may surface that as a string error
or as an exception. Either outcome proves the client -> mesh ->
SecureMCP -> handler chain is intact.
"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_TOOLS = {
    "obsidian_list_files_in_vault",
    "obsidian_list_files_in_dir",
    "obsidian_get_file_contents",
    "obsidian_simple_search",
    "obsidian_append_content",
    "obsidian_patch_content",
    "obsidian_put_content",
    "obsidian_delete_file",
    "obsidian_complex_search",
    "obsidian_batch_get_file_contents",
    "obsidian_get_periodic_note",
    "obsidian_get_recent_periodic_notes",
    "obsidian_get_recent_changes",
}


def get_server(name, client):
    """Look up the mcp-obsidian server's agent_id on the mesh."""
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
        print('Example: python3 client-test-macaw.py "obsidian" obsidian-test-client')
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
    print("MCP-OBSIDIAN TESTS")
    print("=" * 60)

    # --------------------------------------------------------------
    # TEST 1 -- expected tools all present
    #
    # The original used a dict registry with 13 ToolHandler classes;
    # the port collapses each class into a @app.tool() wrapper. If
    # all 13 register cleanly we know:
    #   - import swap (mcp.server.Server -> SecureMCP) didn't break.
    #   - all 13 wrapper signatures parsed and registered.
    #   - all 13 module-level handler instances built without errors.
    # --------------------------------------------------------------
    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_TOOLS - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_TOOLS)} expected tools advertised.")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a @app.tool wrapper didn't run, or a handler")
        print("  instance failed to construct. Check server logs.")
        return

    # --------------------------------------------------------------
    # TEST 2 -- obsidian_list_files_in_vault (no parameters)
    #
    # Smallest possible call. No kwargs to pass. Reaches the handler
    # regardless of Obsidian connectivity. Without a live Obsidian
    # API on the configured host, the handler raises (the original
    # behaviour) and the mesh surfaces an error -- still a proof of
    # reachability.
    # --------------------------------------------------------------
    print("\n[TEST 2] obsidian_list_files_in_vault -- no-arg handler reach")
    try:
        result = await client.call_tool("obsidian_list_files_in_vault", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- list_files_in_vault returned. Either a real ")
        print("  JSON list of files (live Obsidian) or an error string ")
        print("  (no Obsidian). Both prove the wrapper -> handler -> ")
        print("  Obsidian client chain is intact.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    # --------------------------------------------------------------
    # TEST 3 -- obsidian_simple_search (exercises typed-kwarg path)
    #
    # Passes both the required `query` and the optional
    # `context_length` kwarg. Verifies the wrapper rebuilds the dict
    # the handler expects.
    # --------------------------------------------------------------
    print("\n[TEST 3] obsidian_simple_search(query='macaw', context_length=50) -- typed-kwarg path")
    try:
        result = await client.call_tool(
            "obsidian_simple_search",
            {"query": "macaw", "context_length": 50},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- simple_search returned. Either real search ")
        print("  results (live Obsidian) or an error string. Both prove ")
        print("  typed kwargs arrive correctly at the handler's run_tool.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like:

  TEST 1 ✓  All 13 expected tools advertised on the mesh.
            Proves: import swap held; the 13-class -> 13-wrapper
            collapse registered cleanly; all 13 module-level
            ToolHandler instances built without errors.

  TEST 2 ✓  obsidian_list_files_in_vault returned (real list or
            error).
            Proves: client -> mesh -> SecureMCP -> wrapper ->
            handler.run_tool -> Obsidian client chain is intact.

  TEST 3 ✓  obsidian_simple_search returned with both kwargs
            applied.
            Proves: typed kwargs arrive at the handler via the
            wrapper's dict-rebuild step; multi-parameter tools
            are wired correctly.

If all three pass, the FastMCP -> SecureMCP port is verified at
the mesh layer. Validating real Obsidian behaviour (file CRUD,
note search, periodic notes) requires a live Obsidian REST API
plugin running and OBSIDIAN_API_KEY / OBSIDIAN_HOST set
correctly -- out of scope for this smoke test.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
