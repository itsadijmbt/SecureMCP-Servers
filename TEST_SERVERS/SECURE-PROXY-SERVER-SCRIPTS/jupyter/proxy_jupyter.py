"""
jupyter-proxy -> SecureMCPProxy, served natively.

Prereq:
    export JUPYTER_URL="..."
    export JUPYTER_TOKEN="..."
    export DOCUMENT_ID="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_jupyter.py

Claude Code:
    claude mcp add jupyter-macaw python /path/to/proxy_jupyter.py \
      -e JUPYTER_URL=... \
      -e JUPYTER_TOKEN=... \
      -e DOCUMENT_ID=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    PATH must include the venv bin: jupyter-mcp-server is not on the default PATH.
    Startup exceeds Claude Code's 30s default -- export MCP_TIMEOUT=120000 first.
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
}
for k in ("JUPYTER_URL", "JUPYTER_TOKEN", "DOCUMENT_ID"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="jupyter-proxy",
    command=["jupyter-mcp-server", "start"],
    env=upstream_env,
)
logging.info("jupyter-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
