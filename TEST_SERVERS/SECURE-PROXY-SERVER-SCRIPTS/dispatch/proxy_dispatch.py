"""
dispatch-proxy -> SecureMCPProxy, served natively.

Prereq:
    export DISPATCH_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_dispatch.py

Claude Code:
    claude mcp add dispatch-macaw python /path/to/proxy_dispatch.py \
      -e DISPATCH_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    DISPATCH_API_KEY is a Dispatch API key (it starts with dak_). Without it the upstream uses the
    session saved by `dispatch login`.
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
    "DISPATCH_API_KEY",
    "DISPATCH_DEPLOY_URL",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="dispatch-proxy",
    # Installed from the Datadog repository. The PyPI package named "dispatch-cli" is a different project.
    command=[
        "uvx",
        "--from",
        "git+https://github.com/datadog-labs/dispatch_agents_cli.git@v0.11.7",
        "dispatch",
        "mcp",
        "serve",
        "operator",
    ],
    env=upstream_env,
)
logging.info("dispatch-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
