<p align="center">English | <a href="./README_CN.md">中文</a><br></p>

# Alibaba Cloud Database MyDBA Agent

## Features

1. **Supports management of Alibaba Cloud RDS**, including:
   - Instance information query
   - RDS Issue analysis
   - Purchase and modify RDS instance

2. **Query data for self-built databases**, assisting with data queries, statistics and analysis.

## Installation Guide

### Environment Preparation

1. **Install `uv`**:
   - Install `uv` via [Astral](https://docs.astral.sh/uv/getting-started/installation/)
   - Install `uv` via [GitHub README](https://github.com/astral-sh/uv#installation)
   - Download `uv` from [GitHub Release](https://github.com/astral-sh/uv/releases)

2. **Install Python**:
   - Use the following command to install Python:

   ```shell
   uv python install 3.12
   ```

3. **Apply for a LLM api key**:
   - Compatible with OpenAI client, support Qwen and Deepseek.

4. **Prepare an Alibaba Cloud account AK/SK**:
   - Ensure your account having the access permission with Alibaba Cloud RDS service (Policy Name: AliyunRDSFullAccess).

### Install Dependencies

Install dependency modules using `uv`:

```shell
export UV_DEFAULT_INDEX="https://mirrors.aliyun.com/pypi/simple" # optional
uv sync --inexact
```

### Service Initialization

1. **Prepare Configuration File**
   - Default path: `/usr/local/mydba/config_app.ini`
   - Configure parameters in the `model`, `app`, and `rag` sections:

   ```ini
   [common]
   debug = False
   config_database = sqlite:///usr/local/mydba/sqlite_app.db

   [log]
   dir = /usr/local/mydba/logs
   name = mydba
   file_level = INFO

   [model]
   api_key = sk-xxx                    ; LLM api key
   base_url = https://api.deepseek.com ; LLM api base url (example is the model address of Deepseek)
   model = deepseek-chat               ; LLM model name (example is the model name of Deepseek)
   max_tokens = 1000
   temperature = 1.0

   [app]
   refresh_interval = 60
   max_steps = 100
   security_key = xxxxxxxxxxxxxxxx     ; Key for encryption, 16-byte length, for internal data protection

   [rag]
   api_key = sk-xxx                    ; LLM api key
   base_url = https://dashscope.aliyuncs.com/compatible-mode/v1 ; LLM api base url (example is the model address of Qwen)
   embedding = text-embedding-v2       ; Embedding model name (Qwen supports embedding api calls)
   data_dir = /usr/local/mydba/vector_store
   ```

2. **Create Log Directory**
   - The log directory can be found in the configuration: [log].dir
   - Default path: /usr/local/mydba/logs

   ```shell
   mkdir /usr/local/mydba/logs
   ```

3. **Initialize Agent**
   - Execute the following command to initialize the Agent. Ensure you have correctly configured the **`config_app.ini`** file and replace `xxxxxx` with your Alibaba Cloud account AK/SK.

   ```shell
   uv --directory /path/to/mydba \
      run init_config.py \
          init-project \                                   # Initialize project
          --config_file /usr/local/mydba/config_app.ini \  # Configuration file path
          --reset \                                        # Clear existing configuration (optional)
          --rds_access_id xxxxxx \                         # Replace with your Alicloud account ID
          --rds_access_key xxxxxx                          # Replace with your Alicloud account secret
   ```

4. **Add Self-Built Database**
   - Execute the following command to add a self-built database. Ensure you have correctly configured the **`config_app.ini`** file and replace `--db_info` parameters with actual database connection details.

   ```shell
   uv --directory /path/to/mydba \
      run init_config.py \
          add-db \                                         # Add self-built database
          --config_file /usr/local/mydba/config_app.ini \  # Path to the configuration file
          --db_info 'mysql####127.0.0.1##3306##root##123456##utf8mb4##mybase' # Database connection info, pay attention to the escape of special characters
   ```

5. **Initialize RAG Tool**
   - Execute the following command to initialize the RAG tool. Ensure you have correctly configured the **`config_app.ini`** file and added the **self-built database**.

   ```shell
   uv --directory /path/to/mydba/mydba/mcp/rag \           # RAG working directory ./mydba/mcp/rag
      run rag_init.py \                                    # Run RAG initialization script
          init-config \                                    # Initialize configuration
          --config_file /usr/local/mydba/config_app.ini    # Path to the configuration file
   ```

### Service Startup

- Execute the start command: **`mydba`** (install agent via MyBase console, this command will register in the OS)

  ```shell
  mydba
  ```

- Or use the startup script: **`mydba.sh`** (built-in startup script, use directly if default installation path is unchanged)

  ```shell
  sh /path/to/mydba/shell/mydba.sh
  ```

- Or manually execute the following commands:

  ```shell
  # Set environment variables (optional, default: /usr/local/mydba/config_app.ini)
  export MYDBA_CONFIG_FILE=/path/to/mydba/config_app.ini
  # Start RAG Server
  nohup uv --directory /path/to/mydba/mydba/mcp/rag run rag_server.py >> /path/to/mydba/logs/rag.log 2>&1 &
  # Start MyDBA
  uv --directory /path/to/mydba run main.py
  ```

## Contact Us

- Welcome joining the DingTalk group for feedback, refer to the <a href="../../README.md">README.md</a> of RDS MCP for details.