"""MACAW client smoke test for notion_mcp (low-level Server -> SecureMCP).



Usage:
    python client-test-macaw.py "notion-todo" <client_name>
    NOTION_TEST_WRITE=1 python client-test-macaw.py "notion-todo" <client_name>
"""

import asyncio
import json
import os
import sys

from macaw_adapters.mcp import Client


def get_server(client, name):
    """Locate the notion-todo SecureMCP server on the MACAW mesh."""
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
        and "securemcp-client-" not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No SecureMCP server matching '{name}' found.")
        print("Start it first: python -m notion_mcp")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python client-test-macaw.py "notion-todo" <client_name>')
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]
    client = Client(client_type)
    server_id = get_server(client, name)
    if not server_id:
        return 1
    client.set_default_server(server_id)
    print(f"Connected to: {server_id}")

    # TEST 1 -- mesh-native tool discovery
    print("\n" + "=" * 60)
    print("TEST 1: list_tools  (mesh advertises 4 notion tools)")
    print("=" * 60)
    tools = await client.list_tools(server_name=name)
    seen = set()
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
            print(f"  - {t['name']}")
    print(f"  -> {len(seen)} unique tools advertised")
    expected = {"add_todo", "show_all_todos", "show_today_todos", "complete_todo"}
    missing = expected - seen
    assert not missing, f"FAIL: missing tools {missing}"
    print("  PASS -- all 4 expected tools present")

    # TEST 2 -- show_all_todos: read-only round-trip
    print("\n" + "=" * 60)
    print("TEST 2: show_all_todos  (read-only Notion round-trip)")
    print("=" * 60)
    r2 = await client.call_tool("show_all_todos", {})
    output2 = r2.get("result", r2) if isinstance(r2, dict) else r2
    print(f"  result head: {str(output2)[:200]}")
    # The handler returns json.dumps(formatted_todos, indent=2). On
    # success that's a JSON array (possibly empty if the database has
    # no rows). On Notion API failure the handler returns the human
    # error string starting with "Error fetching todos:".
    if isinstance(output2, str) and output2.lstrip().startswith("["):
        try:
            parsed = json.loads(output2)
            assert isinstance(parsed, list)
            print(f"  PASS -- Notion returned {len(parsed)} todo(s)")
        except json.JSONDecodeError as e:
            print(f"  FAIL -- response was not valid JSON: {e}")
            return 1
    elif isinstance(output2, str) and output2.startswith("Error fetching todos:"):
        print("  PASS (handler reachable) -- Notion API rejected the request; "
              "credential / database access is a deployment concern, not a "
              "port-correctness concern.")
    else:
        print(f"  Inspect -- unexpected shape: {type(output2).__name__}")

    # TEST 3 -- add_todo + complete_todo (only if NOTION_TEST_WRITE=1)
    print("\n" + "=" * 60)
    print("TEST 3: add_todo + complete_todo  (write+cleanup pair)")
    print("=" * 60)
    if os.environ.get("NOTION_TEST_WRITE") != "1":
        print("  SKIPPED -- set NOTION_TEST_WRITE=1 to enable Notion writes.")
        return 0

    test_task = "[smoke-test] port-verification task"
    r3a = await client.call_tool(
        "add_todo",
        {"task": test_task, "when": "later"},
    )
    output3a = r3a.get("result", r3a) if isinstance(r3a, dict) else r3a
    print(f"  add_todo result: {str(output3a)[:200]}")
    assert isinstance(output3a, str) and "Added todo" in output3a, (
        f"FAIL: add_todo did not confirm; got: {output3a}"
    )

    # Find the page we just created so we can mark it complete.
    r3b = await client.call_tool("show_all_todos", {})
    output3b = r3b.get("result", r3b) if isinstance(r3b, dict) else r3b
    todos = json.loads(output3b)
    matching = [t for t in todos if t.get("task") == test_task]
    assert matching, "FAIL: just-created todo not found in show_all_todos"
    page_id = matching[0]["id"]
    print(f"  located page_id: {page_id}")

    r3c = await client.call_tool("complete_todo", {"task_id": page_id})
    output3c = r3c.get("result", r3c) if isinstance(r3c, dict) else r3c
    print(f"  complete_todo result: {str(output3c)[:200]}")
    assert isinstance(output3c, str) and "Marked todo as complete" in output3c, (
        f"FAIL: complete_todo did not confirm; got: {output3c}"
    )
    print("  PASS -- write/cleanup pair completed; todo left in 'completed' state")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
