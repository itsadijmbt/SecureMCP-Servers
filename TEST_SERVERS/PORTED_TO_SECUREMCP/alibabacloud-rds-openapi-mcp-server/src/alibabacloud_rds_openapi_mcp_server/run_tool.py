#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alibabacloud RDS Instances Manage CLI: 以命令行方式列出并执行 MCP 工具，供 OpenClaw、Claude Code 等通过 Skill 调用。

用法:
  alibabacloud-rds-instances-manage list [--toolsets rds]
  alibabacloud-rds-instances-manage run <tool_name> <json_args>

环境变量:
  ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET  (必需)
  ALIBABA_CLOUD_SECURITY_TOKEN  (可选, STS)
  MCP_TOOLSETS  (可选, 默认 rds，逗号分隔如 rds,rds_custom_read)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List

# 延迟导入 server，避免直接 import 时启动 MCP 服务；导入期间将 stdout 重定向到 stderr，保证 list 的 JSON 仅写入 stdout
def _get_mcp_and_tools():
    _old = sys.stdout
    sys.stdout = sys.stderr
    try:
        from alibabacloud_rds_openapi_mcp_server.server import mcp, _parse_groups_from_source
    finally:
        sys.stdout = _old
    source = os.getenv("MCP_TOOLSETS")
    enabled = _parse_groups_from_source(source)
    tool_map = {}
    for item in mcp._pending_registrations:
        if item.item_type.value != "tool":
            continue
        if item.group not in enabled:
            continue
        tool_map[item.func.__name__] = item.func
    return tool_map, enabled


def cmd_list(toolsets: str | None) -> None:
    tool_map, enabled = _get_mcp_and_tools()
    out = []
    for name, fn in sorted(tool_map.items()):
        doc = (fn.__doc__ or "").strip().split("\n")[0]
        out.append({"name": name, "description": doc})
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_run(tool_name: str, args_json: str) -> None:
    tool_map, _ = _get_mcp_and_tools()
    if tool_name not in tool_map:
        print(json.dumps({"error": f"Unknown tool: {tool_name}", "available": list(tool_map.keys())}), file=sys.stderr)
        sys.exit(1)
    try:
        args = json.loads(args_json) if args_json.strip() else {}
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
        sys.exit(1)
    fn = tool_map[tool_name]
    try:
        result = asyncio.run(fn(**args))
        if isinstance(result, (dict, list)):
            print(json.dumps(result, ensure_ascii=False, default=str))
        else:
            print(json.dumps({"result": str(result)}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alibabacloud RDS Instances Manage CLI: list or run tools for use by LLM skills."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    list_p = sub.add_parser("list", help="List available tools (JSON)")
    list_p.add_argument("--toolsets", default=os.getenv("MCP_TOOLSETS"), help="Comma-separated toolset names (default: rds)")
    run_p = sub.add_parser("run", help="Run a tool with JSON arguments")
    run_p.add_argument("tool_name", help="Tool name (e.g. describe_db_instances)")
    run_p.add_argument("args_json", nargs="?", default="{}", help='JSON object of arguments, e.g. \'{"region_id":"cn-hangzhou"}\'')

    args = parser.parse_args()
    if args.command == "list":
        if args.toolsets:
            os.environ["MCP_TOOLSETS"] = args.toolsets
        cmd_list(args.toolsets)
    elif args.command == "run":
        cmd_run(args.tool_name, args.args_json)


if __name__ == "__main__":
    main()