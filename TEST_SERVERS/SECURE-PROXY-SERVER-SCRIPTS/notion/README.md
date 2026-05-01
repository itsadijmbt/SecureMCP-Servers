# Notion MCP — SecureMCPProxy

Wraps the official `@notionhq/notion-mcp-server` npm package (local stdio,
internal-integration token auth) with MACAW. One Python file, two tests.

We use the **local server with `NOTION_TOKEN`** because it's the simplest
path. The remote server (`https://mcp.notion.com`) uses OAuth and would
also wrap via `mcp-remote`; the local path has fewer moving parts and works
without a browser callback.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).
- A Notion workspace and an internal integration with at least one page or
  database connected to it.

## Credentials

1. Go to https://www.notion.so/profile/integrations and create an internal
   integration (or pick an existing one). Copy the integration secret —
   format: `ntn_...`.
2. **Crucial:** in the integration's **Access** tab, grant it access to at
   least one page or database. Notion integrations can only see content
   explicitly shared with them. An integration with no granted access will
   pass auth but `API-post-search` returns an empty list — looks like a
   wrap failure but isn't.
3. (Optional) For least privilege, set the integration to "Read content"
   only in the Capabilities tab.

```bash
export NOTION_TOKEN="ntn_..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/notion/proxy_notion.py
```

Expected: tool list on stderr (~22 tools in v2.0), then `API-post-search ->`
followed by a JSON list of pages/databases the integration can see. MACAW
console shows one entry under `app_name=notion-proxy`.

First run is slow (10–20s) because `npx -y` downloads the package.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_notion.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "notion-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/notion/proxy_notion.py"],
      "env": { "NOTION_TOKEN": "ntn_..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add notion-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/notion/proxy_notion.py \
  -e NOTION_TOKEN=ntn_...
```

Then prompt: *"Use the notion-macaw tool to search my workspace and list
the first 5 pages by title."* MACAW console shows a second entry from the
LLM client.

## Notes on what could go wrong

- **Empty `API-post-search` result with no error** — the integration has
  no pages or databases connected to it. Fix in the integration's Access
  tab, not in the script.
- **`401 Unauthorized`** — `NOTION_TOKEN` is wrong or revoked.
- **`object_not_found` on later tool calls** — you're trying to operate on
  a page/database the integration does not have access to. Connect it via
  the page's "..." menu → "Add connections", or via the integration's
  Access tab.
- **v2.0 breaking changes** — if you have hardcoded prompts referencing
  `post-database-query`, they no longer exist. Use `query-data-source`
  (with `data_source_id` instead of `database_id`).
