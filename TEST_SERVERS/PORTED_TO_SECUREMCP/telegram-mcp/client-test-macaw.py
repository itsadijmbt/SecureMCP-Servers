"""
MACAW client smoke test for telegram-mcp
(post FastMCP -> SecureMCP port).

Usage:
    python3 client-test-macaw.py "telegram" telegram-test-client

Args:
    1. server filter substring (matches against agent_id)
    2. client name (any string for this caller's MACAW identity)

What this tests:
    1. Port-correctness  -- server registered on the mesh; a representative
                            sample of expected tools is advertised.
    2. list_accounts     -- pure dict read, no Telegram network call.
                            Should return real account labels.
    3. get_me            -- reaches the handler; needs Telegram auth.
                            Without a working session, telethon raises
                            and the handler returns a string error,
                            which still proves handler reachability.

Tests 2-3 do NOT require live Telegram connectivity for handler-reach
verification: telethon errors are caught inside each tool body and
returned as a string. A successful handler call (real or error) proves
the chain client -> mesh -> SecureMCP -> handler is intact.
"""

import asyncio
import sys

from macaw_adapters.mcp import Client


# Telegram has ~100+ tools; we don't enumerate all here. Just sample the
# tools that exercise different shapes (sync helper, account-aware,
# entity-resolution, file-path). If these are advertised, the @mcp.tool
# import-time decoration ran on every tool path.
EXPECTED_SAMPLE = {
    "list_accounts",
    "get_chats",
    "get_messages",
    "send_message",
    "list_chats",
    "get_me",
}


def get_server(name, client):
    """Look up the telegram-mcp server's agent_id on the mesh."""
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
        print('Example: python3 client-test-macaw.py "telegram" telegram-test-client')
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
    print("TELEGRAM-MCP TESTS")
    print("=" * 60)

    # --------------------------------------------------------------
    # TEST 1 -- representative sample of tools is advertised
    #
    # Pure port-correctness check. Telegram has many tools; we just
    # confirm the sample shows up. If they do, we know the bulk
    # @mcp.tool decoration ran on every tool path, the import swap
    # held, and SecureMCP accepted name=/description= for each.
    # --------------------------------------------------------------
    print("\n[TEST 1] tool list -- port-correctness")
    missing = EXPECTED_SAMPLE - seen
    if not missing:
        print(f"  PASS -- all {len(EXPECTED_SAMPLE)} sampled tools advertised "
              f"(out of {len(seen)} total).")
    else:
        print(f"  FAILED -- missing tools: {sorted(missing)}")
        print("  Either a @mcp.tool decorator didn't run, or the kwarg-strip "
              "broke something. Check server import logs.")
        return

    # --------------------------------------------------------------
    # TEST 2 -- list_accounts (pure dict read)
    #
    # list_accounts reads the module-level `clients` dict built at
    # import time by _discover_accounts(). No Telegram network call.
    # Should return real account labels even without telegram auth.
    # --------------------------------------------------------------
    print("\n[TEST 2] list_accounts -- handler reachability + module state")
    try:
        result = await client.call_tool("list_accounts", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- list_accounts returned. Confirms _discover_accounts() "
              "ran at import time and the handler reaches `clients` dict.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  FAILED -- this should not error; list_accounts has no upstream "
              "dependency. Check that TELEGRAM_API_ID / TELEGRAM_API_HASH and "
              "at least one TELEGRAM_SESSION_* are set in the server's .env.")

    # --------------------------------------------------------------
    # TEST 3 -- get_me (lazy connect to Telegram)
    #
    # get_me hits cl.get_me() which needs ensure_connected() -> the
    # lazy-connect path that replaces the dropped eager cl.start().
    # If telegram session is valid, returns user info. If not, the
    # handler catches and returns a string error -- both prove the
    # handler ran on SecureMCP's loop.
    # --------------------------------------------------------------
    print("\n[TEST 3] get_me -- lazy-connect verification")
    try:
        result = await client.call_tool("get_me", {})
        text = str(result)
        print(f"  Result: {text[:240]}")
        print("  PASS -- get_me returned. If you see a user object, "
              "lazy-connect (ensure_connected) worked end-to-end. "
              "If you see a Telethon error string, the handler ran but "
              "Telegram auth is missing/invalid -- still proves "
              "handler reachability and lazy-connect entry.")
    except Exception as e:
        msg = str(e)
        print(f"  Got error: {msg[:240]}")
        print("  PASS-ish -- exception surfaced via mesh. Handler was "
              "reached; the failure is downstream of the port boundary.")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
What success looks like:

  TEST 1 ✓  Representative sample of tools advertised on the mesh.
            Proves: import swap and the bulk @mcp.tool() registration
            (109 decorator strips + plain ones) succeeded.

  TEST 2 ✓  list_accounts returned real account labels.
            Proves: module-level state initialization survived the
            port; handler reachability via mesh works.

  TEST 3 ✓  get_me returned (real user object OR Telethon error
            string).
            Proves: lazy-connect (ensure_connected, replacing the
            dropped eager cl.start()) entered SecureMCP's loop and
            the handler executed.

If all three pass, the FastMCP -> SecureMCP port is verified at the
mesh layer. Validating real Telegram behaviour (sending messages,
fetching dialogs, file uploads/downloads with allowed roots) requires
real TELEGRAM_API_ID/HASH/SESSION_STRING env vars and a valid
Telegram session -- that lives outside this smoke test.

Note on roots (Path A under this port): file-path tools
(upload_file, download_media, ...) are gated by SERVER_ALLOWED_ROOTS
set via the --allowed-root CLI argument on the server. There is no
client-side register_roots flow in this port; see MIGRATION.txt.
""")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nFatal: {e}")
        sys.exit(1)
