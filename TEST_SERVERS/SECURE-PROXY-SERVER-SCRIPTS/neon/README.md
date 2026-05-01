# Neon MCP — SecureMCPProxy (HTTP, bearer)

Wraps Neon's remote MCP server (`https://mcp.neon.tech/mcp`) with MACAW.
One Python file, two tests. Same shape as `proxy_github.py` — direct HTTP
upstream with `upstream_auth` bearer; no `mcp-remote`, no Docker, no OAuth
flow.

## Why no OAuth dance

Neon's remote MCP supports two auth modes: OAuth (for human-driven MCP
clients) and **API key in `Authorization: Bearer`** (for headless agents).
We use the second because it works directly with `SecureMCPProxy`'s
`upstream_auth` field. No browser callback, no `~/.mcp-auth/` cache.

## Prereqs

- MACAW LocalAgent running.
- A Neon account.

## Credentials

Create an API key:

1. https://console.neon.tech → **Settings → API keys → Create new API key**.
2. Copy — format `napi_...`. Treat as a secret; full account access by default.

```bash
export NEON_API_KEY="napi_..."
```

For organization-scoped access, generate the key from the org's settings
page instead — that limits the proxy to projects in that org.

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/neon/proxy_neon.py
```

Expected: tool list on stderr (~30 tools), then `list_projects -> {...}`
listing your Neon projects. MACAW console shows one entry under
`app_name=neon-proxy`.

If the result is empty, the API key has no projects — create one in the
Neon console first.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_neon.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "neon-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/neon/proxy_neon.py"],
      "env": { "NEON_API_KEY": "napi_..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add neon-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/neon/proxy_neon.py \
  -e NEON_API_KEY=napi_...
```

Then prompt: *"Use the neon-macaw tool to list my projects by name and ID."*

## Read-only mode (recommended for first contact)

Neon's MCP exposes destructive tools (`delete_project`, `run_sql` with
writes, migrations). To restrict the proxy to read-only ops without
touching MAPL policy, change the upstream URL in `proxy_neon.py`:

```python
upstream_url="https://mcp.neon.tech/mcp?readonly=true",
```

That removes write tools at the upstream — `list_tools()` will return only
the read-safe subset (`list_projects`, `describe_project`, `get_database_tables`,
`describe_table_schema`, `run_sql` for SELECTs, `list_slow_queries`, etc).

## Notes on what could go wrong

- **`401 Unauthorized`** — `NEON_API_KEY` is wrong, expired, or pointing at
  the wrong org.
- **`list_projects` returns empty** — the key works but you have no Neon
  projects yet, or the key is org-scoped and the org has no projects.
- **Streamable HTTP vs SSE** — Neon also exposes `/sse` for legacy clients.
  We use `/mcp` (Streamable HTTP); `SecureMCPProxy` handles it.
- **Production warning from Neon docs**: the remote MCP is intended for
  local dev / IDE integrations. Don't put a long-lived MACAW gateway in
  front of a prod Neon org without thinking through the blast radius —
  natural-language `delete_project` is a real risk. Read-only mode above
  is the cheapest mitigation.
