# Excel MCP — SecureMCPProxy

Wraps `uvx excel-mcp-server stdio --allow-dir <EXCEL_FILES_PATH>` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uvx` on `PATH` (from `uv`).
- A folder that holds the workbooks.

Environment variables:

- `EXCEL_FILES_PATH`  — required.

The upstream only opens workbooks inside this folder. No API key or token is needed.

## Setup

```bash
export EXCEL_FILES_PATH="/path/to/workbooks"
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_excel.py
```

Register with Claude Code:

```bash
claude mcp add excel-macaw python /path/to/proxy_excel.py \
  -e EXCEL_FILES_PATH=/path/to/workbooks \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
