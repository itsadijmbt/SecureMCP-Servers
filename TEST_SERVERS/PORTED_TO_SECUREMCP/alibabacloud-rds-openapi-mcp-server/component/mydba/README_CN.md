<p align="center"><a href="./README.md">English</a> | 中文<br></p>

# 阿里云数据库 MyDBA 智能体

## 特性

1. **支持对阿里云 RDS 进行管理**，包括：
   - 实例信息查询
   - 问题分析
   - 购买与变配
2. **对自建数据库进行问数**，帮助进行数据查询、统计与分析。

## 安装指南

### 环境准备

1. **安装 `uv`**：
   - [Astral](https://docs.astral.sh/uv/getting-started/installation/) 安装 `uv`
   - [GitHub README](https://github.com/astral-sh/uv#installation) 安装 `uv`
   - [GitHub Release](https://github.com/astral-sh/uv/releases) 下载 `uv`

2. **安装 Python**：
   - 使用以下命令安装 Python：

   ```shell
   uv python install 3.12
   ```

3. **申请大模型 Key**：
   - 兼容 OpenAI 客户端，支持通义千问、Deepseek。

4. **准备阿里云账号**：
   - 确保你有阿里云 RDS 服务访问权限(策略名:AliyunRDSFullAccess)的账号凭证。

### 安装依赖

使用 `uv` 安装依赖模块：

```shell
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple" 
uv sync --inexact
```

### 服务初始化

1. **准备配置文件**
   - 默认路径：`/usr/local/mydba/config_app.ini`
   - 配置好 `model`、`app` 和 `rag` 部分的参数项：

   ```ini
   [common]
   debug = False
   config_database = sqlite:///usr/local/mydba/sqlite_app.db

   [log]
   dir = /usr/local/mydba/logs
   name = mydba
   file_level = INFO

   [model]
   api_key = sk-xxx                    ; 大模型 key
   base_url = https://api.deepseek.com ; 大模型调用地址（这里是 Deepseek 模型地址）
   model = deepseek-chat               ; 模型名称（这里是 Deepseek 模型名称）
   max_tokens = 1000
   temperature = 1.0

   [app]
   refresh_interval = 60
   max_steps = 100
   security_key = xxxxxxxxxxxxxxxx     ; 加密 key，固定 16 字节长度，用于工程内部数据保护

   [rag]
   api_key = sk-xxx                    ; 大模型 key
   base_url = https://dashscope.aliyuncs.com/compatible-mode/v1 ; 大模型调用地址（这里是通义模型地址）
   embedding = text-embedding-v2       ; embedding 模型名称（通义千问支持 embedding 调用）
   data_dir = /usr/local/mydba/vector_store
   ```

2. **创建日志目录**
   - 日志目录可以查看配置: [log].dir
   - 默认路径：`/usr/local/mydba/logs`

   ```shell
   mkdir /usr/local/mydba/logs
   ```

3. **初始化 Agent**
   - 执行以下命令以初始化 Agent。请确保您已经正确配置了 **`config_app.ini`** 文件，并用您的阿里云账号替换 `xxxxxx`。

   ```shell
   uv --directory /path/to/mydba \
      run init_config.py \
          init-project \                                   # 初始化工程
          --config_file /usr/local/mydba/config_app.ini \  # 配置文件路径
          --reset \                                        # 清空已有配置（可选）
          --rds_access_id xxxxxx \                         # 替换为您的阿里云账号 ID
          --rds_access_key xxxxxx                          # 替换为您的阿里云账号密钥
   ```

4. **添加自建数据库**
   - 执行以下命令以添加自建数据库。请确保您已正确配置 **`config_app.ini`** 文件，并根据实际情况替换 `--db_info` 参数中的数据库连接信息。

   ```shell
   uv --directory /path/to/mydba \
      run init_config.py \
          add-db \                                         # 添加自建数据库
          --config_file /usr/local/mydba/config_app.ini \  # 配置文件路径
          --db_info 'mysql####127.0.0.1##3306##root##123456##utf8mb4##mybase' # 数据库连接信息，注意特殊字符的转义
   ```

5. **初始化 RAG 工具**
   - 执行以下命令以初始化 RAG 工具。请确保您已经正确配置了 **`config_app.ini`** 文件，并添加了**自建数据库**。

   ```shell
   uv --directory /path/to/mydba/mydba/mcp/rag \           # 这里是 RAG 的工作目录 ./mydba/mcp/rag
      run rag_init.py \                                    # 运行 RAG 初始化脚本
          init-config \                                    # 初始化配置
          --config_file /usr/local/mydba/config_app.ini    # 配置文件路径
   ```

### 服务启动

- 执行启动命令：**`mydba`** 通过控制台安装的智能体，会在操作系统注册此命令。

  ```shell
  mydba
  ```

- 或者执行启动脚本：**`mydba.sh`** 智能体自带的启动脚本，如果没有修改默认的安装路径，可直接使用。

  ```shell
  sh /path/to/mydba/shell/mydba.sh
  ```

- 或者手动执行如下命令：

  ```shell
  # 配置环境变量（可选，默认：/usr/local/mydba/config_app.ini）
  export MYDBA_CONFIG_FILE=/path/to/mydba/config_app.ini
  # 启动 RAG Server
  nohup uv --directory /path/to/mydba/mydba/mcp/rag run rag_server.py >> /path/to/mydba/logs/rag.log 2>&1 &
  # 启动 MyDBA
  uv --directory /path/to/mydba run main.py
  ```

## 联系我们

- 向上查看 RDS MCP 的 <a href="../../README_CN.md">README_CN.md</a>，加入钉钉群。
