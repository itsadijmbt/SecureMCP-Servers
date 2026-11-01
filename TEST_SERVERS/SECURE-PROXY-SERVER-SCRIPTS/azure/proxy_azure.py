"""
azure-proxy -> SecureMCPProxy, served natively.

Prereq:
    export AZURE_CLIENT_ID="..."
    export AZURE_CLIENT_SECRET="..."
    export AZURE_SUBSCRIPTION_ID="..."
    export AZURE_TENANT_ID="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_azure.py

Claude Code:
    claude mcp add azure-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
      export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
      export AZURE_TENANT_ID="..." && \
      export AZURE_CLIENT_ID="..." && \
      export AZURE_CLIENT_SECRET="..." && \
      export AZURE_SUBSCRIPTION_ID="..." && \
      python /path/to/proxy_azure.py'
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
for k in ("AZURE_TENANT_ID", "AZURE_CLIENT_ID", "AZURE_CLIENT_SECRET",
          "AZURE_SUBSCRIPTION_ID"):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="azure-proxy",
    command=["npx", "-y", "@azure/mcp@4.0.0-beta.3", "server", "start", "--mode", "all", "--read-only"],
    env=upstream_env,
)
logging.info("azure-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
