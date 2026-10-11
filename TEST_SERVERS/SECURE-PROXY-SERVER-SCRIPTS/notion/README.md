# Notion MCP — SecureMCPProxy

Wraps `npx -y @notionhq/notion-mcp-server` over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- Node.js and `npx` on `PATH`.

Environment variables:

- `NOTION_TOKEN`  — required.

## Setup

```bash
export NOTION_TOKEN="..."
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_notion.py
```

Register with Claude Code:

```bash
claude mcp add notion-macaw python /path/to/proxy_notion.py \
  -e NOTION_TOKEN=... \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```
