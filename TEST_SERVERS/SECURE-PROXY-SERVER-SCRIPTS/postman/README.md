# Postman MCP — SecureMCPProxy

Wraps `npx -y @postman/postman-mcp-server --minimal` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `POSTMAN_API_KEY`  — required.

## Setup

```bash
export POSTMAN_API_KEY="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_postman.py            # stdio
python proxy_postman.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add postman-macaw python /path/to/proxy_postman.py \
  -e POSTMAN_API_KEY=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
