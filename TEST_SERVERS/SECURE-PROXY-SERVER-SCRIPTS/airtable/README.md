# Airtable MCP — SecureMCPProxy

Wraps the community `airtable-mcp-server` npm package (local stdio, PAT auth)
with MACAW. One Python file, two tests.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).
- An Airtable account and at least one base.

## Credentials

Create a personal access token at
https://airtable.com/create/tokens. **Required scopes** for the smoke test:

- `schema.bases:read`
- `data.records:read`

Optional scopes for richer testing through Test 2:

- `schema.bases:write`
- `data.records:write`
- `data.recordComments:read` / `data.recordComments:write`

**Access:** select the bases you want to expose, or "Add all resources".

```bash
export AIRTABLE_API_KEY="pat123.abc123..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/airtable/proxy_airtable.py
```

Expected: tool list on stderr (~16 tools), then `list_bases -> {...}` listing
your bases by ID and name. MACAW console shows one entry under
`app_name=airtable-proxy`.

First run is slow (10–20s) because `npx -y` downloads the package. Subsequent
runs reuse the npm cache.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_airtable.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "airtable-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/airtable/proxy_airtable.py"],
      "env": { "AIRTABLE_API_KEY": "pat123.abc123..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add airtable-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/airtable/proxy_airtable.py \
  -e AIRTABLE_API_KEY=pat123.abc123...
```

Then prompt: *"Use the airtable-macaw tool to list my bases by name and ID."*
MACAW console shows a second entry — originated from the LLM client, not the
smoke test.

## Notes on what could go wrong

- **First-run hang on `npx -y`** — the package is downloading. Give it 30s
  before assuming it's broken.
- **`401 Unauthorized` / empty `list_bases`** — token missing the
  `schema.bases:read` scope, or token doesn't have access to any base. Check
  the token's resource selection at https://airtable.com/create/tokens.
- **PAT format** — Airtable PATs look like `pat123.abc123...` (the part after
  the dot is much longer). If yours doesn't match this shape, you may have a
  legacy API key — generate a new PAT.
- **Write tools fail with read-only token** — `create_record`, `update_records`,
  `delete_records`, `create_table`, etc. need the write scopes. Add only what
  you'll actually exercise; principle of least privilege.
