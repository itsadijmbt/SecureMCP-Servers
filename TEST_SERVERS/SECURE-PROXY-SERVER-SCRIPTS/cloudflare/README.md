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

python proxy_cloudflare.py            # stdio
python proxy_cloudflare.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add cloudflare-macaw python /path/to/proxy_cloudflare.py \
  -e CLOUDFLARE_API_TOKEN=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
