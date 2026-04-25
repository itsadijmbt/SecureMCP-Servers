---
name: alibabacloud-rds-copilot
description: 使用阿里云 RDS Copilot API,帮助用户完成 RDS 相关的智能问答、SQL 优化、实例运维和故障排查, 可直接调用 uv run ./scripts/call_rds_ai.py 脚本获取实时结果。
metadata: {"clawdbot":{"emoji":"🗄️","homepage":"https://www.aliyun.com/product/rds","requires":{"bins":["uv"],"env":["ALIBABA_CLOUD_ACCESS_KEY_ID","ALIBABA_CLOUD_ACCESS_KEY_SECRET"]},"os":["darwin","linux"]},"moltbot":{"emoji":"🗄️","homepage":"https://www.aliyun.com/product/rds","requires":{"bins":["uv"],"env":["ALIBABA_CLOUD_ACCESS_KEY_ID","ALIBABA_CLOUD_ACCESS_KEY_SECRET"]},"os":["darwin","linux"]}}
---

## Skill 概览

本 Skill 用于在对话中充当 **阿里云 RDS Copilot 的智能代理**:

- **理解用户的自然语言需求**(中文或英文),识别是否与 RDS Copilot 相关;
- **直接调用内置脚本** `scripts/call_rds_ai.py` 实时查询 RDS Copilot 并获取结果;
- 当获取到结果或用户粘贴错误信息时,**进一步解释、诊断并给出后续建议**。

**工作模式**:
- 使用 `scripts/call_rds_ai.py` 脚本直接获取 RDS Copilot 的实时响应

## 标准使用流程
1. **确认任务类型与参数**
    - 判断用户意图:SQL 编写/优化、SQL 诊断、实例参数调优、故障排查、性能分析、查询实例列表等。
    - 收集必要参数(如未指定则使用默认值):
        - `--region`:地域 ID(默认 `cn-hangzhou`)
        - `--language`:语言(默认 `zh-CN`)
        - `--timezone`:时区(默认 `Asia/Shanghai`)
        - `--custom-agent-id`:专属 Agent ID(可选)
        - `--conversation-id`:会话 ID,用于多轮对话(可选)

2. **构造查询并调用脚本**
     ```
   - 示例:
     ```bash
     # 基础查询
     uv run ./scripts/call_rds_ai.py "查询杭州地域的 RDS MySQL 实例列表"
     
     # 指定地域
     uv run  ./scripts/call_rds_ai.py "优化这条SQL" --region cn-beijing
     
     # 多轮对话
     uv run ./scripts/call_rds_ai.py "继续分析" --conversation-id "<上次返回的会话ID>"
     ```

3. **解析结果并后续处理**
    - 将 RDS Copilot 的响应用自然语言解释给用户;
    - 如返回包含 SQL 或操作步骤,评估风险并提醒:
        - 避免在生产环境直接执行高风险语句(如大表 `DELETE` / `UPDATE` / 结构变更);
        - 建议在测试环境验证或加上备份/条件限制。
    - 如需继续对话,记录 `conversation_id` 用于下一轮查询。

## 工具脚本使用说明
### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 查询内容(必需),使用 `-` 从标准输入读取 | - |
| `--region` / `--region-id` | 阿里云地域 ID | `cn-hangzhou` |
| `--language` / `--lang` | 语言 | `zh-CN` |
| `--timezone` / `--tz` | 时区 | `Asia/Shanghai` |
| `--custom-agent-id` | 专属 Agent ID | 无 |
| `--conversation-id` / `--conv-id` | 会话 ID(多轮对话) | 无 |
| `--endpoint` | API 端点 | `rdsai.aliyuncs.com` |
| `--no-stream` | 禁用流式输出 | False(默认启用流式) |


### 输出格式

脚本会将查询信息输出到 `stderr`,将 RDS Copilot 的回答输出到 `stdout`,便于分离日志和结果:

```
[查询] 查询杭州地域实例列表
[地域] cn-hangzhou | [语言] zh-CN
============================================================
[RDS Copilot 回答]
<实际回答内容>

[会话ID] conv-xxxx-xxxx-xxxx
```
