"""
arxiv-proxy -> SecureMCPProxy, served natively.

Prereq:
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_arxiv.py

Claude Code:
    claude mcp add arxiv-macaw python /path/to/proxy_arxiv.py \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    No API key or token: arXiv is a public service. Papers are stored in ~/.arxiv-mcp-server/papers.
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

proxy = SecureMCPProxy(
    app_name="arxiv-proxy",
    command=["uvx", "arxiv-mcp-server"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
    },
)
logging.info("arxiv-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
