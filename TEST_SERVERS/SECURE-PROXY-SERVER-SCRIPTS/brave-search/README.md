# Brave Search MCP — SecureMCPProxy

Wraps `npx -y @brave/brave-search-mcp-server --transport stdio`. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `BRAVE_API_KEY`  — required.

## Setup

```bash
export BRAVE_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_brave_search.py
```

Register with Claude Code:

```bash
claude mcp add brave-search-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export BRAVE_API_KEY="..." && \
  python /path/to/proxy_brave_search.py'
```
