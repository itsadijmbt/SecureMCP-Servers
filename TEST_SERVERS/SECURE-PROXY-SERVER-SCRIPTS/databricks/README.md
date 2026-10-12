# Databricks MCP — SecureMCPProxy

Wraps the Databricks managed MCP endpoint in `DATABRICKS_MCP_URL` over HTTPS with a bearer token. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.

Environment variables:

- `DATABRICKS_MCP_URL`  — required.
- `DATABRICKS_TOKEN`  — required.

`DATABRICKS_MCP_URL` is the managed MCP URL of your workspace, for example `https://<workspace>/api/2.0/mcp/sql`. `DATABRICKS_TOKEN` is a workspace personal access token.

## Setup

```bash
export DATABRICKS_MCP_URL="..."
export DATABRICKS_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python mcp_databricks_proxy.py
```

Register with Claude Code:

```bash
claude mcp add databricks-macaw python /path/to/mcp_databricks_proxy.py \
  -e DATABRICKS_MCP_URL=... \
  -e DATABRICKS_TOKEN=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
