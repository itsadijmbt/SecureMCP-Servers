# Prisma AIRS MCP Relay — SecureMCPProxy (uvx stdio)

Wraps `pan-mcp-relay` (Palo Alto Networks Prisma AIRS MCP Security Relay)
with MACAW. One Python file, two tests, one bundled config.

## Status

**Wrap: verified.** **Acceptance: blocked, two reasons.**

Running the script reaches the upstream's tool-registry initialization,
which crashes inside pan-mcp-relay's own code:

    TypeError: ClientSessionGroup._establish_session()
      missing 1 required positional argument: 'session_params'

The relay calls a private method on the `mcp` SDK whose signature changed
in a recent release. The bug is in pan-mcp-relay, not in this proxy. No
credentials reach Prisma AIRS in this trace, so real or bogus creds give
the same result.

What this run does verify (Layer 1 — wrap mechanics):

- `SecureMCPProxy` spawns the upstream cleanly.
- MACAW Client + Server both register; agent IDs visible in console.
- The MCP `tools/list` request travels MACAW → pan-mcp-relay end-to-end.
- pan-mcp-relay's internal crash surfaces as a structured error, not a hang.

Acceptance with real Prisma AIRS credentials is doubly blocked:

1. The vendor bug above must be fixed (or an older pan-mcp-relay version
   pinned that's compatible with the installed `mcp` SDK).
2. A Prisma AIRS / Strata Cloud Manager subscription is required to obtain
   an API key and AI Security Profile.

Revisit when both unblock. Until then: registry entry is **PROXY ✓ (wrap
verified, vendor + account acceptance pending)**.

## What's interesting about this one

Pan-mcp-relay is **itself a security relay** — it sits between MCP clients
and downstream MCP servers and uses the Prisma AIRS API to scan tool
descriptions, parameters, and responses for prompt injection, malicious
URLs, sensitive data, etc.

Stacking it under MACAW gives **two security relays in series**:

```
Gemini -> MACAW SecureMCPProxy -> pan-mcp-relay -> downstream servers
          (identity + MAPL +     (Prisma AIRS:
           cryptographic audit)   threat scanning)
```

Both contribute different signals — record this as a **layered-security
pattern** in `PORTABILITY_REGISTRY.md`. The downstream servers are configured
in `mcp-relay.yaml` in this folder. The default config bundles
`mcp-server-fetch` so the relay has at least one tool registered.

## Prereqs

- MACAW LocalAgent running.
- `uv` installed and on `$PATH` (`uv --version`).
- A Prisma AIRS API key + AI Security Profile name or ID.
  Activation/onboarding: see Palo Alto's
  [Prisma AIRS API Intercept docs](https://pan.dev/prisma-airs/scan/api/).

## Credentials

```bash
export PRISMA_AIRS_API_KEY="..."          # from Strata Cloud Manager → Manage → API Keys
export PRISMA_AIRS_AI_PROFILE="..."       # profile name or ID
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/pan-mcp-relay/proxy_pan_mcp_relay.py
```

Expected on stderr:

- `tools: 1` (or more if you add downstreams) — `fetch` from `mcp-server-fetch`.
- `fetch -> {...}` — HTML body from `https://example.com`.
- AIRS scan happens transparently in the relay; if your AI profile blocks
  `example.com` (unlikely), you'd get a structured threat decision instead.

First run is slow (10–30s) — `uvx` downloads `pan-mcp-relay` and
`mcp-server-fetch`. Subsequent runs reuse the uv cache.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_pan_mcp_relay.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "pan-mcp-relay-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/pan-mcp-relay/proxy_pan_mcp_relay.py"],
      "env": {
        "PRISMA_AIRS_API_KEY": "...",
        "PRISMA_AIRS_AI_PROFILE": "..."
      }
    }
  }
}
```

Then prompt: *"Use the pan-mcp-relay-macaw tool to call fetch with
{\"url\":\"https://example.com\"} and show me the page title."* MACAW console
shows a second entry from the LLM client.

## Adding more downstream servers

Edit `mcp-relay.yaml` in this folder. Pan-mcp-relay supports stdio, SSE, and
Streamable HTTP downstream servers — all behind one MACAW edge. Example:

```yaml
mcpServers:
  fetch:
    command: uvx
    args: [mcp-server-fetch]
  filesystem:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-filesystem"
      - /var/tmp/safe-readonly-dir
```

`pan-mcp-relay` enforces `--max-mcp-servers` (default 32) and
`--max-mcp-tools` (default 256). Bump if you exceed.

## Notes on what could go wrong

- **`uvx: command not found`** — install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  then re-source your shell.
- **First run hangs** — `uvx` is downloading the package. 30s is normal.
- **`401` from AIRS API** — `PRISMA_AIRS_API_KEY` invalid or revoked.
  Rotate in Strata Cloud Manager → Manage → API Keys.
- **`AI profile not found`** — `PRISMA_AIRS_AI_PROFILE` mismatch. Use either
  profile name *or* the profile ID; double-check in Strata Cloud Manager →
  Manage → Security Profiles.
- **`fetch` blocked** — your AI profile's policy is rejecting the URL. This
  is the intended behavior, not a wrap failure. Try a different URL or
  inspect the AIRS scan log.
- **Empty `tools:` list** — `mcp-relay.yaml` had no downstream servers, or
  `uvx mcp-server-fetch` failed to start. Check the relay's stderr for
  downstream connection errors.

## Licensing note

`pan-mcp-relay` ships under the Polyform Internal Use License. It's intended
for use within your own organization, not for redistribution. Fine for
integration testing on your dev box; check with legal before bundling into
shipped software.
