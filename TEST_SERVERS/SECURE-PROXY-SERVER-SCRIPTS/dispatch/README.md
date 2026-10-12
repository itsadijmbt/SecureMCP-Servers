# Dispatch Agents (operator) MCP — SecureMCPProxy

Wraps `dispatch mcp serve operator` (installed with `uvx` from `datadog-labs/dispatch_agents_cli`, tag `v0.11.7`) over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` (from `uv`) and `git` on `PATH`. The upstream is installed from its GitHub repository.
- A Dispatch account.

Environment variables:

- `DISPATCH_API_KEY`
- `DISPATCH_DEPLOY_URL`

`DISPATCH_API_KEY` is a Dispatch API key (it starts with `dak_`). Without it the upstream uses the session saved by `dispatch login`. `DISPATCH_DEPLOY_URL` is the backend URL. The default is `https://dispatchagents.ai`.

## Setup

```bash
export DISPATCH_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_dispatch.py
```

Register with Claude Code:

```bash
claude mcp add dispatch-macaw python /path/to/proxy_dispatch.py \
  -e DISPATCH_API_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```

Startup can exceed Claude Code's 30s default. Run `export MCP_TIMEOUT=120000` before starting Claude Code.
