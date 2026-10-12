# Redis MCP — SecureMCPProxy

Wraps `uvx --from redis-mcp-server@latest redis-mcp-server` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).
- A Redis server the proxy can reach.

Environment variables:

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_DB`
- `REDIS_USERNAME`
- `REDIS_PWD`
- `REDIS_SSL`
- `REDIS_CLUSTER_MODE`

All are optional. Without them the upstream connects to `127.0.0.1:6379`, database 0, user `default`, no password.

## Setup

```bash
export REDIS_HOST="..."
export REDIS_PORT="..."
export REDIS_USERNAME="..."
export REDIS_PWD="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_redis.py
```

Register with Claude Code:

```bash
claude mcp add redis-macaw python /path/to/proxy_redis.py \
  -e REDIS_HOST=... \
  -e REDIS_PORT=... \
  -e REDIS_USERNAME=... \
  -e REDIS_PWD=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
