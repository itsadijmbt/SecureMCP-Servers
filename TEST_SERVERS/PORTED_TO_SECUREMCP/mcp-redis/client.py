"""
client.py — Policy test client for the Redis SecureMCP port.

Tests Policy/server_policy_v0.1.json against the running server in 12
cases grouped into 4 policy areas (3 tests each).

Usage:
    Terminal 1:  python -m src.main                       # start server
    Terminal 2:  python client.py Redis-mCP-server <name> # run policy tests


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
        print(f"No server matching '{name}' is registered. "
              "Start it first: python -m src.main")
        return None
    return server[0].get("agent_id")


async def run_test(client, label, tool, args, expect, note=""):
    """
    expect: "allow" — call should succeed (policy permits)
            "deny"  — MAPL should reject (PermissionError / policy denial)
    """
    arg_preview = (str(args)[:60] + "...") if len(str(args)) > 60 else str(args)
    print(f"\n[{label}] {tool}({arg_preview})")
    if note:
        print(f"   why: {note}")
    print(f"   expect: {expect.upper()}")
    try:
        result = await client.call_tool(tool, args)
        output = (
            result.get("result", result) if isinstance(result, dict)
            else getattr(result, "text", result)
        )
        if expect == "allow":
            print(f"   PASS — ALLOWED (as expected)")
            preview = str(output)[:180]
            print(f"   result: {preview}{'...' if len(str(output)) > 180 else ''}")
        else:
            print(f"   FAIL — ALLOWED (expected DENY) — POLICY GAP")
            preview = str(output)[:180]
            print(f"   result: {preview}{'...' if len(str(output)) > 180 else ''}")
    except Exception as e:
        msg = str(e)[:200]
        if expect == "deny":
            print(f"   PASS — DENIED (as expected): {msg}")
        else:
            print(f"   FAIL — DENIED (expected ALLOW) — UNEXPECTED BLOCK")
            print(f"   error: {msg}")


async def main():
    if len(sys.argv) < 3:
        print("Usage: python client.py <server_filter_name> <client_name>")
        sys.exit(1)

    name = sys.argv[1]
    client_type = sys.argv[2]

    client = Client(client_type)
    server_id = get_server(client, name)
    if not server_id:
        return

    client.set_default_server(server_id)

    print(f"Connected to server agent_id: {server_id}")
    print("\nFetching tools from MACAW mesh...")
    tools = await client.list_tools(server_name=name)
    seen = set()
    for t in tools:
        if t["name"] not in seen:
            seen.add(t["name"])
    print(f" {len(seen)} unique tools registered\n")

    print("=" * 60)
    print("server_policy_v0.1 — TEST SUITE (12 tests across 4 areas)")
    print("=" * 60)

    print("\n--- Area A: Resource allowlist + denied_resources ---")
    await run_test(
        client, "TEST A1 [allow:info]", "info", {}, "allow",
        note="'info' is in tool:** allowlist, no denied_resources match"
    )
    await run_test(
        client, "TEST A2 [deny:scan_keys]", "scan_keys",
        {"pattern": "*", "count": 10}, "deny",
        note="'scan_keys' is in denied_resources; MAPL should reject"
    )
    await run_test(
        client, "TEST A3 [deny:json_del]", "json_del",
        {"name": "ignored"}, "deny",
        note="'json_del' is in denied_resources; MAPL should reject"
    )

    print("\n--- Area B: get.key pattern + max_length ---")
    await run_test(
        client, "TEST B1 [allow:valid_key]", "get",
        {"key": "macaw_test_key"}, "allow",
        note="key matches ^[A-Za-z]..., length 14 <= 100"
    )
    await run_test(
        client, "TEST B2 [deny:starts_with_digit]", "get",
        {"key": "1bad_key"}, "deny",
        note="key starts with digit; pattern ^[A-Za-z]... fails"
    )
    long_key = "x" * 150
    await run_test(
        client, "TEST B3 [deny:over_max_length]", "get",
        {"key": long_key}, "deny",
        note=f"key length {len(long_key)} > max_length 100"
    )

    print("\n--- Area C: set.key pattern + expire.expire_seconds min ---")
    await run_test(
        client, "TEST C1 [allow:set_valid]", "set",
        {"key": "macaw_key", "value": "hello"}, "allow",
        note="valid key pattern, value provided"
    )
    await run_test(
        client, "TEST C2 [deny:set_bad_pattern]", "set",
        {"key": "@bad_key", "value": "x"}, "deny",
        note="key starts with '@'; pattern ^[A-Za-z]... fails"
    )
    await run_test(
        client, "TEST C3 [deny:expire_seconds_zero]", "expire",
        {"name": "valid_key", "expire_seconds": 0}, "deny",
        note="expire_seconds = 0 < min 1; constraint should reject"
    )

    print("\n--- Area D: denied_resources destructive denials ---")
    await run_test(
        client, "TEST D1 [deny:delete]", "delete",
        {"key": "macaw_key"}, "deny",
        note="tool:delete is in denied_resources; deny overrides tool:** allow"
    )
    await run_test(
        client, "TEST D2 [deny:rename]", "rename",
        {"old_key": "macaw_key", "new_key": "macaw_key_renamed"}, "deny",
        note="tool:rename is in denied_resources"
    )
    await run_test(
        client, "TEST D3 [deny:hdel]", "hdel",
        {"name": "macaw_hash", "key": "field1"}, "deny",
        note="tool:hdel is in denied_resources"
    )

    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE — review PASS/FAIL markers above")
    print("=" * 60)
    print(
        "\nNotes:\n"
        " * Area D PASS = denied_resources blocked the destructive tool.\n"
        " * This policy has NO attestations (a param condition cannot select a\n"
        "   redis tool), so client-analyst.py is not exercised here.\n"
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
