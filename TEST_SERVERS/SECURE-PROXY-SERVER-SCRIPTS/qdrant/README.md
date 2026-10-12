# Qdrant MCP — SecureMCPProxy

Wraps `uvx --python 3.12 mcp-server-qdrant` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`). Python 3.12 is pinned: `mcp-server-qdrant` 0.8.1 does not install on Python 3.14.

Environment variables:

- `QDRANT_URL`
- `QDRANT_API_KEY`
- `QDRANT_LOCAL_PATH`
- `COLLECTION_NAME`
- `EMBEDDING_MODEL`
- `QDRANT_SEARCH_LIMIT`
- `QDRANT_READ_ONLY`

Set `QDRANT_URL` (with `QDRANT_API_KEY` if the server needs one), or `QDRANT_LOCAL_PATH`. One of the two is required, and the upstream does not accept both.

## Setup

```bash
export QDRANT_URL="..."
export QDRANT_API_KEY="..."
export COLLECTION_NAME="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_qdrant.py
```

Register with Claude Code:

```bash
claude mcp add qdrant-macaw python /path/to/proxy_qdrant.py \
  -e QDRANT_URL=... \
  -e QDRANT_API_KEY=... \
  -e COLLECTION_NAME=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
