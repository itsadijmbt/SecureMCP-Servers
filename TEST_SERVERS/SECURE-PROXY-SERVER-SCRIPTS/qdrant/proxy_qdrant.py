"""
qdrant-proxy -> SecureMCPProxy, served natively.

Prereq:
    export QDRANT_URL="..."
    export QDRANT_API_KEY="..."
    export COLLECTION_NAME="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_qdrant.py

Claude Code:
    claude mcp add qdrant-macaw python /path/to/proxy_qdrant.py \
      -e QDRANT_URL=... \
      -e QDRANT_API_KEY=... \
      -e COLLECTION_NAME=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    For a local database on disk, set QDRANT_LOCAL_PATH instead of QDRANT_URL and QDRANT_API_KEY.
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
for k in (
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "QDRANT_LOCAL_PATH",
    "COLLECTION_NAME",
    "EMBEDDING_MODEL",
    "QDRANT_SEARCH_LIMIT",
    "QDRANT_READ_ONLY",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]
if "QDRANT_URL" not in upstream_env and "QDRANT_LOCAL_PATH" not in upstream_env:
    raise ValueError("Set QDRANT_URL (server) or QDRANT_LOCAL_PATH (local database)")

proxy = SecureMCPProxy(
    app_name="qdrant-proxy",
    # Python pinned: mcp-server-qdrant 0.8.1 needs pydantic-core 2.33.2, which has no Python 3.14 wheel.
    command=["uvx", "--python", "3.12", "mcp-server-qdrant"],
    env=upstream_env,
)
logging.info("qdrant-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
