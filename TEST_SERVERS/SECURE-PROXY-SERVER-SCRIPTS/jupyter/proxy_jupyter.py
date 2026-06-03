"""
Jupyter MCP (stdio spawn) -> SecureMCPProxy with bind_to_user.

This proxy SPAWNS jupyter-mcp-server as a stdio child process and
manages its lifecycle. You don't need to boot the upstream server
separately -- just run this script and it spawns + connects + tests.

The original jupyter-mcp-server stays untouched. All upstream
features (3 custom HTTP routes, dual-registry dispatcher in
jupyter_extension/handlers.py, hooks/OTel pipeline, 17 tools'
Pydantic Field metadata) are preserved -- the upstream still runs
as-is; this just sits in front of it.

Two tests, one file.

  Test 1 (active by default):  3 read-only smoke calls:
                                  list_kernels, list_files, list_notebooks
  Test 2 (bottom):              stdio MCP gateway for Gemini/Claude CLI.

Prerequisites:
    1. jupyter-mcp-server on PATH (editable install is fine):
         pip install -e ~/MACAW-MCP-STORE/TEST_SERVERS/COMMUNITY_PY_INTE_SECUREMCP/jupyter-mcp-server

    2. A reachable Jupyter server (JupyterLab / classic / JupyterHub).

Run:
    # These are read natively by jupyter-mcp-server's Click CLI
    # (envvar=RUNTIME_URL/RUNTIME_TOKEN in jupyter_mcp_server/CLI.py).
    # The subprocess inherits them; we don't re-pass as flags.
    export RUNTIME_URL="http://localhost:8888"
    export RUNTIME_TOKEN="<jupyter-server-token>"
    # Optional, otherwise document_* fall back to runtime_*:
    # export DOCUMENT_URL=...  DOCUMENT_TOKEN=...  DOCUMENT_ID=notebook.ipynb

    python TEST_SERVERS/SECURE-PROXY-SERVER-SCRIPTS/jupyter/proxy_jupyter.py
"""

import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

# SecureMCPProxy in spawn mode: command=[...].
# `jupyter-mcp-server start` defaults to --transport stdio and reads
# RUNTIME_URL/RUNTIME_TOKEN/DOCUMENT_* from the inherited env via Click,
# so no flag plumbing here.
proxy = SecureMCPProxy(
    app_name="jupyter-mcp-proxy",
    command=["jupyter-mcp-server", "start"],
)

# Client identity: registers as securemcp-client-jupyter-macaw-gateway.
# Static identity -- sufficient for testing; swap to RemoteIdentityProvider for prod.
client = Client("jupyter-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

# ============================================================================
# Test 1 -- smoke check (default). Three read-only tool calls.
#
# bound.call_tool routes via the client identity, so MACAW shows a
# two-node graph: client -> jupyter-mcp-proxy for each call. All three
# tools chosen are read-only and have NO kernel/notebook side effects.
# ============================================================================
tools = proxy.list_tools()
print(f"\nUpstream tools: {len(tools)}", file=sys.stderr)
for t in tools:
    print(f"  - {t['name']}: {t.get('description','')[:80]}", file=sys.stderr)

print("\n" + "=" * 60, file=sys.stderr)
print("Test 1a: list_kernels (no args; expects kernel list)", file=sys.stderr)
print("=" * 60, file=sys.stderr)
try:
    r1 = bound.call_tool("list_kernels", {})
    print(f"  result: {str(r1)[:280]}", file=sys.stderr)
    print("  PASS -- handler reachable; upstream returned", file=sys.stderr)
except Exception as e:
    print(f"  Got error: {str(e)[:240]}", file=sys.stderr)
    print("  Inspect: list_kernels failed (upstream / auth / network)", file=sys.stderr)

print("\n" + "=" * 60, file=sys.stderr)
print("Test 1b: list_files (root listing, depth=1, limit=10)", file=sys.stderr)
print("=" * 60, file=sys.stderr)
try:
    r2 = bound.call_tool(
        "list_files",
        {"path": "", "max_depth": 1, "limit": 10},
    )
    print(f"  result: {str(r2)[:280]}", file=sys.stderr)
    print("  PASS -- file enumeration reached upstream", file=sys.stderr)
except Exception as e:
    print(f"  Got error: {str(e)[:240]}", file=sys.stderr)
    print("  Inspect: list_files failed (upstream / auth / path)", file=sys.stderr)

print("\n" + "=" * 60, file=sys.stderr)
print("Test 1c: list_notebooks (lists managed notebooks)", file=sys.stderr)
print("=" * 60, file=sys.stderr)
try:
    r3 = bound.call_tool("list_notebooks", {})
    print(f"  result: {str(r3)[:280]}", file=sys.stderr)
    print("  PASS -- notebook manager reachable through proxy", file=sys.stderr)
except Exception as e:
    print(f"  Got error: {str(e)[:240]}", file=sys.stderr)
    print("  Inspect: list_notebooks failed (upstream / auth)", file=sys.stderr)

print("\n" + "=" * 60, file=sys.stderr)
print("Test 1 SUMMARY", file=sys.stderr)
print("=" * 60, file=sys.stderr)
print(
    "  - Three read-only tools exercised through the proxy.\n"
    "  - Each call traverses: client -> Local Agent (PEP + audit) ->\n"
    "    SecureMCPProxy -> upstream jupyter-mcp-server.\n"
    "  - MACAW Console activity graph should show two nodes\n"
    "    (jupyter-macaw-gateway -> jupyter-mcp-proxy) and an audit entry\n"
    "    per call.",
    file=sys.stderr,
)

