# MongoDB MCP — SecureMCPProxy

Wraps `mongodb/mongodb-mcp-server` in Docker over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Docker daemon running.
- Image pulled: `docker pull mongodb/mongodb-mcp-server:latest`.

Environment variables:

- `MDB_MCP_CONNECTION_STRING`
- `MDB_MCP_API_CLIENT_ID`
- `MDB_MCP_API_CLIENT_SECRET`

## Setup

```bash
export MDB_MCP_CONNECTION_STRING="..."
export MDB_MCP_API_CLIENT_ID="..."
export MDB_MCP_API_CLIENT_SECRET="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_mongodb.py            # stdio
python proxy_mongodb.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add mongodb-macaw python /path/to/proxy_mongodb.py \
  -e MDB_MCP_CONNECTION_STRING=... \
  -e MDB_MCP_API_CLIENT_ID=... \
  -e MDB_MCP_API_CLIENT_SECRET=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
