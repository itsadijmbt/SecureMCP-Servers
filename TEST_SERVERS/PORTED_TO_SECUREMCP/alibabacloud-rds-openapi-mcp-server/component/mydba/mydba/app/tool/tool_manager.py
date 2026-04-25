# -*- coding: utf-8 -*-
import asyncio
import json
from datetime import datetime
from exceptiongroup import ExceptionGroup
from typing import List, Optional
from mydba.app.config.agent import AgentMcp
from mydba.app.config.settings import settings
from mydba.app.config.mcp_tool import  McpToolInfo, mcp_config, mcp_tool_config
from mydba.app.tool.base_local_tool import LOCAL_TOOL_VALUES, LOCAL_TOOL_TYPE, BaseLocalTool, LocalTool
from mydba.app.tool.interaction import Interaction
from mydba.app.tool.mcp_tool import McpClient
from mydba.app.tool.mysql_execution import MySQLExecution
from mydba.common import stream
from mydba.common.global_settings import global_settings
from mydba.common.logger import logger
from mydba.common.session import get_context, set_context, reset_context

RETRYABLE_NAME_PREFIX = ['get', 'describe', 'list']

class ToolManager:
    def __init__(self):
        # mcp 工具列表上次刷新时间
        self.last_refresh_time = 0
        self.local_tool_map = {
            LocalTool.INTERACTION.value: Interaction(),
            LocalTool.MYSQL_EXECUTION.value: MySQLExecution()
        }
        pass

    async def get_tool_list(self, filter_: Optional[AgentMcp] = None) -> List[McpToolInfo]:
        """
        获取最新的 tool 列表
        Args:
            filter_ (AgentMcp): 过滤器，包含 allow 和 deny 列表。
        Returns:
            list: tool 列表。
        """
        await self._wait_refresh()
        tools = self.get_local_tool_list()
        tools.extend(mcp_tool_config.mcp_tool_list)
        if filter_ and filter_.allow:
            tools = list(filter(lambda tool: tool.server_name in filter_.allow, tools))
        elif filter_ and filter_.deny:
            tools = list(filter(lambda tool: tool.server_name not in filter_.deny, tools))
        return tools

    def get_local_tool(self, name:LOCAL_TOOL_TYPE) -> McpToolInfo: # type: ignore
        if name not in self.local_tool_map:
            raise ValueError(f"local tool '{name}' does not exist")
        tool = self.local_tool_map[name]
        return self._convert(tool)

    def get_local_tool_list(self) -> List[McpToolInfo]:
        tool_infos = []
        for _, tool in self.local_tool_map.items():
            tool_info = self._convert(tool)
            tool_infos.append(tool_info)
        return tool_infos
    
    def is_retryable_tool(self, tool_name: str) -> bool:
        """工具是否能重试调用"""
        for prefix in RETRYABLE_NAME_PREFIX:
            if tool_name.lower().startswith(prefix):
                return True
        return False
    
    async def convert_name(self, tool_key: str) -> List[str]:
        """
        转换 tool_key 为可识读的名称
        Args:
            tool_key (str): 工具名称或者工具 tool_key
        Returns:
            str: 工具可识读名称
        """
        if tool_key in LOCAL_TOOL_VALUES:
            return [tool_key, ]
        mcp_tool_info = mcp_tool_config.get_mcp_tool_by_key(tool_key)
        if not mcp_tool_info:
            return [tool_key, ]
        return [mcp_tool_info.server_name, mcp_tool_info.tool_name]
    
    async def execute(self, name:str, arguments:str) -> str:
        # 输出工具信息
        context = get_context()
        tool_name_infos = await self.convert_name(name)
        if name != LocalTool.INTERACTION.value:
            await stream.aprint(f"[A] 执行工具 {'::'.join(tool_name_infos)}")
            if context.detail_info:
                await stream.aprint(f"  - 参数: {arguments}")
        
        # 执行工具调用
        if name in LOCAL_TOOL_VALUES:
            result = await self._execute_local_tool(name, arguments)
        else:
            result = await self._execute_mcp_tool(name, arguments)
        
        # 输出调用结果
        if name != LocalTool.INTERACTION.value and context.detail_info:
            await stream.aprint(f"  - 返回: {result}")
        return result

    async def _execute_local_tool(self, name:LOCAL_TOOL_TYPE, arguments:str) -> str: # type: ignore
        tool = self.local_tool_map.get(name)
        if tool is None:
            raise Exception(f"The specified tool '{name}' does not exist.")
        return await tool.execute(arguments)

    async def _execute_mcp_tool(self, name:str, arguments:str) -> str:
        mcp_client = await self._get_mcp_client(tool_key=name)
        mcp_tool_info = mcp_tool_config.get_mcp_tool_by_key(name)
        logger.info(f"[tool] call tool, service name: {mcp_tool_info.server_name}, tool name: {mcp_tool_info.tool_name}")
        return await mcp_client.execute_tool(tool_name=mcp_tool_info.tool_name,
                                             arguments=None if not arguments else json.loads(arguments))
    
    async def _get_mcp_client(self, tool_key:str) -> McpClient:
        """
        获取 mcp client。
        Args:
            tool_key (str): mcp tool key。
        Returns:
            mcp_client: mcp client 对象。
        """
        mcp_tool_info = mcp_tool_config.get_mcp_tool_by_key(tool_key)
        if not mcp_tool_info:
            logger.error(f"[tool] mcp tool {tool_key} not exist, tool list: {mcp_tool_config.mcp_tool_list}")
            raise Exception(f"tool {tool_key} not exist")
        mcp_info = mcp_config.get_mcp_by_name(mcp_tool_info.server_name)
        if not mcp_info:
            logger.error(f"[tool] mcp server {mcp_tool_info.server_name} not exist, tool list: {mcp_tool_config.mcp_tool_list}")
            raise Exception(f"mcp server {mcp_tool_info.server_name} not found")
        mcp_client = McpClient(mcp_info=mcp_info)
        return mcp_client

    async def _wait_refresh(self) -> None:
        if self.last_refresh_time == 0:
            token = set_context(None)
            asyncio.create_task(self._refresh_tool_list())
            reset_context(token)
            logger.info("[tool] tool list is being refreshed...")
            while self.last_refresh_time == 0:
                logger.info("[tool] Waiting for refreshing to complete")
                await asyncio.sleep(1)
        return

    async def _fetch_tool_list(self) -> None:
        """
        获取 tool 列表
        """
        if not mcp_config.mcp_list:
            return
        for mcp_info in mcp_config.mcp_list:
            try:
                mcp_client = McpClient(mcp_info=mcp_info)
                tools = await mcp_client.list_tools()
                for tool in tools:
                    description = f"{mcp_info.description}\n{tool.get('description')}" if mcp_info.description else tool.get('description')
                    await mcp_tool_config.add_mcp_tool(server_name=tool.get('server_name'), tool_name=tool.get('tool_name'),
                                                       description=description, input_schema=tool.get('input_schema'))
            except ExceptionGroup as eg:
                logger.error(f"[tool] fetch tool exception, mcp: {mcp_info}")
                for task in eg.exceptions:
                    logger.error(f"[tool] task raised an exception: {task}")
            except Exception as e:
                logger.error(f"[tool] fetch tool exception, mcp: {mcp_info}, ex: {e}")

    async def _refresh_tool_list(self) -> None:
        """
        刷新 tool 列表
        """
        while True:
            if global_settings.IS_EXIT:
                break
            elif datetime.now().timestamp() - self.last_refresh_time > settings.REFRESH_INTERVAL:
                await self._fetch_tool_list()
                logger.info(f"[tool] refresh tool list over")
                self.last_refresh_time = datetime.now().timestamp()
            else:
                try:
                    await asyncio.sleep(1)
                except BaseException:
                    pass
    
    def _convert(self, local_tool:BaseLocalTool) -> McpToolInfo:
        return McpToolInfo(tool_key=local_tool.tool_name, server_name="local-tool", tool_name=local_tool.tool_name,
                           description=local_tool.description, input_schema=json.dumps(local_tool.input_schema, ensure_ascii=False))
tool_manager = ToolManager()
