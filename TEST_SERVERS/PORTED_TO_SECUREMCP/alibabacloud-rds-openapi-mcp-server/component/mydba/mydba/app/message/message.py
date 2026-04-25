# -*- coding: utf-8 -*-
import json
from abc import ABC
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Any, List, Optional, Union

class Role(str, Enum):
    """定义参与对话的角色"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant" 
    TOOL = "tool"

class Function(BaseModel):
    name: str = Field(..., description="工具函数的名称")
    arguments: str = Field(..., description="工具函数的入参")
    def __repr__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)

class ToolCall(BaseModel):
    id: str = Field(..., description="模型为本次调用分配的 id")
    type: str = Field(default="function", description="调用的类型，目前只有 function")
    function: Function = Field(..., description="模型需要调用的工具函数")
    def __repr__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)

class Message(BaseModel):
    role: str = Field(..., description="消息的角色")
    content: Optional[str] = Field(default=None, description="消息的内容")
    name: str = Field(None, description="用户名称")
    tool_calls: Optional[List[ToolCall]] = Field(default=None, description="调用列表")
    tool_call_id: Optional[str] = Field(default=None, description="模型为调用分配的 id")
    time: datetime = Field(default_factory=datetime.now, description="消息时间")
    
    @classmethod
    def user_message(cls, content: str) -> "Message":
        """用户消息"""
        return cls(role=Role.USER, content=content)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        """系统消息"""
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def assistant_message(cls, content: Optional[str] = None, tool_calls: Optional[List[Any]] = None) -> "Message":
        """LLM 返回消息"""
        formatted_calls = None
        if tool_calls:
            formatted_calls = [
                {"id": call.id, "function": call.function.model_dump(), "type": "function"} for call in tool_calls
            ]
        if not content and not formatted_calls:
            raise ValueError("content and tool_calls cannot be both None")
        return cls(role=Role.ASSISTANT, content=content, tool_calls=formatted_calls)

    @classmethod
    def tool_message(cls, content: str, tool_call_id: str) -> "Message":
        """工具调用消息"""
        return cls(role=Role.TOOL, content=content, tool_call_id=tool_call_id)
    
    def format(self) -> dict:
        """格式化消息为字典，进行 LLM 调用"""
        message = {"role": self.role}
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls is not None:
            message["tool_calls"] = [tool_call.model_dump() for tool_call in self.tool_calls]
        if self.name is not None:
            message["name"] = self.name
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        return message
    
    def __repr__(self):
        return str(self.format())
    
    def __str__(self):
        return str(self.format())
