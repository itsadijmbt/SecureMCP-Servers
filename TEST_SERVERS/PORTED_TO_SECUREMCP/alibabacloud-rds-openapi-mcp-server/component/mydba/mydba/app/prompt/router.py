# -*- coding: utf-8 -*-
from functools import reduce
from typing import List
from mydba.app.config.agent import AgentInfo

pack_intent_info = lambda l: "\n".join([INTENT_INFO.format(id=i+1, name=agent.intent, description=agent.intent_description) for i, agent in enumerate(l, start=0)])
pack_intent_name = lambda l: "、".join([agent.intent for agent in l])
pack_default_intent = lambda l: next(iter([agent.intent for agent in filter(lambda agent: agent.is_default, l)]), None)

def pack_condition(agents: List[AgentInfo]) -> str:
    conditions = map(lambda agent: agent.prompts.get('condition'), filter(lambda agent: agent.prompts and agent.prompts.get('condition'), agents))
    reduce_conditions = reduce(lambda x, y: x + y, conditions, list())
    return "\n".join([CONDITION_INFO.format(condition=condition) for condition in reduce_conditions])

def pack_shot(agents: List[AgentInfo]) -> str:
    id = 0
    shot_infos = []
    for agent in agents:
        if not agent.prompts or not agent.prompts.get('shot'):
            continue
        for shot in agent.prompts.get('shot'):
            id += 1
            shot_info = SHOT_INFO.format(id=id, shot=shot, intent=agent.intent)
            shot_infos.append(shot_info)
    if not shot_infos:
        return "暂无示例"
    return "\n".join(shot_infos)

INTENT_INFO = """  {id}. **{name}**：{description}。"""
CONDITION_INFO = """- {condition}"""
SHOT_INFO = """###示例{id}\n{{\n  "问题描述": "{shot}",\n  "意图": "{intent}"\n}}"""

SYSTEM_PROMPT = """# 角色

您是专业的阿里巴巴云数据库运营助手，专注于为客户提供高效的数据库技术支持和解决方案。您的目标是通过清晰的问题理解，识别出用户意图。

## 技能

### 技能 1：分析问题
- 深入分析用户问题，结合问题上下文，识别核心需求及相关的潜在诉求。
- 对问题的分析要基于事实和逻辑，不得主观臆断。

### 技能 2：识别意图
- 根据用户问题，识别出其意图。
- 意图种类是固定的，有：
{intent_infos}
- 对于无法识别的意图，返回“{default_intent}”。
- 意图识别必须基于事实和逻辑，避免主观臆断。
- 意图识别需要充分结合上下文信息进行，识别结果需要考虑到之前的对话历史，根据历史对话意图及当前问题汇总得出，若用户输入中有明确的意图切换，则优先使用用户输入的意图。

## 约束条件
- **意图精确性**：始终返回列表里的意图，禁止返回其它内容。这里再重申一次有效的意图列表，有 {intent_names}。
- **专业聚焦**：仅讨论与数据库相关的技术话题。
- **安全意识**：确保没有任何操作会对客户的数据库产生负面影响。
{conditions}

## 示例

{shots}

"""

USER_PROMPT = """
问题：
<start_question>
{query}
<end_question>
请根据问题内容，识别出意图。
请注意，必须基于事实和逻辑进行识别，禁止主观臆断，只返回具体的意图种类，不输出分析过程。
"""
