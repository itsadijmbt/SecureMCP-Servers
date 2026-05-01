# GitHub MCP — SecureMCPProxy

Wraps GitHub's remote MCP server (`https://api.githubcopilot.com/mcp/`) with
MACAW. One Python file, two tests.


## Credentials

```bash
export GITHUB_PERSONAL_ACCESS_TOKEN="ghp_xxx"
```

PAT scopes: `read:user` is enough for `get_me`. Add `repo`, `issues`, etc. only
if you intend to exercise those tools through Test 2.

## Test 1 — proxy works (1 dot)

```bash
/home/itsadijmbt/MACAW-MCP-STORE/venv311/bin/python \
    TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/github/proxy_github.py
```

Expected: tool list on stderr, then `get_me -> {...}`. MACAW console shows
one entry under `app_name=github-remote-proxy`.

## Test 2 — real CLI through the proxy (2nd dot)

1. Open `proxy_github.py`. Uncomment the **Test 2** block (the `# import asyncio`
   ... `# asyncio.run(_main())` lines at the bottom).
2. Configure your CLI to spawn this script as an MCP server.

**Gemini CLI** — `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "github-macaw": {
      "command": "/home/itsadijmbt/MACAW-MCP-STORE/venv311/bin/python",
      "args": ["/home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/github/proxy_github.py"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx" }
    }
  }
}
```

**Claude Code CLI:**

```bash
claude mcp add github-macaw \
  /home/itsadijmbt/MACAW-MCP-STORE/venv311/bin/python \
  /home/itsadijmbt/MACAW-MCP-STORE/TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/github/proxy_github.py \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxx
```

Then in the CLI, prompt: *"Use the github-macaw tool to call get_me and show
my login."* MACAW console shows a second entry — this one originated from a
real LLM client, not the smoke test.

## Notes on what could go wrong

- The proxy's `list_tools()` uses the key `schema`, not `inputSchema` (renamed
  in the SDK). Test 2 maps `t["schema"]` → MCP `inputSchema`. If a future
  upstream server omits a schema, the fallback `{"type": "object"}` keeps the
  CLI's tool registration valid.
- `proxy.call_tool` runs `asyncio.run` internally per call. That's fine for
  stdio handlers (each `tools/call` request is its own task), but it means the
  proxy is not safe to share across event loops if you ever embed it in an
  existing async app. Not a concern for this script.
- If GitHub returns 41 tools, the LLM's context can balloon. To trim, set
  `GITHUB_TOOLSETS=repos,issues` in the env passed to `SecureMCPProxy(env=...)`
  on the local Docker variant — for the remote HTTP variant, GitHub's server
  applies the default toolset and `--tools`/`--toolsets` aren't exposed.
