"""
cloudflare-proxy -> SecureMCPProxy, served natively.

Prereq:
    export CLOUDFLARE_API_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_cloudflare.py

Claude Code:
    claude mcp add cloudflare-macaw python /path/to/proxy_cloudflare.py \
      -e CLOUDFLARE_API_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("CLOUDFLARE_API_TOKEN")
if not token:
    raise ValueError("CLOUDFLARE_API_TOKEN is not set")

CF_MCP_URL = "https://bindings.mcp.cloudflare.com/mcp"

proxy = SecureMCPProxy(
    app_name="cloudflare-proxy",
    upstream_url=CF_MCP_URL,
    upstream_auth={"type": "bearer", "token": token},
)
logging.info("cloudflare-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
