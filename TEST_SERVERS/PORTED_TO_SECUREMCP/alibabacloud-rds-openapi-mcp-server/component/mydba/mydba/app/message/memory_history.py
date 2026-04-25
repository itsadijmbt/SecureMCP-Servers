# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
from mydba.app.config.settings import settings
from mydba.app.database.base_database import BaseDatabases
from mydba.app.message.message import Function, ToolCall

class MemoryInfo(BaseModel):
    time: str = Field(..., description="记录时间")
    request_id: Optional[str] = Field(None, description="请求标识")
    user_name: str = Field(..., description="用户标识")
    session: str = Field(..., description="会话标识")
    agent_name: str = Field(..., description="agent 标识")
    system_content: Optional[str] = Field(None, description="系统指令内容")
    user_content: Optional[str] = Field(None, description="用户查询内容")
    assistant_content: Optional[str] = Field(None, description="大模型返回的内容")
    assistant_tool_calls: Optional[List[ToolCall]] = Field(None, description="大模型返回的工具调用列表")
    tool_contents: Optional[List[Dict[str, str]]] = Field(None, description="工具调用返回的内容列表，内容格式为 {'tool_call_id': 'xxx', 'content': 'xxx'}")

async def get_memory(user_name: str, session: str, agent_name: str, start_time: Optional[datetime] = None, 
                     request_id: Optional[str] = None, limit: int=10) -> List[MemoryInfo]:
    """
    获取用户的 agent memory
    Args:
        user_name (str): 用户标识。
        session (str): 会话标识。
        agent_name (str): agent 标识。
        start_time (datetime): 起始时间。
        request_id (str): 请求标识。
        limit (int): 限制返回的记录数。
    Returns:
        list: 用户的 memory 列表（按时间倒序）。
    """
    # 读取 db 中的 agent memory
    params = [user_name, session, agent_name]
    sql = "SELECT * FROM memory WHERE user_name=? AND session=? AND agent_name=?"
    if start_time:
        params.append(start_time.strftime("%Y-%m-%d %H:%M:%S"))
        sql += " AND time>=?"
    if request_id:
        params.append(request_id)
        sql += " AND request_id=?"
    sql += f" ORDER BY id DESC LIMIT {limit}"
    db = BaseDatabases.create_database(uri=settings.CONFIG_DATABASE)
    try:
        rows = await db.query(sql, params)
        memories = []
        for row in rows:
            assistant_tool_calls = None
            if row['assistant_tool_calls']:
                assistant_tool_calls = []
                tool_call_list = json.loads(row['assistant_tool_calls'])
                for item in tool_call_list:
                    function = Function(name=item['function']['name'], arguments=item['function']['arguments'])
                    tool_call = ToolCall(id=item['id'], type=item['type'], function=function)
                    assistant_tool_calls.append(tool_call)
            tool_contents = json.loads(row['tool_contents']) if row['tool_contents'] else None
            memory = MemoryInfo(
                time = row['time'],
                request_id = row['request_id'],
                user_name = row['user_name'],
                session = row['session'],
                agent_name = row['agent_name'],
                system_content = row['system_content'],
                user_content = row['user_content'],
                assistant_content = row['assistant_content'],
                assistant_tool_calls = assistant_tool_calls,
                tool_contents = tool_contents
            )
            memories.append(memory)
    finally:
        await db.clean()
    return memories

async def save_memory(memory_info: MemoryInfo) -> None:
    """
    保存用户的 agent memory
    Args:
        memory_info (MemoryInfo): 用户的 agent memory 信息。
    """
    sql = "INSERT INTO memory (time, request_id, user_name, session, agent_name, system_content, user_content, assistant_content, assistant_tool_calls, tool_contents) "
    sql += "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    params = [memory_info.time, memory_info.request_id, memory_info.user_name, memory_info.session, memory_info.agent_name]
    params.extend([memory_info.system_content, memory_info.user_content, memory_info.assistant_content])
    params.append(str(memory_info.assistant_tool_calls) if memory_info.assistant_tool_calls else None)
    params.append(json.dumps(memory_info.tool_contents, ensure_ascii=False) if memory_info.tool_contents else None)
    db = BaseDatabases.create_database(uri=settings.CONFIG_DATABASE)
    try:
        await db.execute(sql=sql, parameters=params)
    finally:
        await db.clean()
