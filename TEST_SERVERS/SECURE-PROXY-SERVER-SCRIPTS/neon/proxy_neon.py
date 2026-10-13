"""
neon-proxy -> SecureMCPProxy, served natively.

Prereq:
    export NEON_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_neon.py

Claude Code:
    claude mcp add neon-macaw python /path/to/proxy_neon.py \
      -e NEON_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging

from macaw_adapters.mcp import SecureMCPProxy

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

NEON_API_KEY = os.environ.get("NEON_API_KEY")
if not NEON_API_KEY:
    raise ValueError("NEON_API_KEY is not set (create at https://console.neon.tech/app/settings/api-keys)")

NEON_MCP_URL = "https://mcp.neon.tech/mcp"

proxy = SecureMCPProxy(
    app_name="neon-proxy",
    upstream_url=NEON_MCP_URL,
    upstream_auth={"type": "bearer", "token": NEON_API_KEY},
)
logging.info("neon-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
