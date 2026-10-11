"""
chrome-devtools-proxy -> SecureMCPProxy, served natively.

Prereq:
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_chrome_devtools.py

Claude Code:
    claude mcp add chrome-devtools-macaw python /path/to/proxy_chrome_devtools.py \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

proxy = SecureMCPProxy(
    app_name="chrome-devtools-proxy",
    command=[
        "npx", "-y", "chrome-devtools-mcp@latest",
        "--headless",
        "--isolated",
    ],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
    },
)
logging.info("chrome-devtools-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
