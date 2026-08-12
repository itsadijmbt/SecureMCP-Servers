# Brave Search MCP — SecureMCPProxy

Wraps `npx -y @brave/brave-search-mcp-server --transport stdio`. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `BRAVE_API_KEY`

## Setup

```bash
export BRAVE_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_brave_search.py            # stdio
python proxy_brave_search.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add brave-search-macaw python /path/to/proxy_brave_search.py \
  -e BRAVE_API_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
