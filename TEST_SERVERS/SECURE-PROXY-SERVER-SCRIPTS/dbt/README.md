# dbt MCP — SecureMCPProxy

Wraps the official `dbt-mcp` Python package (run via `uvx`) with MACAW.
One Python file, two tests.

The upstream exposes ~50 tools across nine categories: SQL, Semantic
Layer, Discovery, dbt CLI, Admin API, dbt Codegen, dbt LSP, Product Docs,
and Server Metadata. Each category needs different env config to activate;
the smoke test in Test 1 uses **Server Metadata** which works with zero
config.

## Prereqs

- MACAW LocalAgent running.
- `uv` / `uvx` installed (verified present in this environment at
  `/home/itsadijmbt/.local/bin/uvx`). If it goes missing on a fresh box:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## Credentials

**Smoke test (Test 1) needs nothing.** `get_mcp_server_version` and the
Product Docs tools (`search_product_docs`, `get_product_doc_pages`) work
without a dbt account.

For the richer tool groups, set whichever applies:

| Tool group | Required env |
|---|---|
| SQL, Semantic Layer, Discovery, Admin API | `DBT_HOST`, `DBT_TOKEN`, `DBT_PROD_ENV_ID`, `DBT_DEV_ENV_ID`, `DBT_USER_ID` |
| dbt CLI (`run`, `build`, `test`, …) | `DBT_PROJECT_DIR` pointing to a local dbt project; usually also `DBT_PATH` |
| dbt LSP column-lineage | dbt-lsp via the dbt Labs VS Code extension installed locally |

The upstream auto-disables any group whose config is missing. Missing
config does **not** crash the server — it just hides those tools.

```bash
# Optional; only what you have:
# export DBT_HOST="cloud.getdbt.com"
# export DBT_TOKEN="dbtu_..."
# export DBT_PROD_ENV_ID="123456"
# export DBT_DEV_ENV_ID="123457"
# export DBT_USER_ID="..."
# export DBT_PROJECT_DIR="/path/to/your/dbt/project"
```

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/dbt/proxy_dbt.py
```

Expected: tool list on stderr (the active subset depending on what env you
set), then `get_mcp_server_version -> {...}` with the version string. MACAW
console shows one entry under `app_name=dbt-proxy`.

First run is slow (15–60s) because `uvx` downloads `dbt-mcp` and its
dependencies into a uv-managed virtualenv. Subsequent runs reuse the cache.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_dbt.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "dbt-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/dbt/proxy_dbt.py"],
      "env": {}
    }
  }
}
```

(Add any of the optional `DBT_*` vars to the `env` block above when you
want to expose more tools.)

**Claude Code CLI:**

```bash
claude mcp add dbt-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/dbt/proxy_dbt.py
```

Then prompt: *"Use dbt-macaw to call get_mcp_server_version, then
search_product_docs for 'incremental models' and show the top 3 result titles."*

## Notes on what could go wrong

- **First-run hang on `uvx`** — package download in progress; can take a
  full minute the first time. Subsequent runs are instant from cache.
- **Empty tool list** — if literally nothing shows up, `dbt-mcp` likely
  failed to import. Run `uvx dbt-mcp --help` directly to surface the error.
- **`401 Unauthorized` on Platform tools** — `DBT_TOKEN` invalid or
  scoped to wrong account; check `DBT_HOST` matches your dbt Cloud region
  (`cloud.getdbt.com` for US multi-tenant, others for EU/AU).
- **CLI tools (`run`, `build`, etc.) missing or erroring** — `DBT_PROJECT_DIR`
  not pointed at a real dbt project, or the project's adapter isn't
  installed in the `dbt-mcp` venv. Avoid `build` / `run` until you're
  confident the integration is what you want; they materialize tables.
- **dbt CLI tools modify your warehouse** — per the upstream README,
  these tools can change models, sources, and warehouse objects. Treat
  the prompt that triggers them like a deploy.
