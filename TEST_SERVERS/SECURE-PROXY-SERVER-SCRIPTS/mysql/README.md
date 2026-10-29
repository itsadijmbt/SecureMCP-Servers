# MySQL MCP — SecureMCPProxy

Wraps `uvx mysql_mcp_server` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).
- A MySQL server the proxy can reach.

Environment variables:

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`  — required.
- `MYSQL_PASSWORD`  — required.
- `MYSQL_DATABASE`

`MYSQL_HOST` defaults to `localhost` and `MYSQL_PORT` to `3306`. Leave `MYSQL_DATABASE` out to work across databases.

## Setup

```bash
export MYSQL_HOST="..."
export MYSQL_PORT="..."
export MYSQL_USER="..."
export MYSQL_PASSWORD="..."
export MYSQL_DATABASE="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_mysql.py
```

Register with Claude Code:

```bash
claude mcp add mysql-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export MYSQL_HOST="..." && \
  export MYSQL_PORT="..." && \
  export MYSQL_USER="..." && \
  export MYSQL_PASSWORD="..." && \
  export MYSQL_DATABASE="..." && \
  python /path/to/proxy_mysql.py'
```
