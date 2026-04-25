---
name: alibabacloud-rds-instances-manage
description: 通过阿里云 RDS OpenAPI 与只读 SQL 工具管理 RDS 实例。在用户需要查询/管理阿里云 RDS、执行只读 SQL、查看实例/监控/慢日志/参数时使用。需先配置环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID、ALIBABA_CLOUD_ACCESS_KEY_SECRET，再通过命令行工具 alibabacloud-rds-instances-manage 列出并执行工具。
keywords: rds, aliyun, 阿里云, 数据库, openapi, sql, 实例, 监控, 慢日志
---

# Alibabacloud RDS Instances Manage

本 Skill 让大模型通过**命令行**调用阿里云 RDS OpenAPI 与只读 SQL 能力，用于查询/管理 RDS 实例。

## 何时使用

- 用户询问某地域的 RDS 实例列表、实例详情、监控、慢日志、参数、账号、数据库、白名单等
- 用户需要对实例执行只读 SQL（如 `explain`、`show create table`、`query_sql`）或查看大表/碎片
- 用户需要创建/修改实例、账号、参数、规格、重启、公网连接等 OpenAPI 操作

## 前置条件

1. **安装**：已安装本包（任选其一）
   - 从项目根目录：`uv pip install -e .` 或 `pip install -e .`
   - 或使用：`uvx alibabacloud-rds-openapi-mcp-server` 时，需在本地安装后使用 `alibabacloud-rds-instances-manage` 命令
2. **凭证**：必须提供阿里云 AK/SK 环境变量
   - `ALIBABA_CLOUD_ACCESS_KEY_ID`
   - `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
   - （可选）`ALIBABA_CLOUD_SECURITY_TOKEN`（STS）
   - （可选）`MCP_TOOLSETS`，默认 `rds`，可设为 `rds,rds_custom_read` 等

## 配置 entries（推荐）

在 OpenClaw、Claude Code 等平台中，建议在 skill 的 **entries** 里为本 skill 配置 `env`，把 `ALIBABA_CLOUD_ACCESS_KEY_ID` 和 `ALIBABA_CLOUD_ACCESS_KEY_SECRET` 写进去，这样运行时无需再单独配置环境变量，便于后续使用。

**OpenClaw**：在 `~/.openclaw/openclaw.json` 的 `skills.entries` 中为 `alibabacloud-rds-instances-manage` 增加一项，并写入 `env`：

```json
{
  "skills": {
    "entries": {
      "alibabacloud-rds-instances-manage": {
        "enabled": true,
        "env": {
          "ALIBABA_CLOUD_ACCESS_KEY_ID": "你的 AccessKey ID",
          "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "你的 AccessKey Secret"
        }
      }
    }
  }
}
```

可选：若使用 STS，可在同一 `env` 中增加 `ALIBABA_CLOUD_SECURITY_TOKEN`；若需指定工具集，可增加 `MCP_TOOLSETS`（如 `"rds,rds_custom_read"`）。

**Claude Code / 其他平台**：在对应技能的配置中找到「entries」或「环境变量」项，为 `alibabacloud-rds-instances-manage` 配置上述两个 env 即可。

## 标准流程

1. **列出可用工具**（若不确定工具名）  
   ```bash
   alibabacloud-rds-instances-manage list
   ```  
   输出为 JSON 数组，每项含 `name`、`description`。

2. **执行工具**  
   ```bash
   alibabacloud-rds-instances-manage run <工具名> '<JSON 参数>'
   ```  
   - 参数为 JSON 对象，键为工具文档中的参数名（如 `region_id`、`db_instance_id`）。  
   - 示例：查询杭州地域实例  
     ```bash
     alibabacloud-rds-instances-manage run describe_db_instances '{"region_id":"cn-hangzhou"}'
     ```  
   - 示例：查询实例详情  
     ```bash
     alibabacloud-rds-instances-manage run describe_db_instance_attribute '{"region_id":"cn-hangzhou","db_instance_id":"rm-xxxxx"}'
     ```  
   - 示例：执行只读 SQL  
     ```bash
     alibabacloud-rds-instances-manage run query_sql '{"region_id":"cn-hangzhou","db_instance_id":"rm-xxxxx","db_name":"mydb","sql":"SELECT 1"}'
     ```

3. **解析结果**  
   - 成功：标准输出为工具返回的 JSON 或文本的 JSON 包装。  
   - 失败：标准错误为 `{"error":"..."}`，退出码非 0。

## 常用工具速查

| 能力 | 工具名 | 典型参数 |
|------|--------|----------|
| 实例列表 | `describe_db_instances` | `region_id` |
| 实例详情 | `describe_db_instance_attribute` | `region_id`, `db_instance_id` |
| 可用区 | `describe_available_zones` | `region_id`, `engine`, 等 |
| 可用规格 | `describe_available_classes` | `region_id`, `zone_id`, `engine`, `engine_version`, 等 |
| 监控指标 | `describe_db_instance_performance` / `describe_monitor_metrics` | `region_id`, `db_instance_id`, 时间等 |
| 慢日志 | `describe_slow_log_records` | `region_id`, `db_instance_id`, 时间等 |
| 参数 | `describe_db_instance_parameters` | `region_id`, `db_instance_id` |
| 修改参数 | `modify_parameter` | `region_id`, `dbinstance_id`, `parameters` 等 |
| 只读 SQL | `query_sql` | `region_id`, `db_instance_id`, `db_name`, `sql` |
| 执行计划 | `explain_sql` | `region_id`, `db_instance_id`, `db_name`, `sql` |
| 建表语句 | `show_create_table` | `region_id`, `db_instance_id`, `db_name`, `table_name` |
| 当前时间 | `get_current_time` | 无参数 `{}` |

完整工具列表与参数见 [tools_reference.md](tools_reference.md)。

## 注意事项

- 所有写操作（创建/修改/重启等）会真实变更资源，调用前应确认参数与权限。  
- SQL 类工具（如 `query_sql`）仅支持只读；写操作请通过 OpenAPI 工具完成。  
- 时间参数建议使用 `get_current_time` 获取当前时间后再计算范围。