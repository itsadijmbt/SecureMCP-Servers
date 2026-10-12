"""
databricks-proxy -> SecureMCPProxy, served natively.

Prereq:
    export DATABRICKS_MCP_URL="..."
    export DATABRICKS_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python mcp_databricks_proxy.py

Claude Code:
    claude mcp add databricks-macaw python /path/to/mcp_databricks_proxy.py \
      -e DATABRICKS_MCP_URL=... \
      -e DATABRICKS_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    DATABRICKS_MCP_URL is the managed MCP URL of your workspace, for example https://<workspace>/api/2.0/mcp/sql.
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("DATABRICKS_TOKEN")
if not token:
    raise ValueError("DATABRICKS_TOKEN is not set (workspace PAT)")

DATABRICKS_MCP_URL = os.environ.get("DATABRICKS_MCP_URL")
if not DATABRICKS_MCP_URL:
    raise ValueError(
        "DATABRICKS_MCP_URL is not set -- e.g. https://<workspace>/api/2.0/mcp/sql")

proxy = SecureMCPProxy(
    app_name="databricks-proxy",
    upstream_url=DATABRICKS_MCP_URL,
    upstream_auth={"type": "bearer", "token": token},
)
logging.info("databricks-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
