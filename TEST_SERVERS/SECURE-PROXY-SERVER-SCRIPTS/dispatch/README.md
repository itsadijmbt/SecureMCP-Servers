# Dispatch Agents (operator) MCP — SecureMCPProxy

Wraps `dispatch mcp serve operator` (installed with `uvx` from `datadog-labs/dispatch_agents_cli`, tag `v0.11.7`) over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` (from `uv`) and `git` on `PATH`. The upstream is installed from GitHub. The PyPI package named `dispatch-cli` is a different project.
- A Dispatch account.

Environment variables:

- `DISPATCH_API_KEY`
- `DISPATCH_DEPLOY_URL`

`DISPATCH_API_KEY` is a Dispatch API key (it starts with `dak_`). Without it the upstream uses the session saved by `dispatch login`. `DISPATCH_DEPLOY_URL` is the backend URL; without it the upstream uses `https://dispatchagents.ai`.

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

The proxy starts in about 26 seconds, close to the roughly 30 seconds Claude Code waits by default. If Claude Code shows the server as failed, run `export MCP_TIMEOUT=120000` in the shell that starts Claude Code.

## Policy

`Policy/server_policy_v0.1.0.json` is for the app `dispatch-proxy`, the same name as `app_name` in `proxy_dispatch.py`. Tools are named `tool:dispatch-proxy/<tool>`.

- Allowed: 16 tools. Tools that only read: they send `GET` to the Dispatch backend, or read local state (`list_local_routers`, `read_local_agent_logs`).
- Denied: 16 tools. Tools that send `POST`, `PATCH` or `DELETE` to the backend, start a local process or write files (deploy, uninstall, stop, reboot, invoke, publish, schedules, local dev tools, feedback).
- No parameter limits. Every tool takes one `request` object, and the upstream checks its fields itself (for example `limit` must be 1 to 100).

## Checked

- With `dispatch_agents_cli` v0.11.7: 32 tools, the same names, descriptions and input schemas as the upstream serves on its own.
- Against a local stand-in for the Dispatch backend, not a real Dispatch account.
- The upstream starts without a key. A call then comes back with the upstream's own login message.
