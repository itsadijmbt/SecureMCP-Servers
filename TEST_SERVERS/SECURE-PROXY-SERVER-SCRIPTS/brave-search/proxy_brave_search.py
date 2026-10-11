"""
brave-search-proxy -> SecureMCPProxy, served natively.

Prereq:
    export BRAVE_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_brave_search.py

Claude Code:
    claude mcp add brave-search-macaw python /path/to/proxy_brave_search.py \
      -e BRAVE_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("BRAVE_API_KEY")
if not api_key:
    raise ValueError(
        "BRAVE_API_KEY is not set. "
        "Get a key at https://api-dashboard.search.brave.com/app/keys"
    )

proxy = SecureMCPProxy(
    app_name="brave-search-proxy",
    command=["npx", "-y", "@brave/brave-search-mcp-server", "--transport", "stdio"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "BRAVE_API_KEY": api_key,
    },
)
logging.info("brave-search-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
