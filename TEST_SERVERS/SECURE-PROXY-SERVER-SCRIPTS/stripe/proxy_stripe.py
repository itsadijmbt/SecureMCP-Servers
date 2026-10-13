"""
stripe-proxy -> SecureMCPProxy, served natively.

Prereq:
    export STRIPE_SECRET_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_stripe.py

Claude Code:
    claude mcp add stripe-macaw python /path/to/proxy_stripe.py \
      -e STRIPE_SECRET_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("STRIPE_SECRET_KEY")
if not api_key:
    raise ValueError("STRIPE_SECRET_KEY is not set (use a Restricted API Key: rk_test_... or rk_live_...)")


proxy = SecureMCPProxy(
    app_name="stripe-proxy",
    command=["npx", "-y", "@stripe/mcp"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "STRIPE_SECRET_KEY": api_key,
    },
)
logging.info("stripe-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
