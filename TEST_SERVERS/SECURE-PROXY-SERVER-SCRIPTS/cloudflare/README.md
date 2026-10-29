# Cloudflare MCP — SecureMCPProxy

Wraps `https://bindings.mcp.cloudflare.com/mcp` over HTTPS with a bearer token. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.

Environment variables:

- `CLOUDFLARE_API_TOKEN`  — required.

## Setup

```bash
export CLOUDFLARE_API_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_cloudflare.py
```

Register with Claude Code:

```bash
claude mcp add cloudflare-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export CLOUDFLARE_API_TOKEN="..." && \
  python /path/to/proxy_cloudflare.py'
```
