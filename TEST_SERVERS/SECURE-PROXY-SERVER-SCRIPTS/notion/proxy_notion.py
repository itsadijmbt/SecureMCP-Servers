"""
notion-proxy -> SecureMCPProxy, served natively.

Prereq:
    export NOTION_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_notion.py

Claude Code:
    claude mcp add notion-macaw python /path/to/proxy_notion.py \
      -e NOTION_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("NOTION_TOKEN")
if not token:
    raise ValueError("NOTION_TOKEN is not set (format: ntn_...)")

proxy = SecureMCPProxy(
    app_name="notion-proxy",
    command=["npx", "-y", "@notionhq/notion-mcp-server"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "NOTION_TOKEN": token,
    },
)
logging.info("notion-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
