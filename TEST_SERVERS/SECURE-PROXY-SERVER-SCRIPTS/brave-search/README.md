# Brave Search MCP — SecureMCPProxy

Wraps the official `@brave/brave-search-mcp-server` npm package (local
stdio, API-key auth) with MACAW. One Python file, two tests.

Same shape as Airtable / Postman / Notion / Neon — local stdio via `npx
-y` + a bearer-style API key in env. No OAuth dance, no Docker (unless
you specifically want it), no allowlist wall.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).
- A Brave Search API key. Free tier exists — Data for AI plan grants 2K
  queries/month at no charge.

## Credentials

1. Sign up at https://brave.com/search/api/.
2. Generate a key at https://api-dashboard.search.brave.com/app/keys.
3. Format starts with `BSA` (e.g. `BSAxxx...`). Copy — full key is shown
   only at creation.

```bash
export BRAVE_API_KEY="BSA..."
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/brave-search/proxy_brave_search.py
```

Expected: tool list on stderr (~8 tools), then
`brave_web_search -> {"web":{"results":[...]}}` with real Brave search
hits for "model context protocol". MACAW console shows one entry under
`app_name=brave-search-proxy`.

First run is slow (10–20s) for `npx -y` to fetch the package. Subsequent
runs reuse the npm cache. Smoke test costs **1** search request against
your monthly quota.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_brave_search.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "brave-search-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/brave-search/proxy_brave_search.py"],
      "env": { "BRAVE_API_KEY": "BSA..." }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add brave-search-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/brave-search/proxy_brave_search.py \
  -e BRAVE_API_KEY=BSA...
```

Then prompt: *"Use the brave-search-macaw tool to search for 'MACAW
security' and list the top 3 results as: <title> — <url>."* MACAW console
shows a second entry from the LLM client.

## Tool surface

- `brave_web_search` — general web search (smoke target).
- `brave_news_search` — news search.
- `brave_local_search` / `brave_place_search` — places, lat/lon-aware.
- `brave_video_search`, `brave_image_search` — multimedia search.
- `brave_llm_context` — search result formatted for LLM consumption.
- `brave_summarizer` — summarize a result; takes a key from a prior search.

All except `brave_summarizer` accept just `{"query": "..."}` for a
minimal call.

## Notes on what could go wrong

- **First run hangs ~20s** — `npx` is downloading the package. Be patient.
- **`401 Unauthorized` / `Authentication failed`** — `BRAVE_API_KEY` is
  wrong, expired, or you copied a fragment. Re-check at
  https://api-dashboard.search.brave.com/app/keys.
- **`429 Too Many Requests`** — you've hit your monthly free-tier quota
  (2K queries by default) or the per-second rate limit (1 req/s on free
  tier). Wait or upgrade.
- **`Tool not found: brave_web_search`** — Brave renamed it. Read the
  printed tools list and swap the smoke target on line 50.
- **Empty `web.results`** — query returned no hits (try a less obscure
  query). Wrap is fine.
