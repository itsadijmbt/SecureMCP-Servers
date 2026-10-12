# Dingo MCP — SecureMCPProxy

Wraps `mcp_server.py` from a clone of `MigoXLab/dingo` (run with `uv run`) over stdio. MACAW policy is enforced at the proxy before any call reaches the upstream.

## What it needs

- MACAW LocalAgent running, `MACAW_HOME` set.
- `uv` on `PATH`.
- A clone of Dingo. The `dingo-python` package on PyPI does not ship `mcp_server.py`:
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

`DINGO_HOME` is the cloned folder (the one that holds `mcp_server.py`). The model keys are only needed for LLM based evaluations. A rule based `run_quick_evaluation` ran without any key. `DEFAULT_OUTPUT_DIR` is where evaluation results are written; without it they go into a `dingo_output_...` folder next to the input file.

## Setup

```bash
export DINGO_HOME="/path/to/dingo"
export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

python proxy_dingo.py
```

Register with Claude Code:

```bash
claude mcp add dingo-macaw python /path/to/proxy_dingo.py \
  -e DINGO_HOME=/path/to/dingo \
  -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
```

## Policy

`Policy/server_policy_v0.1.0.json` is for the app `dingo-proxy`, the same name as `app_name` in `proxy_dingo.py`. Tools are named `tool:dingo-proxy/<tool>`.

- Allowed: 5 tools (`list_dingo_components`, `get_rule_details`, `get_llm_details`, `get_prompt_details`, `run_quick_evaluation`).
- Denied: 1 tool (`run_dingo_evaluation`).
- Limits: 7 parameters on the 5 allowed tools. An `input_path` that contains `..` is refused.

## Checked

- With Dingo v2.5.0: 6 tools, the same names, descriptions and input schemas as the upstream serves on its own.
- `list_dingo_components`, `get_rule_details`, `get_llm_details`, `get_prompt_details` and a rule based `run_quick_evaluation` returned real data. LLM based evaluations were not run (no model key).
- `dingo serve --transport stdio` is not used. It prints a line to stdout before it starts, and the MCP Python client stops on that line. The proxy runs `mcp_server.py` with `LOCAL_DEPLOYMENT_MODE=true`, which is the upstream's own stdio switch.
