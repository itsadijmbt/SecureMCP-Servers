# -*- coding: utf-8 -*-
import json
from abc import ABC
from enum import Enum
from typing import Any, Dict, Literal
from pydantic import BaseModel, Field

class LocalTool(str, Enum):
    """本地工具"""
    INTERACTION = "interaction"
    MYSQL_EXECUTION = "mysql_execution"

LOCAL_TOOL_VALUES = tuple(tool.value for tool in LocalTool)
LOCAL_TOOL_TYPE = Literal[LOCAL_TOOL_VALUES]

class BaseLocalTool(ABC, BaseModel):
    tool_name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    input_schema: Dict = Field(..., description="工具参数描述")

    async def execute(self, arguments: str) -> str:
        return NotImplementedError("Subclasses must implement this method")
    
    def _parse_arguments(self, arguments: str) -> Dict[str, Any]:
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError as e:
            raise ValueError(f"The parameters for tool '{self.tool_name}' are in an incorrect format.")
        return args
