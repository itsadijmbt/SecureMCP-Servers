"""
dingo-proxy -> SecureMCPProxy, served natively.

Prereq:
    git clone --depth 1 --branch v2.5.0 https://github.com/MigoXLab/dingo.git
    export DINGO_HOME="/path/to/dingo"
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_dingo.py

Claude Code:
    claude mcp add dingo-macaw python /path/to/proxy_dingo.py \
      -e DINGO_HOME=/path/to/dingo \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    For LLM based evaluations also set OPENAI_API_KEY (with OPENAI_BASE_URL and OPENAI_MODEL if needed).
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

dingo_home = os.environ.get("DINGO_HOME", "")
if not os.path.isfile(os.path.join(dingo_home, "mcp_server.py")):
    raise ValueError(
        "DINGO_HOME must point to a clone of https://github.com/MigoXLab/dingo "
        "(the folder that holds mcp_server.py). The dingo-python package on PyPI does not ship that file."
    )

upstream_env = {
    "PATH": os.environ["PATH"],
    "HOME": os.environ["HOME"],
    # The upstream serves stdio only when this is "true". Otherwise it starts an SSE server.
    "LOCAL_DEPLOYMENT_MODE": "true",
}
for k in (
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_BASE_URL",
    "ANTHROPIC_MODEL",
    "DEFAULT_OUTPUT_DIR",
):
    if os.environ.get(k):
        upstream_env[k] = os.environ[k]

proxy = SecureMCPProxy(
    app_name="dingo-proxy",
    # mcp_server.py is run directly: `dingo serve --transport stdio` prints a line to stdout before it
    # starts, and the MCP Python client stops on that line.
    command=[
        "uv",
        "run",
        "--no-project",
        "--with-requirements",
        os.path.join(dingo_home, "requirements", "runtime.txt"),
        "python",
        os.path.join(dingo_home, "mcp_server.py"),
    ],
    env=upstream_env,
)
logging.info("dingo-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
