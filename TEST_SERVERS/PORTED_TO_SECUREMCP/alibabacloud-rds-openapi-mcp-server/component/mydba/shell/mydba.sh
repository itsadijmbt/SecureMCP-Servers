#!/usr/bin/env bash

set -e

usage() {
    echo "Usage: $0 [-h] [-s session]\n启动 mydba 智能体"
    echo "Options:"
    echo "  -h            展示帮助信息"
    echo "  -s session    指定会话 ID，默认 default"
    exit 1
}

session=""
while getopts ":hs:" opt; do
    case $opt in
        h) usage ;;
        s)
            session="$OPTARG"
            ;;
        \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
        :) echo "Option -$OPTARG requires an argument." >&2; usage ;;
    esac
done

HOME_DIR="/usr/local/mydba"
LOG_DIR="$HOME_DIR/logs"
AGENT_SCRIPT="main.py"
RAG_DIR="$HOME_DIR/mydba/mcp/rag"
RAG_SCRIPT="rag_server.py"
RAG_LOG="$LOG_DIR/rag.log"
RDS_DIR="$HOME_DIR/mydba/mcp/alibabacloud-rds-openapi-mcp-server/src/alibabacloud_rds_openapi_mcp_server"
RDS_SCRIPT="server.py"

if ! [ -e "${HOME_DIR}/main.py" ]; then
    echo "请确认 mydba 是否正确安装！"
    exit 1
fi

if ! [ -e "${RDS_DIR}/${RDS_SCRIPT}" ]; then
    echo "RDS 服务未安装，阿里云RDS管理功能将无法正常使用！"
    exit 1
fi

if ! [ -e "${RAG_DIR}/${RAG_SCRIPT}" ]; then
    echo "RAG 服务未安装，问询数据功能将无法正常使用！"
    exit 1
fi

if ! pgrep -f "${RAG_SCRIPT}" > /dev/null; then
    cd "$RAG_DIR"
    nohup uv run "${RAG_SCRIPT}" >> "$RAG_LOG" 2>&1 &
fi

cd "$HOME_DIR"
if [ -z "$session" ]; then
    uv run "${AGENT_SCRIPT}"
else
    echo "使用会话: $session"
    uv run "${AGENT_SCRIPT}" -s "$session"
fi
