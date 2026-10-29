# dbt MCP — SecureMCPProxy

Wraps `uvx dbt-mcp` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).

Environment variables:

- `DBT_HOST`
- `DBT_TOKEN`
- `DBT_PROD_ENV_ID`
- `DBT_DEV_ENV_ID`
- `DBT_USER_ID`
- `DBT_ACCOUNT_ID`
- `DBT_PROJECT_DIR`
- `DBT_PATH`
- `MULTICELL_ACCOUNT_PREFIX`

## Setup

```bash
export DBT_HOST="..."
export DBT_TOKEN="..."
export DBT_PROD_ENV_ID="..."
export DBT_DEV_ENV_ID="..."
export DBT_USER_ID="..."
export DBT_ACCOUNT_ID="..."
export DBT_PROJECT_DIR="..."
export DBT_PATH="..."
export MULTICELL_ACCOUNT_PREFIX="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_dbt.py
```

Register with Claude Code:

```bash
claude mcp add dbt-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export DBT_HOST="..." && \
  export DBT_TOKEN="..." && \
  export DBT_PROD_ENV_ID="..." && \
  export DBT_DEV_ENV_ID="..." && \
  export DBT_USER_ID="..." && \
  export DBT_ACCOUNT_ID="..." && \
  export DBT_PROJECT_DIR="..." && \
  export DBT_PATH="..." && \
  export MULTICELL_ACCOUNT_PREFIX="..." && \
  python /path/to/proxy_dbt.py'
```
