"""
MACAW client smoke test for mcp-server-couchbase
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "couchbase" couchbase-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

Two layers being checked:

  Caller auth -- "is this caller really who they say they are?"
  MACAW signs every invoke_tool call with this caller's keypair.
  If MACAW didn't trust us, none of these calls would even reach
  the server. Any response coming back is the proof.

  Upstream auth -- "what credentials does the server use to talk
  to Couchbase?" The server reads connection-string + username +
  password from CLI flags / env vars at startup (process-global,
  set once, used for every call). Same shape as alibaba's env-var
  fallback or rainmaker's CLI-login config.

  Two outcome branches both prove the port:
    - No Couchbase reachable -> tool returns/raises a clear error,
      flowing through the SecureMCP handler chain.
    - Couchbase reachable     -> tools return real data (lists,
      dicts) from the cluster.
"""

import asyncio
import sys

from macaw_adapters.mcp import Client


def get_server(name, client):
    agents = client.macaw_client.list_agents(agent_type="app")
    server = [
        a for a in agents
        if name in a.get("agent_id", "")
        and "/tool." not in a.get("agent_id", "")
        # Exclude client agents (their IDs start with "securemcp-client-").
        # The server we want is "securemcp-<NAME>", and a substring filter
        # like "couchbase" would otherwise also match "securemcp-client-
        # couchbase-test-client" -- the caller itself.
        and "securemcp-client-" not in a.get("agent_id", "")
    ]
    if not server:
        print(f"No server found matching: {name}")
        return None
    return server[0].get("agent_id")


async def main():
    if len(sys.argv) < 3:
        print('Usage: python3 client-test-macaw.py "<server filter>" <client name>')
        print('Example: python3 client-test-macaw.py "couchbase" couchbase-test-client')
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
    print("COUCHBASE MCP TESTS")
    print("=" * 60)

    # TEST 1 -- get_server_configuration_status
    # Doesn't actually connect to Couchbase. Just reports what
    # configuration the server was started with + whether the
    # cluster object has been built yet (False until a real
    # cluster-touching tool runs first). Always succeeds end-to-end
    # if the port is correct.
    print("\n[TEST 1] get_server_configuration_status -- no upstream call")
    try:
        result = await client.call_tool("get_server_configuration_status", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"server_name"' in text or "couchbase" in text.lower():
            print("  PASS -- handler ran, configuration came back. "
                  "Caller-auth + dispatch chain verified.")
        else:
            print("  Inspect -- shape unexpected.")
    except Exception as e:
        print(f"  FAILED: {e}")
        print("  This is a blocker -- the port itself is broken.")

    # TEST 2 -- test_cluster_connection
    # Forces a cluster connect. Two outcomes:
    #   - Couchbase reachable (and creds correct):
    #     {"status": "success", "cluster_connected": true, ...}
    #   - Couchbase unreachable / no creds:
    #     {"status": "error", "cluster_connected": false, "error": "..."}
    # Either result coming back through SecureMCP proves the
    # handler chain works AND the upstream connect path executed.
    print("\n[TEST 2] test_cluster_connection -- attempts a real cluster connect")
    try:
        result = await client.call_tool("test_cluster_connection", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if '"success"' in text or '"cluster_connected": True' in text:
            print("  PASS (creds branch) -- Couchbase reachable, cluster built.")
        elif '"error"' in text or '"cluster_connected": False' in text:
            print("  PASS (no-creds/no-server branch) -- the SDK raised, the "
                  "tool wrapped the error, and it came back as JSON. The "
                  "handler chain is wired end-to-end.")
        else:
            print("  Inspect -- response did not match either branch.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  Mesh-level error -- caller-auth or transport problem, "
              "NOT a Couchbase issue.")

    # TEST 3 -- get_buckets_in_cluster
    # Goes one step further than TEST 2: actually queries the
    # cluster manager for bucket names. Two outcomes:
    #   - With a real Couchbase + valid creds: a list of bucket names.
    #   - Without: an exception propagating "could not connect" or
    #     similar from the SDK, caught by the SecureMCP handler.
    print("\n[TEST 3] get_buckets_in_cluster -- read-only cluster query")
    try:
        result = await client.call_tool("get_buckets_in_cluster", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        if "[" in text and "]" in text:
            print("  PASS (creds branch) -- bucket names returned. Full "
                  "vertical: client -> mesh -> SecureMCP -> tool -> "
                  "Couchbase SDK -> cluster -> back.")
        else:
            print("  Inspect -- unexpected response shape.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        if "connect" in msg.lower() or "auth" in msg.lower() or "timeout" in msg.lower():
            print("  PASS (no-creds/no-server branch) -- SDK error propagated "
                  "cleanly through SecureMCP. Same proof as TEST 2 via a "
                  "different SDK path.")
        else:
            print("  Inspect -- exception shape unexpected.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What you should see:

  Without a real Couchbase cluster on this host:
    TEST 1  configuration dict (always passes; no upstream call).
    TEST 2  {"status": "error", "cluster_connected": false} or similar.
    TEST 3  exception with "connect" / "timeout" / "auth" in the text.
    All three came back through the SecureMCP handler chain.
    That is the port-correctness proof.

  With a real Couchbase cluster + creds:
    TEST 1  configuration dict (unchanged).
    TEST 2  {"status": "success", "cluster_connected": true, ...}.
    TEST 3  list of bucket names like ["travel-sample", "default"].

How to run with creds:

  Easiest path -- run a local Couchbase Docker container:

      docker run -d --name couchbase \\
          -p 8091-8097:8091-8097 -p 11210:11210 \\
          couchbase/server:7.6.0
      # Wait ~30 seconds, then open http://localhost:8091 in a
      # browser and complete the one-time setup wizard
      # (cluster name, admin user, sample buckets).

  Then start the MCP server with creds matching the wizard:

      export CB_CONNECTION_STRING="couchbase://localhost"
      export CB_USERNAME="Administrator"
      export CB_PASSWORD="<password you set in wizard>"
      python3 -m mcp_server   # in the src/ directory

  Re-run this script in a second terminal. TESTS 2 and 3 should
  flip from the error-branch to the creds-branch responses.

  If you only want to verify port-correctness (no real Couchbase),
  just run the server and this script -- the error-branch responses
  are sufficient proof.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
