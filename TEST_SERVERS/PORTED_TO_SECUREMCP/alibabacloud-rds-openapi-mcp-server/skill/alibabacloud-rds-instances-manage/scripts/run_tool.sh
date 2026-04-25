#!/usr/bin/env bash
# 从仓库根目录执行: uv run skill/alibabacloud-rds-instances-manage/scripts/run_tool.sh [list|run <tool_name> <json>]
# 或安装包后直接使用: alibabacloud-rds-instances-manage list / alibabacloud-rds-instances-manage run <name> '<json>'
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$REPO_ROOT"
exec uv run python -m alibabacloud_rds_openapi_mcp_server.run_tool "$@"
