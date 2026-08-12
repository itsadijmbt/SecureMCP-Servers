# Atlassian MCP — SecureMCPProxy

Wraps `npx -y mcp-remote https://mcp.atlassian.com/v1/mcp/authv2` — OAuth in the browser on first run. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js 20+ on `PATH` (`mcp-remote` needs it; Node 18 fails with `ReferenceError: File is not defined`).

No credentials required.

## Setup

```bash
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_atlassian.py            # stdio
python proxy_atlassian.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add atlassian-macaw python /path/to/proxy_atlassian.py \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
