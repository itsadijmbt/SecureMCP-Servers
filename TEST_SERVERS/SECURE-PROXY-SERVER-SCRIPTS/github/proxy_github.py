"""
github-proxy -> SecureMCPProxy, served natively.

Prereq:
    export GITHUB_PERSONAL_ACCESS_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_github.py

Claude Code:
    claude mcp add github-macaw python /path/to/proxy_github.py \
      -e GITHUB_PERSONAL_ACCESS_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN")
if not token:
    raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN is not set")

proxy = SecureMCPProxy(
    app_name="github-proxy",
    upstream_url="https://api.githubcopilot.com/mcp/",
    upstream_auth={"type": "bearer", "token": token},
)
logging.info("github-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
