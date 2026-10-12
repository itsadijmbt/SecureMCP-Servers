"""
falcon-proxy -> SecureMCPProxy, served natively.

Prereq:
    export FALCON_CLIENT_ID="..."
    export FALCON_CLIENT_SECRET="..."
    export FALCON_BASE_URL="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_falcon.py

Claude Code:
    export MCP_TIMEOUT=120000
    claude mcp add falcon-macaw python /path/to/proxy_falcon.py \
      -e FALCON_CLIENT_ID=... \
      -e FALCON_CLIENT_SECRET=... \
      -e FALCON_BASE_URL=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    FALCON_BASE_URL is the API URL of your CrowdStrike region, for example https://api.us-2.crowdstrike.com.
    Without it the upstream uses https://api.crowdstrike.com (US-1).
    MCP_TIMEOUT is needed: with all 169 tools the proxy takes about 100 seconds to start, and Claude Code
    waits about 30 seconds by default. FALCON_MCP_MODULES=hosts,detections loads fewer tools.
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

if not os.environ.get("FALCON_CLIENT_ID") or not os.environ.get("FALCON_CLIENT_SECRET"):
    raise ValueError(
        "FALCON_CLIENT_ID and FALCON_CLIENT_SECRET are not set. "
        "The upstream cannot log in to the Falcon API without them."
    )

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
}
for k in (
    "FALCON_CLIENT_ID",
    "FALCON_CLIENT_SECRET",
    "FALCON_BASE_URL",
    "FALCON_MEMBER_CID",
    "FALCON_MCP_MODULES",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="falcon-proxy",
    # The upstream logs in to the Falcon API when it starts and stops if the login fails.
    command=["uvx", "falcon-mcp"],
    env=upstream_env,
)
logging.info("falcon-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
