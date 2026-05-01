# Postman MCP — SecureMCPProxy

Wraps the official `@postman/postman-mcp-server` npm package (local stdio
mode) with MACAW. One Python file, two tests.

We use the **local server with API key auth** because it's the simplest
path: no OAuth dance, no Docker, no remote allowlists. The remote server
(`https://mcp.postman.com`) supports OAuth with proper DCR and would also
wrap cleanly via `mcp-remote`, but the local path has fewer moving parts.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).

## Credentials

Get a Postman API key: Postman → your profile → **Settings → API keys →
Generate API key**.

```bash
export POSTMAN_API_KEY="PMAK-..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/postman/proxy_postman.py
```

Expected: tool list on stderr (~37 tools in minimal mode), then
`getWorkspaces -> {...}` listing your accessible workspaces. MACAW console
shows one entry under `app_name=postman-proxy`.

First run is slow (10–20s) because `npx -y` downloads the package. Subsequent
runs reuse the npm cache.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_postman.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "postman-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/postman/proxy_postman.py"],
      "env": { "POSTMAN_API_KEY": "PMAK-..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add postman-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/postman/proxy_postman.py \
  -e POSTMAN_API_KEY=PMAK-...
```

Then prompt: *"Use the postman-macaw tool to list my workspaces."* MACAW
console shows a second entry — originated from the LLM client, not the
smoke test.

## Toolset modes

The script defaults to `--minimal` (~37 tools, fastest). To switch:

- **Full** (100+ tools): change `"--minimal"` → `"--full"` in the script.
- **Code** (client-code generation): change `"--minimal"` → `"--code"`.

Larger toolsets bloat the LLM's context window — keep `--minimal` unless
you're actually exercising advanced features.

## Notes on what could go wrong

- **First-run hang on `npx -y`** — the package is downloading. Give it 30s
  before assuming it's broken.
- **`401 Unauthorized` on tool calls** — API key invalid or revoked. Check
  Postman → Settings → API keys.
- **`getWorkspaces` returns empty** — the API key's user has no workspaces,
  or the key is scoped to a single workspace they're not in. Try the call
  with a workspace UUID arg to verify auth itself works.
- **Region: EU users** add `"--region", "eu"` to the `args` list. The local
  server hits `api.getpostman.com` by default (US).
