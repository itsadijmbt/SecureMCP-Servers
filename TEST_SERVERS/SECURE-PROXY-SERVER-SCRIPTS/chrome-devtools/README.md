# Chrome DevTools MCP — SecureMCPProxy

Wraps `npx -y chrome-devtools-mcp@latest --headless --isolated` — spawns the system Chrome. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.
- Google Chrome installed — the package launches the system browser, it does not bundle one.

No credentials required.

## Setup

```bash
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_chrome_devtools.py            # stdio
python proxy_chrome_devtools.py http 8080  # http
```

Register with Claude Code:

```bash
claude mcp add chrome-devtools-macaw python /path/to/proxy_chrome_devtools.py \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
