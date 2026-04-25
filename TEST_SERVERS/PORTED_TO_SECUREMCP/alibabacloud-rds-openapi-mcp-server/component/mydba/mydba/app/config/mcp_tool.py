# -*- coding: utf-8 -*-
import base64
import hashlib
import asyncio
import json
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class Transport(str, Enum):
    """mcp server 传输协议"""
    STDIO = "stdio"
    SSE = "sse"
TRANSPORT_VALUES = tuple(transport.value for transport in Transport)
TRANSPORT_TYPE = Literal[TRANSPORT_VALUES]

class McpInfo(BaseModel):
    name: str = Field(..., description="mcp 服务名称（全局唯一）")
    transport: TRANSPORT_TYPE = Field("sse", description="mcp server 的传输协议") # type: ignore
    description: Optional[str] = Field(None, description="服务描述")
    server_uri: Optional[str] = Field(None, description="mcp 服务器 URI")
    command: Optional[str] = Field(None, description="mcp server 启动命令")
    args: Optional[List[str]] = Field(None, description="mcp server 启动参数")
    envs: Optional[Dict[str, str]] = Field(None, description="mcp server 启动依赖的环境变量")
    def __repr__(self):
        info = self.model_dump()
        info['args'] = '******' if info['args'] else info['args']
        info['envs'] = '******' if info['envs'] else info['envs']
        return json.dumps(info, ensure_ascii=False)
    def __str__(self):
        info = self.model_dump()
        info['args'] = '******' if info['args'] else info['args']
        info['envs'] = '******' if info['envs'] else info['envs']
        return json.dumps(info, ensure_ascii=False)

class McpConfig(BaseModel):
    mcp_list: List[McpInfo] = Field(default_factory=list, description="mcp 列表")
    config_map: Dict[str, McpInfo] = Field(default_factory=dict, description="配置映射, name -> mcp server info")

    def add_mcp(self, name: str, transport: str="sse", description: Optional[str]=None, 
                server_uri: Optional[str]=None, command: Optional[str]=None, 
                args: Optional[str]=None, envs: Optional[str]=None) -> None:
        """添加 mcp 到列表"""
        if name in self.config_map:
            raise ValueError(f"mcp {name} already exists.")
        mcp_info = McpInfo(**{
            "name": name,
            "transport": transport,
            "description": description,
            "server_uri": server_uri,
            "command": command,
            "args": None if not args else json.loads(args),
            "envs": None if not envs else json.loads(envs)
        })
        self.mcp_list.append(mcp_info)
        self.config_map[name] = mcp_info
    
    def get_mcp_by_name(self, name) -> McpInfo:
        """
        根据 mcp 名称获取 mcp
        Args:
            name (str): mcp 服务名称（全局唯一）。
        Returns:
            McpInfo: mcp 信息。
        """
        return self.config_map.get(name)
mcp_config = McpConfig()

class McpToolInfo(BaseModel):
    tool_key: str = Field(None, description="工具标识（全局唯一）")
    server_name: str = Field(..., description="mcp 服务名称")
    tool_name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    input_schema: str = Field(..., description="工具参数描述")

    def format(self) -> dict:
        tool = {"type": "function"}
        tool["function"] = {
            "name": self.tool_key if self.tool_key else self.tool_name,
            "description": self.description,
            "parameters": json.loads(self.input_schema)
        }
        return tool
    
    def __repr__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
    
    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)

class McpToolConfig(BaseModel):
    mcp_tool_list: List[McpToolInfo] = Field(default_factory=list, description="mcp tool 列表")
    config_map: Dict[str, McpToolInfo] = Field(default_factory=dict, description="配置映射")
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock, description="配置的更新锁")

    async def add_mcp_tool(self, server_name: str, tool_name: str, description: str, input_schema: str) -> None:
        """
        添加 mcp tool 到列表
        Args:
            server_name (str): mcp 服务名称。
            tool_name (str): 工具名称。
            description (str): 工具描述。
            input_schema (str): 工具参数描述。
        """
        tool_key = f"{server_name}_{tool_name}"
        tool_key = hashlib.md5(tool_key.encode("utf-8")).digest()
        tool_key = base64.urlsafe_b64encode(tool_key).decode("utf-8")
        tool_key = tool_key.rstrip("=")
        mcp_tool_info = McpToolInfo(**{
            "tool_key": tool_key,
            "server_name": server_name,
            "tool_name": tool_name,
            "description": description,
            "input_schema": input_schema
        })

        # 使用 COW 机制，进行读写保护
        async with self.lock:
            mcp_tool_list = [mcp_tool_info]
            config_map = {
                tool_key: mcp_tool_info
            }
            for mcp_tool in self.mcp_tool_list:
                if mcp_tool.tool_key != tool_key:
                    mcp_tool_list.append(mcp_tool)
                    config_map[mcp_tool.tool_key] = mcp_tool
            
            self.mcp_tool_list = mcp_tool_list
            self.config_map = config_map
        return
    
    def get_mcp_tool_by_key(self, tool_key: str) -> McpToolInfo:
        """
        根据 tool_key 获取 mcp tool
        Args:
            tool_key (str): 工具标识（全局唯一）。
        Returns:
            McpToolInfo: mcp tool 信息。
        """
        return self.config_map.get(tool_key)
    
    class Config:
        arbitrary_types_allowed = True
mcp_tool_config = McpToolConfig()
