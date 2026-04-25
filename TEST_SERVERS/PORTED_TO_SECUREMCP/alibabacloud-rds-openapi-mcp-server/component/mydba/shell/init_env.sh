#!/usr/bin/env bash

set -e

if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "无法确定操作系统类型"
    exit 1
fi

# check distro
if [ -f /etc/os-release ]; then
  . /etc/os-release
  DISTRO_VERSION=$(echo "$VERSION_ID" | cut -d '.' -f 1)
else
  echo "Unable to determine the distribution. Please check /etc/os-release."
  exit 1
fi

case $OS in
    ubuntu|debian)
        ;;
    alinux)
        ;;
    centos|rhel)
        echo "CentOS $DISTRO_VERSION"
        if [[ "$DISTRO_VERSION" -lt 8 && "$DISTRO_VERSION" -ge 7 ]]; then
            sed -i \
				-e 's/faiss-cpu>=1.11.0/faiss-cpu==1.9.0.post1/'  /usr/local/mydba/pyproject.toml
			echo "修改pyproject.toml完成"
        fi
        ;;
    *)
        echo "不支持的操作系统: $OS"
        exit 1
        ;;
esac

HOME_DIR="/usr/local/mydba"

# starting
echo "执行初始化环境命令"

# mkdir logs
if ! [ -e "/usr/local/mydba/logs" ]; then
  mkdir /usr/local/mydba/logs
fi

# install 
echo "安装uv"
if ! command -v uv &> /dev/null; then
    /usr/local/mydba/shell/uv-installer.sh
    ln -s /root/.local/bin/uv  /usr/bin/uv
else
    echo "uv 已安装"
fi

# install python3.12
export UV_PYTHON_INSTALL_MIRROR="https://ghproxy.cn/https://github.com/indygreg/python-build-standalone/releases/download"
uv python install 3.12

# init agent env
echo "设置镜像源"
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple" 

echo "拉取Agent依赖"
cd "$HOME_DIR"
uv sync --inexact

# init mcp env
echo "拉取RDS MCP依赖"
cd mydba/mcp/alibabacloud-rds-openapi-mcp-server
uv sync --inexact
