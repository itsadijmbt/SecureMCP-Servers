# Chrome DevTools MCP — SecureMCPProxy

Wraps `npx -y chrome-devtools-mcp@latest --headless --isolated` — spawns the system Chrome. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js 20.19+, 22.12+ or 23+, and `npx` on `PATH`.
- Google Chrome installed (the package launches the system browser).

No credentials required.

## Setup

```bash
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_chrome_devtools.py
```

Register with Claude Code:

```bash
claude mcp add chrome-devtools-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  python /path/to/proxy_chrome_devtools.py'
```
