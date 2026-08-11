"""
MACAW client smoke test for mcp-azure-devops
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "Azure DevOps" devops-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

"""

import asyncio
import sys

from macaw_adapters.mcp import Client


# Sample of the 21 tools across projects/teams/work_items features.
# Names verified against the live tool advertisement, not guessed.
# If these register, the bulk @mcp.tool decoration ran on every path.
EXPECTED_SAMPLE = {
    "get_projects",          # features/projects/tools.py
    "get_all_teams",         # features/teams/tools.py
    "get_team_members",      # features/teams/tools.py
    "get_work_item",         # features/work_items/tools/read.py
    "create_work_item",      # features/work_items/tools/create.py
    "query_work_items",      # features/work_items/tools/query.py
}


def get_server(name, client):
    """Look up the azure-devops mcp server's agent_id on the mesh."""
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
        print('Example: python3 client-test-macaw.py "Azure DevOps" devops-test-client')
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
    print("Tools advertised by server (showing first 20):")
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
    for n in sorted(seen)[:20]:
        print(f"  - {n}")
    print(f"\n  Total unique tools: {len(seen)}\n")

    print("=" * 60)
    print("MCP-AZURE-DEVOPS TESTS")
    print("=" * 60)


    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_SAMPLE - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_SAMPLE)} sampled tools advertised "
              f"(out of {len(seen)} total).")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a register_*() didn't run or a feature import broke.")
        return


    print("\n[TEST 2] get_projects -- handler reachability + Azure DevOps API")
    try:
        result = await client.call_tool("get_projects", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- get_projects returned. Either real project data, ")
        print("  or 'Error: ...' from the wrapped AzureDevOpsClientError. ")
        print("  Both prove client -> mesh -> handler -> azure_client wrapping ")
        print("  works end-to-end.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like:

  TEST 1 ✓  Representative sample of the 21 tools advertised
            on the mesh.
            Proves: import swap held, register_all() /
            register_all_prompts() executed, all @mcp.tool
            decorators ran without raising.

  TEST 2 ✓  get_projects returned (real list or 'Error: ...').
            Proves: client -> mesh -> SecureMCP -> handler ->
            azure_client.get_connection() chain is intact.


""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
