# Dingo MCP — SecureMCPProxy

Wraps `mcp_server.py` from a clone of `MigoXLab/dingo` (run with `uv run`) over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uv` on `PATH`.
- A clone of Dingo (the proxy runs its `mcp_server.py`):
  `git clone --depth 1 --branch v2.5.0 https://github.com/MigoXLab/dingo.git`

Environment variables:

- `DINGO_HOME`  — required.
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `ANTHROPIC_MODEL`
- `DEFAULT_OUTPUT_DIR`

`DINGO_HOME` is the cloned folder (the one that holds `mcp_server.py`). The model keys are only needed for LLM based evaluations. `DEFAULT_OUTPUT_DIR` is where evaluation results are written. The default is a `dingo_output_...` folder next to the input file.

## Setup

```bash
export DINGO_HOME="/path/to/dingo"
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_dingo.py
```

Register with Claude Code:

```bash
claude mcp add dingo-macaw -- bash -lc 'source /path/to/.venv/bin/activate && \
  export MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12 && \
  export DINGO_HOME="/path/to/dingo" && \
  python /path/to/proxy_dingo.py'
```
