"""
excel-proxy -> SecureMCPProxy, served natively.

Prereq:
    export EXCEL_FILES_PATH="/path/to/workbooks"
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_excel.py

Claude Code:
    claude mcp add excel-macaw python /path/to/proxy_excel.py \
      -e EXCEL_FILES_PATH=/path/to/workbooks \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    No API key or token: the server works on local files only.
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

files_path = os.environ.get("EXCEL_FILES_PATH")
if not files_path:
    raise ValueError("EXCEL_FILES_PATH is not set (the folder the workbooks must be in)")

proxy = SecureMCPProxy(
    app_name="excel-proxy",
    # --allow-dir: without it the upstream opens any absolute path to an Excel file.
    command=["uvx", "excel-mcp-server", "stdio", "--allow-dir", files_path],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
    },
)
logging.info("excel-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
