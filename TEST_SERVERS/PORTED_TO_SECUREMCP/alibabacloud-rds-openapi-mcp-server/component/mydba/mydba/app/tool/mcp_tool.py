# -*- coding: utf-8 -*-
import asyncio
from datetime import timedelta
import json
import os
import shutil
from contextlib import AsyncExitStack
from exceptiongroup import ExceptionGroup
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict
from mydba.app.config.mcp_tool import McpInfo, Transport
from mydba.common.logger import logger

class McpClient(BaseModel):
    """Manages MCP server connections and tool execution."""
    mcp_info: McpInfo = Field(..., description="mcp server 信息")
    timeout: int = Field(30, description="mcp client session 超时时间")

    async def list_tools(self) -> list[Dict[str, str]]:
        tools = []
        if self.mcp_info.transport == Transport.STDIO:
            envs = self._merge_env(self.mcp_info.envs)
            server_params = StdioServerParameters(
                command=self.mcp_info.command,
                args=self.mcp_info.args,
                env=envs,
            )
            async with stdio_client(server_params) as streams:
                read, write = streams
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=self.timeout)) as session:
                    await session.initialize()
                    tools_response = await session.list_tools()
                    for tool in tools_response.tools:
                        tools.append({
                            'server_name': self.mcp_info.name, 
                            'tool_name': tool.name, 
                            'description': tool.description, 
                            'input_schema': json.dumps(tool.inputSchema)})
        else:
            async with sse_client(self.mcp_info.server_uri) as streams:
                read, write = streams
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=self.timeout)) as session:
                    await session.initialize()
                    tools_response = await session.list_tools()
                    for tool in tools_response.tools:
                        tools.append({
                            'server_name': self.mcp_info.name, 
                            'tool_name': tool.name, 
                            'description': tool.description, 
                            'input_schema': json.dumps(tool.inputSchema)})
        return tools

    async def execute_tool(self, tool_name: str, arguments: Optional[dict[str, Any]] = None) -> str:
        if self.mcp_info.transport == Transport.STDIO:
            envs = self._merge_env(self.mcp_info.envs)
            server_params = StdioServerParameters(
                command=self.mcp_info.command,
                args=self.mcp_info.args,
                env=envs,
            )
            async with stdio_client(server_params) as streams:
                read, write = streams
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=self.timeout)) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
        else:
            async with sse_client(self.mcp_info.server_uri) as streams:
                read, write = streams
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=self.timeout)) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
        if result.isError:
            raise Exception(f"execute fail, resp={result.content}")
        # 默认取 text 信息
        return result.content[0].text
    
    def _merge_env(self, mcp_envs: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """合并 mcp env 和当前环境的 env"""
        envs = {**os.environ}
        if 'VIRTUAL_ENV' in envs:
            del envs['VIRTUAL_ENV']
        if not mcp_envs:
            return envs
        for k, v in mcp_envs.items():
            if v:
                envs[k] = v
        return envs
