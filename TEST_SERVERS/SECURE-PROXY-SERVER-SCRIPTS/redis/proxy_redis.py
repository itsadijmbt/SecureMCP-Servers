"""
redis-proxy -> SecureMCPProxy, served natively.

Prereq:
    export REDIS_HOST="..."
    export REDIS_PORT="..."
    export REDIS_USERNAME="..."
    export REDIS_PWD="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_redis.py

Claude Code:
    claude mcp add redis-macaw python /path/to/proxy_redis.py \
      -e REDIS_HOST=... \
      -e REDIS_PORT=... \
      -e REDIS_USERNAME=... \
      -e REDIS_PWD=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
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
    "REDIS_HOST",
    "REDIS_PORT",
    "REDIS_DB",
    "REDIS_USERNAME",
    "REDIS_PWD",
    "REDIS_SSL",
    "REDIS_CLUSTER_MODE",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="redis-proxy",
    command=["uvx", "--from", "redis-mcp-server@latest", "redis-mcp-server"],
    env=upstream_env,
)
logging.info("redis-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
