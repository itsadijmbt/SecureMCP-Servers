# RDS 相关 Skills 使用说明

本仓库提供多类 Skill，均可用于 Claude、OpenClaw、Claude Code 等以「技能」形式接入：

## 核心 RDS Skills

1. **alibabacloud-rds-copilot**：调用阿里云 RDS AI 助手 API，完成智能问答、SQL 优化、故障排查等。
2. **alibabacloud-rds-instances-manage**：通过命令行直接调用本项目的 **RDS OpenAPI 工具** 与 **只读 SQL 工具**，管理实例、查监控/慢日志/参数、执行只读 SQL 等。

## 其他 Skills

3. **mcporter**：使用 mcporter CLI 直接列出、配置、认证和调用 MCP 服务器/工具（HTTP 或 stdio），包括临时服务器、配置编辑和 CLI/类型生成。
4. **cli-anything**：使用 CLI-Anything 方法论为现有软件/代码库生成或改进适用于代理的 CLI。将 GUI 应用、桌面工具、仓库、SDK 或 Web/API 表面转换为适用于代理的结构化 CLI。
5. **data-analyst**：数据可视化、报告生成、SQL 查询和电子表格自动化。将您的 AI 代理转变为精通数据的分析师，将原始数据转化为可操作的洞察。
6. **arxiv-watcher**：搜索和总结 ArXiv 论文。当您需要最新研究、ArXiv 上的特定主题或 AI 论文的每日摘要时使用。
7. **duckdb-cli-ai-skills**：DuckDB CLI 专家，用于 SQL 分析、数据处理和文件转换。用于 SQL 查询、CSV/Parquet/JSON 分析、数据库查询或数据转换。
8. **self-improving-agent**：捕获学习、错误和更正以实现持续改进。当命令失败、用户纠正您或发现更好的方法时使用。

---

## 一、RDS Copilot Claude Skill（RDS AI 助手）

阿里云 [RDS AI助手](https://help.aliyun.com/zh/rds/apsaradb-rds-for-mysql/rds-copilot-overview) 的 Claude Skill，用于在 Claude 对话中直接调用 RDS AI 助手能力，完成 SQL 优化、实例运维、故障排查等任务。

<img src="../assets/claude_skill.png" alt="Claude Skill 使用示例" width="800"/>


## 环境要求

### 开通 RDS AI助手专业版
- [阿里云 RDS AI助手](https://rdsnext.console.aliyun.com/rdsCopilotProfessional/cn-hangzhou) 已经开通专业版


### Python 版本

- **Python 3.7+**（推荐 Python 3.8 或更高版本）

验证 Python 版本：
```bash
python3 --version
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/aliyun/alibabacloud-rds-openapi-mcp-server
cd alibabacloud-rds-openapi-mcp-server/skill
```

### 2. 安装依赖

安装uv：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. 配置环境变量

设置阿里云访问凭证（必需）：

**macOS / Linux：**
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
```

**Windows (PowerShell)：**
```powershell
$env:ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
$env:ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
```

**永久配置（推荐）：**

将上述命令添加到你的 shell 配置文件中：
- Bash: `~/.bashrc` 或 `~/.bash_profile`
- Zsh: `~/.zshrc`
- Windows: 系统环境变量设置

### 4. 部署 Skill 到 Claude

将 Skill 文件复制到 Claude 的 skills 目录：

**方法一：直接使用本仓库结构**

如果你使用的是 Claude Desktop 或支持自定义 skills 的环境，本仓库已经包含正确的目录结构 `alibabacloud-rds-copilot/`，可以直接使用。

**方法二：复制到用户级 skills 目录**

```bash
# macOS / Linux
mkdir -p ~/.claude/skills/
cp -r alibabacloud-rds-copilot ~/.claude/skills/

# Windows (PowerShell)
New-Item -ItemType Directory -Path "$env:USERPROFILE\.claude\skills\" -Force
Copy-Item -Recurse ".claude\skills\aliyun-rds-copilot" "$env:USERPROFILE\.claude\skills\"
```

**方法三：创建符号链接（推荐开发环境）**

```bash
# macOS / Linux
mkdir -p ~/.claude/skills/
ln -s "$(pwd)/alibabacloud-rds-copilot" ~/alibabacloud-rds-copilot

# Windows (需管理员权限)
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\aliyun-rds-copilot" -Target "$(Get-Location)\.claude\skills\aliyun-rds-copilot"
```

### 5. 验证安装

运行claude，选择alibabacloud-rds-copilot skill：

```bash
claude
```
```bash
/alibabacloud-rds-copilot 我在杭州有多少实例？
```


预期输出：
```
[查询] 查询杭州地域的 RDS 实例列表
[地域] cn-hangzhou | [语言] zh-CN
============================================================
[RDS Copilot 回答]
<RDS Copilot 的实际回答内容>

[会话ID] conv-xxxx-xxxx-xxxx
```

## 使用说明

### 基础用法

在 Claude 对话中，直接提问 RDS 相关问题：

```
你：查询杭州地域有哪些 MySQL 实例？
Claude：[调用 RDS Copilot 并返回结果]

你：针对rm-xxx实例帮我分析和优化这条 SQL：SELECT * FROM users WHERE status=1 ORDER BY created_at
Claude：[调用 RDS Copilot 获取 SQL 优化建议]
```

## 常见问题

### 1. 提示找不到模块 `alibabacloud_rdsai20250507`

**原因**：未安装依赖包或使用了错误的 Python 环境。

**解决方法**：
```bash
# 使用 pip3 确保安装到 Python 3 环境
pip3 install -r alibabacloud-rds-copilot/requirements.txt

# 验证安装
pip3 list | grep alibabacloud
```

### 2. 提示环境变量未设置

**错误信息**：
```
未找到阿里云访问凭证。请设置环境变量:
  ALIBABA_CLOUD_ACCESS_KEY_ID
  ALIBABA_CLOUD_ACCESS_KEY_SECRET
```

**解决方法**：
按照"配置环境变量"章节设置 AccessKey 和 Secret。

### 3. Claude 未识别到 Skill

**原因**：Skill 文件未正确部署到 Claude skills 目录。

**解决方法**：
- 检查 `alibabacloud-rds-copilot/SKILL.md` 是否存在
- 确认 Skill 目录结构完整
- 重启 Claude 应用

### 5. 使用 `python` 命令报错

**原因**：系统中 `python` 命令指向 Python 2 或未配置。

**解决方法**：
统一使用 `python3` 命令：
```bash
python3 alibabacloud-rds-copilot/scripts/call_rds_ai.py "your query"
```

---

## 二、Alibabacloud RDS Instances Manage（OpenAPI + SQL 工具命令行）

**alibabacloud-rds-instances-manage** 将本项目的 MCP 工具以「脚本/命令行」形式暴露，便于接入 **OpenClaw、Claude Code** 等：大模型通过执行 `alibabacloud-rds-instances-manage list` / `alibabacloud-rds-instances-manage run <工具名> '<JSON 参数>'` 来调用 RDS OpenAPI 与只读 SQL 能力，从而管理 RDS 实例。

### 能力概览

- **OpenAPI 工具**：查询实例列表/详情、可用区/规格、监控、慢日志、参数、账号、数据库、白名单；创建/修改实例与账号、改参数/规格、重启、公网连接等。
- **SQL 工具**：只读执行 `query_sql`、`explain_sql`、`show_create_table`、`show_engine_innodb_status`、`show_largest_table`、`show_largest_table_fragment` 等。

### 安装与配置

1. **安装本包**（任选其一）  
   - 在仓库根目录：`uv pip install -e .` 或 `pip install -e .`  
   - 安装后可使用命令：`alibabacloud-rds-instances-manage`

2. **环境变量**（与 MCP 服务相同）  
   - `ALIBABA_CLOUD_ACCESS_KEY_ID`、`ALIBABA_CLOUD_ACCESS_KEY_SECRET`（必填）  
   - 可选：`ALIBABA_CLOUD_SECURITY_TOKEN`、`MCP_TOOLSETS`（默认 `rds`）

### 命令行用法

```bash
# 列出当前启用的工具（JSON）
alibabacloud-rds-instances-manage list

# 执行工具，参数为 JSON 字符串
alibabacloud-rds-instances-manage run describe_db_instances '{"region_id":"cn-hangzhou"}'
alibabacloud-rds-instances-manage run describe_db_instance_attribute '{"region_id":"cn-hangzhou","db_instance_id":"rm-xxxxx"}'
alibabacloud-rds-instances-manage run get_current_time '{}'
```

未安装到环境时，可从仓库根目录用模块方式执行：

```bash
uv run python -m alibabacloud_rds_openapi_mcp_server.run_tool list
uv run python -m alibabacloud_rds_openapi_mcp_server.run_tool run describe_db_instances '{"region_id":"cn-hangzhou"}'
```

### 接入 OpenClaw / Claude Code

1. **部署 Skill 目录**  
   将 `skill/alibabacloud-rds-instances-manage/` 复制或链接到对应平台的 skills 目录，例如：  
   - OpenClaw：`~/.openclaw/workspace/skills/alibabacloud-rds-instances-manage/`  
   - Claude Code：`~/.claude/skills/alibabacloud-rds-instances-manage/` 或项目内 `.claude/skills/alibabacloud-rds-instances-manage/`

2. **配置 entries 并写入 env（推荐）**  
   本 skill 需要环境变量 `ALIBABA_CLOUD_ACCESS_KEY_ID` 和 `ALIBABA_CLOUD_ACCESS_KEY_SECRET`。建议在平台的 **entries** 里为 `alibabacloud-rds-instances-manage` 配置 `env`，把这两个变量写进去，后续使用无需再单独配置。  
   - **OpenClaw**：编辑 `~/.openclaw/openclaw.json`，在 `skills.entries` 中增加：
     ```json
     "alibabacloud-rds-instances-manage": {
       "enabled": true,
       "env": {
         "ALIBABA_CLOUD_ACCESS_KEY_ID": "你的 AccessKey ID",
         "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "你的 AccessKey Secret"
       }
     }
     ```
   - 可选：同一 `env` 中可加 `ALIBABA_CLOUD_SECURITY_TOKEN`（STS）、`MCP_TOOLSETS`（如 `"rds,rds_custom_read"`）。  
   - **Claude Code 等**：在对应技能的「entries」或「环境变量」配置中为 `alibabacloud-rds-instances-manage` 设置上述两个 env 即可。

3. **确保环境中可执行**  
   安装本包后，保证在终端能直接运行 `alibabacloud-rds-instances-manage`。大模型会按 SKILL.md 中的说明调用 `alibabacloud-rds-instances-manage list` 与 `alibabacloud-rds-instances-manage run <name> '<json>'`。

4. **Skill 内容说明**  
   - `skill/alibabacloud-rds-instances-manage/SKILL.md`：技能名称、描述、何时使用、标准流程、**配置 entries** 与常用工具速查。  
   - `skill/alibabacloud-rds-instances-manage/tools_reference.md`：工具名与参数参考。  
   - `skill/alibabacloud-rds-instances-manage/skill.yaml`：供 OpenClaw/ClawHub 使用的元数据（可选）。