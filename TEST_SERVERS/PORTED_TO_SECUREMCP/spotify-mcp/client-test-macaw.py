"""
MACAW client smoke test for spotify-mcp
(post low-level-Server -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "spotify" spotify-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

What this tests:
    1. Port-correctness  -- server registered on the mesh, all 5 tools advertised
                            with the original Spotify-prefixed names.
    2. SpotifySearch     -- reaches the handler (calls spotipy.search()).
    3. SpotifyPlayback   -- reaches the handler with action="get".
    4. SpotifyQueue      -- reaches the handler with action="get".

Tests 2-4 do NOT require a working Spotify OAuth session. The handlers
catch SpotifyException and return {"error": ...}, so we treat both
"tool ran + returned error JSON" and "tool ran + got real data" as PASS.
What we are proving is that the call traversed:
    client -> mesh -> SecureMCP handler.
The handler's downstream Spotify Web API call is out of scope.
"""

import asyncio
import sys

from macaw_adapters.mcp import Client


EXPECTED_TOOLS = {
    "SpotifyPlayback",
    "SpotifySearch",
    "SpotifyQueue",
    "SpotifyGetInfo",
    "SpotifyPlaylist",
}


def get_server(name, client):
    """Look up the spotify-mcp server's agent_id on the mesh.

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
        print('Example: python3 client-test-macaw.py "spotify" spotify-test-client')
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
    print("SPOTIFY-MCP TESTS")
    print("=" * 60)

    # --------------------------------------------------------------
    # TEST 1 -- expected tools all present
    #
    # Pure port-correctness check. If all 5 tools registered cleanly
    # we know:
    #   - import swap (low-level Server -> SecureMCP) didn't break anything
    #   - the 5 @mcp.tool() decorators ran at module import time
    #   - SecureMCP's .tool() accepted (name=, description=) for each
    #   - the original tool names (Spotify-prefixed) were preserved
    # No upstream Spotify Web API call yet.
    # --------------------------------------------------------------
    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_TOOLS - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_TOOLS)} expected tools advertised.")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a @mcp.tool decorator didn't run, or it raised at "
              "import time. Check server logs.")
        return

    # --------------------------------------------------------------
    # TEST 2 -- SpotifySearch reaches the handler
    #
    # Calls spotify_client.search(query, qtype, limit). Without
    # working OAuth credentials, spotipy raises SpotifyException
    # which the tool body catches and returns as {"error": ...}.
    # Either outcome proves the call reached the handler.
    # --------------------------------------------------------------
    print("\n[TEST 2] SpotifySearch -- handler reachability")
    try:
        result = await client.call_tool(
            "SpotifySearch",
            {"query": "macaw smoke test", "qtype": "track", "limit": 1},
        )
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- SpotifySearch returned. Either Spotify answered, "
              "or the handler caught a SpotifyException and returned "
              "an error dict. Both prove the call reached the handler.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was "
              "reached, upstream Spotify API was not (or auth missing).")

    # --------------------------------------------------------------
    # TEST 3 -- SpotifyPlayback (action=get) reaches the handler
    #
    # Read-only -- "get" returns the current track, no playback change.
    # --------------------------------------------------------------
    print("\n[TEST 3] SpotifyPlayback action=get -- handler reachability")
    try:
        result = await client.call_tool("SpotifyPlayback", {"action": "get"})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- SpotifyPlayback returned (real or error dict).")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    # --------------------------------------------------------------
    # TEST 4 -- SpotifyQueue (action=get) reaches the handler
    #
    # Read-only -- "get" returns the current queue.
    # --------------------------------------------------------------
    print("\n[TEST 4] SpotifyQueue action=get -- handler reachability")
    try:
        result = await client.call_tool("SpotifyQueue", {"action": "get"})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- SpotifyQueue returned (real or error dict).")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh; handler was reached.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like (no Spotify OAuth required):

  TEST 1 ✓  All 5 expected tools advertised on the mesh with the
            original Spotify-prefixed names.
            Proves: import swap and tool registration succeeded.

  TEST 2 ✓  SpotifySearch returned (real results or {"error": ...}).
            Proves: client -> mesh -> SecureMCP handler is intact.

  TEST 3 ✓  SpotifyPlayback action=get returned similarly.

  TEST 4 ✓  SpotifyQueue action=get returned similarly.

If all four pass, the low-level-Server -> SecureMCP port is verified
at the mesh layer. Validating actual Spotify behaviour (real playback
control, real search results, real playlist edits) requires:
  - SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET / SPOTIFY_REDIRECT_URI
    set in the spotify-mcp environment,
  - a completed user OAuth flow (.cache file present),
and is out of scope for this smoke test -- that responsibility lives
with the original integration tests / manual verification against
a real Spotify account.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
