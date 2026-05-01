# Supabase MCP — SecureMCPProxy (mcp-remote stdio)

Wraps Supabase's remote MCP server (`https://mcp.supabase.com/mcp`) with
MACAW via `mcp-remote`. One Python file, two tests.

Supabase MCP is OAuth 2.1 with proper Dynamic Client Registration — unlike
Figma. `mcp-remote` handles the OAuth dance once; SecureMCPProxy wraps the
resulting stdio.

## Prereqs

- MACAW LocalAgent running.
- Node + npm available on `$PATH` (`node -v && npx --version`).
- A Supabase account with at least one project.

## Defaults — security baked in

The script defaults to Supabase's recommended security posture:

- **`read_only=true`** — all queries run as a read-only Postgres user.
  Mutating tools (`apply_migration`, `create_project`, `deploy_edge_function`,
  branch ops, storage writes) are disabled server-side.
- **Project scoping** — opt-in via `SUPABASE_PROJECT_REF`. Without it, the
  server has access to all projects in your org. Set it before going beyond
  smoke testing.

## One-time OAuth setup

```bash
npx -y mcp-remote "https://mcp.supabase.com/mcp?read_only=true"
```

A browser tab opens. Sign in to Supabase, pick the **organization** that
contains the project you'll use, approve. Token cached in `~/.mcp-auth/`.
**Ctrl+C** once you see "Proxy established successfully".

## Test 1 — proxy works (1 dot)

```bash
# Unscoped (smoke target: list_projects)
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/supabase/proxy_supabase.py

# Or scoped to one project (smoke target: list_tables)
export SUPABASE_PROJECT_REF="<your-project-ref>"
/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/supabase/proxy_supabase.py
```

Find your `project_ref` under **Project Settings → General → Project ID**.

Expected: tool list on stderr (~15–25 tools depending on scope), then
`list_projects -> [...]` (or `list_tables -> [...]` when scoped). MACAW
console shows one entry under `app_name=supabase-proxy`.

First run is slow (10–20s) for `npx -y` download; subsequent runs reuse
the npm cache and the cached OAuth token.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_supabase.py`. Uncomment the **Test 2** block at the bottom.
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "supabase-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/supabase/proxy_supabase.py"],
      "env": { "SUPABASE_PROJECT_REF": "<your-project-ref-or-omit>" }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add supabase-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv/bin/python3.11 \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/supabase/proxy_supabase.py \
  -e SUPABASE_PROJECT_REF=<your-project-ref>
```

Then prompt: *"Use the supabase-macaw tool to call list_tables and show me
the first 10 table names."* MACAW console shows a second entry from the
LLM client.

## Notes on what could go wrong

- **First call hangs forever** — `mcp-remote` is waiting for OAuth. Run the
  one-time setup command first.
- **`Authorization failed` after working before** — token expired and
  refresh failed. `rm -rf ~/.mcp-auth` and redo the one-time setup.
- **`list_projects` returns "tool not available" when scoped** — expected.
  When `SUPABASE_PROJECT_REF` is set, account-level tools are removed. The
  script auto-swaps to `list_tables` for the smoke check.
- **Mutating call fails with permission error** — `read_only=true` is doing
  its job. Drop the param if you need write access (not recommended; do it
  on a development project only, never production).
- **`$HOME` mismatch when spawned by Gemini** — the script forwards `HOME`
  explicitly so `mcp-remote` finds `~/.mcp-auth/`. If Gemini ever runs
  under a different user / sandbox, the cache won't be visible.

## Why not the local CLI server (`http://localhost:54321/mcp`)?

Supabase's local CLI MCP is a limited subset — no OAuth, no full feature
set. The remote server is the canonical target and exercises the OAuth
chain end-to-end. If you specifically need to test against `supabase
start` locally, swap the upstream URL — same wrapper.
