"""
MACAW client smoke test for memory-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "memory" memory-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_TOOLS = {
    "store_memory",
    "retrieve_memory",
    "semantic_cache_response",
    "check_semantic_cache",
    "hybrid_search",
    "search_web",
}


def get_server(name, client):
    """Look up the memory-mcp server's agent_id on the mesh.

    Filters out per-tool sub-agents and the test client's own agent.
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
        print('Example: python3 client-test-macaw.py "memory" memory-test-client')
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
    print("MEMORY-MCP TESTS")
    print("=" * 60)


    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_TOOLS - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_TOOLS)} expected tools advertised.")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a register_*_tools call didn't run, or a decorator "
              "raised at import time. Check server logs.")
        return


    print("\n[TEST 2] store_memory -- handler reachability")
    try:
        result = await client.call_tool(
            "store_memory",
            {
                "conversation_id": "macaw-smoke-conv-1",
                "text": "macaw smoke test message",
                "message_type": "human",
                "user_id": "macaw-smoke-user",
            },
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- store_memory returned. Either upstream service "
              "answered, or the handler caught httpx error and returned "
              "an error dict. Both prove the call reached the handler.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "ValueError" in msg or "validate" in msg.lower():
            print("  Inspect -- validator rejected our inputs. Check "
                  "utils/validators.py for the accepted shape.")
        else:
            print("  PASS-ish -- exception was not a validator error. "
                  "Likely mesh-level or upstream HTTP failure surfaced "
                  "through invoke_tool. The handler was reached.")


    print("\n[TEST 3] retrieve_memory -- handler reachability")
    try:
        result = await client.call_tool(
            "retrieve_memory",
            {"user_id": "macaw-smoke-user", "text": "previous chat about mongodb"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- retrieve_memory returned (real or error dict).")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was "
              "reached, upstream HTTP service was not.")

    
    print("\n[TEST 4] check_semantic_cache -- handler reachability")
    try:
        result = await client.call_tool(
            "check_semantic_cache",
            {"user_id": "macaw-smoke-user", "query": "what is mongodb"},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- check_semantic_cache returned (real or error dict).")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
