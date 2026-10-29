# Atlassian MCP — SecureMCPProxy

Wraps `npx -y mcp-remote https://mcp.atlassian.com/v2/mcp` — OAuth in the browser on first run. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js 20+ on `PATH` (`mcp-remote` needs it).

No credentials required.

## Setup

```bash
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_atlassian.py
```

Register with Claude Code:

```bash
claude mcp add atlassian-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  python /path/to/proxy_atlassian.py'
```
