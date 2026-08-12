# Neon MCP — SecureMCPProxy

Wraps `https://mcp.neon.tech/mcp` over HTTPS with a bearer API key. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.

Environment variables:

- `NEON_API_KEY`  — required.

## Setup

```bash
export NEON_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_neon.py            # stdio
python proxy_neon.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add neon-macaw python /path/to/proxy_neon.py \
  -e NEON_API_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
