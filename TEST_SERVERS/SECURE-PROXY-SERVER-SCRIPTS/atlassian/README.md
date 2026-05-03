# Atlassian Rovo MCP — SecureMCPProxy (mcp-remote stdio)

Wraps Atlassian's remote MCP server (`https://mcp.atlassian.com/v1/mcp/authv2`)
with MACAW via `mcp-remote`. One Python file, two tests.

Atlassian Rovo MCP is OAuth 2.1 with proper Dynamic Client Registration
— same wrap shape as Postman and Supabase. No manual OAuth app,
no API token, no allowlist wall.

Covers Jira, Confluence, and Compass (whichever your Atlassian Cloud
site has enabled).

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).
- An Atlassian Cloud site with at least Jira, Confluence, or Compass
  enabled. Cloud only — no Server / Data Center support.

## Rate limits

Free: 500 calls/hour. Standard: 1,000/hour. Premium / Enterprise:
1,000/hour base + 20 per user up to 10,000/hour. The smoke test costs 2
calls (`tools/list` + `getAccessibleAtlassianResources`). Don't loop it.

## One-time OAuth setup

```bash
npx -y mcp-remote "https://mcp.atlassian.com/v1/mcp/authv2"
```

A browser opens. Sign in to Atlassian, **pick the Cloud site** to
authorize, approve the requested scopes. Token cached in `~/.mcp-auth/`.
**Ctrl+C** once you see "Proxy established successfully".

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/atlassian/proxy_atlassian.py
```

Expected: tool list on stderr (~15–25 tools depending on your enabled
products), then `getAccessibleAtlassianResources -> [...]` listing your
Cloud sites by id and name. MACAW console shows one entry under
`app_name=atlassian-proxy`.

If the smoke target name doesn't match what your tool list shows
(Atlassian sometimes changes tool names between versions), swap
`getAccessibleAtlassianResources` in line 50 of `proxy_atlassian.py` for
one of the names in the printed list — `getCurrentUser` and `getAccessibleResources`
are common alternatives.

First run: 10–20s for `npx -y` to fetch `mcp-remote`. Subsequent runs
are fast.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_atlassian.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "atlassian-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/atlassian/proxy_atlassian.py"]
    }
  }
}
```

No env vars needed — `mcp-remote` reads the cached OAuth token from `$HOME`.

**Claude Code CLI:**

```bash
claude mcp add atlassian-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/atlassian/proxy_atlassian.py
```

Then prompt: *"Use the atlassian-macaw tool to list my accessible
Atlassian sites by id and name. Do not call any other tool."* MACAW
console shows a second entry from the LLM client.

## Notes on what could go wrong

- **First call hangs forever** — `mcp-remote` is waiting for OAuth.
  Run the one-time setup command first.
- **`Authorization failed` after working before** — token expired and
  refresh failed. `rm -rf ~/.mcp-auth` and redo the one-time setup.
- **`Tool not found: getAccessibleAtlassianResources`** — Atlassian
  renamed it. Read the printed `tools:` list, pick the closest match,
  swap the name on line 50.
- **`429 Too Many Requests`** — you've hit the per-hour rate limit.
  Wait 60 minutes or upgrade your Cloud plan.
- **`$HOME` mismatch when spawned by Gemini** — the script forwards
  `HOME` explicitly, so `mcp-remote` finds `~/.mcp-auth/`. If Gemini
  ever runs under a different user / sandbox, the cache won't be
  visible.
- **Tools require granular OAuth scopes** — during the OAuth flow,
  Atlassian asks you to approve specific permissions per product. If
  you skipped some, those tools will 403 even though the wrap is fine.
  Redo OAuth and grant everything you need.
