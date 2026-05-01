# Cloudflare MCP — SecureMCPProxy

Wraps Cloudflare's Documentation MCP server (`https://docs.mcp.cloudflare.com/mcp`)
with MACAW. Direct HTTPS + Bearer API token auth — no `mcp-remote`, no OAuth
browser dance. Same shape as `proxy_github.py`. One Python file, two tests.

The same wrap works for all 14 Cloudflare MCP servers — change one URL.

## Why direct HTTPS + Bearer instead of `mcp-remote`

Cloudflare's MCP servers accept their standard API token as a Bearer header
(per their OpenAI Responses API documentation). That's identical to GitHub's
remote MCP, which we already wrap that way. `mcp-remote` would add OAuth +
an orphan-process risk (we hit it on Figma) for no extra benefit.

## Cloudflare's 14 servers

Pick one URL based on what you need to expose:

| Server | URL |
|---|---|
| Documentation | `https://docs.mcp.cloudflare.com/mcp` |
| Workers Bindings | `https://bindings.mcp.cloudflare.com/mcp` |
| Workers Builds | `https://builds.mcp.cloudflare.com/mcp` |
| Observability | `https://observability.mcp.cloudflare.com/mcp` |
| Radar | `https://radar.mcp.cloudflare.com/mcp` |
| Container | `https://containers.mcp.cloudflare.com/mcp` |
| Browser Rendering | `https://browser.mcp.cloudflare.com/mcp` |
| Logpush | `https://logs.mcp.cloudflare.com/mcp` |
| AI Gateway | `https://ai-gateway.mcp.cloudflare.com/mcp` |
| Audit Logs | `https://auditlogs.mcp.cloudflare.com/mcp` |
| DNS Analytics | `https://dns-analytics.mcp.cloudflare.com/mcp` |
| Digital Experience Monitoring | `https://dex.mcp.cloudflare.com/mcp` |
| Cloudflare One CASB | `https://casb.mcp.cloudflare.com/mcp` |
| GraphQL | `https://graphql.mcp.cloudflare.com/mcp` |

This script defaults to **Documentation** because it's read-only with the
smallest scope and lowest blast radius. To wrap another, edit
`CF_MCP_URL` in `proxy_cloudflare.py`.

## Prereqs

- MACAW LocalAgent running.
- A Cloudflare account.

## Credentials

Create an API token at https://dash.cloudflare.com/profile/api-tokens →
**Create Token**.

For the **Documentation** server (this script's default), no specific
permissions are required — but Cloudflare requires every token to have at
least one scope, so pick something minimal like:

- **Account → Account Settings: Read**

For other servers, the required scopes are listed in Cloudflare's docs
(observability needs Workers logs read, browser needs Browser Rendering,
etc.).

```bash
export CLOUDFLARE_API_TOKEN="..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/cloudflare/proxy_cloudflare.py
```

Expected: tool list on stderr, then `search_cloudflare_documentation -> {...}`
with hits about Workers. MACAW console shows one entry under
`app_name=cloudflare-docs-proxy`.

If the smoke target tool name is wrong (Cloudflare may rename), the script
will error with a clear message. Check the printed tool list and replace
`"search_cloudflare_documentation"` in Test 1 with whatever name appears.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_cloudflare.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cloudflare-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/cloudflare/proxy_cloudflare.py"],
      "env": { "CLOUDFLARE_API_TOKEN": "..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add cloudflare-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/cloudflare/proxy_cloudflare.py \
  -e CLOUDFLARE_API_TOKEN=...
```

Then prompt: *"Use the cloudflare-macaw tool to search Cloudflare docs for
'durable objects' and show the top 3 result titles."*

## Notes on what could go wrong

- **`401 Unauthorized`** — token wrong or revoked.
- **`403 Forbidden`** on a non-docs server — token is missing the scope that
  particular server needs (e.g. `bindings` requires Workers Scripts:Edit).
  Generate a wider token, or stick to `docs.mcp.cloudflare.com`.
- **Smoke tool name mismatch** — Cloudflare may rename
  `search_cloudflare_documentation`. Look at the printed tool list and
  swap the call-tool target. Doesn't break the wrap; just the smoke
  assertion.
- **"Claude's response was interrupted"** in MCP clients — Cloudflare's docs
  call out that observability and similar servers can chain many tool
  calls and overflow context. Keep prompts narrow.
