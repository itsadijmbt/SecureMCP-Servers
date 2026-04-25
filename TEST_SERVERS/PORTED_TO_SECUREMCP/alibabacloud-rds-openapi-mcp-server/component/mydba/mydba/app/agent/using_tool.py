# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from tenacity import RetryError
from mydba.app.agent.base import BaseAgent, cleanup_decorator
from mydba.app.config.agent import AgentMcp
from mydba.app.config.settings import settings
from mydba.app.llm import ToolChoice
from mydba.app.message.memory_history import MemoryInfo
from mydba.app.message.message import Message, ToolCall
from mydba.app.tool.tool_manager import tool_manager
from mydba.common.logger import logger
from mydba.common.session import get_context

class UsingToolAgent(BaseAgent, BaseModel):
    """
    工具型 Agent
    """
    system_message: Optional[Message] = Field(None, description="工具型 Agent 的系统提示信息")
    mcps: Optional[AgentMcp] = Field(default=None, description="绑定的 mcp 服务")
    
    def __init__(self, **data):
        super().__init__(**data)
        prompts = data.get("prompts", {})
        self.prompt_patterns["system"] = prompts.get("system")
        self.system_message = Message.system_message(self.prompt_patterns["system"])

    @cleanup_decorator
    async def run(self, query: str, context_memory: Optional[List[MemoryInfo]] = None) -> str:
        logger.info(f"[{self.name}] start to query: {query}")
        if context_memory:
            self.memory.extend(self.format_memory(context_memory))
        self.memory.append(Message.user_message(query))
        step_counter = 0
        tool_contents = None
        while step_counter < 100:
            # 调用大模型
            llm_result = await self._execute_model(step_counter == 0)

            #记录历史
            if step_counter == 0:
                await self.save_memory_history(system_content=self.system_message.content,
                                               user_content=query,
                                               assistant_content=llm_result.content,
                                               assistant_tool_calls=llm_result.tool_calls)
            else:
                await self.save_memory_history(assistant_content=llm_result.content,
                                               assistant_tool_calls=llm_result.tool_calls,
                                               tool_contents=tool_contents)
            if not llm_result.tool_calls:
                # 结束工具调用，返回结果
                logger.info(f"[{self.name}] query over, query: {query}, content: {llm_result.content}")
                return llm_result.content
            
            # 调用工具
            if step_counter >= settings.MAX_STEPS:
                logger.error(f"[{self.name}] call tool too much, break loop, step_counter: {step_counter}, query: {query}")
                raise Exception(f"Agent({self.name}) call tool too much, step_counter: {step_counter}, query: {query}")
            tool_contents = await self._execute_tool(llm_result.tool_calls)
            step_counter += 1
        logger.error(f"[{self.name}] call tool too much, step_counter: {step_counter}, query: {query}")
        raise Exception(f"Agent({self.name}) call tool too much, step_counter: {step_counter}, query: {query}")

    async def _execute_model(self, first: bool) -> Message:
        tools = await tool_manager.get_tool_list(filter_=self.mcps)
        tool_choice = ToolChoice.REQUIRED if first and tools else ToolChoice.AUTO
        context = get_context()
        result = await self.llm.ask_tool(
            messages=self.memory,
            system_msgs=[self.system_message],
            tools=tools,
            tool_choice=tool_choice,
            stream=context.detail_info,
        )
        #logger.info(f"[{self.name}] query model, first: {first}, result: {result}")
        self.memory.append(result)
        return result

    async def _execute_tool(self, tool_calls: List[ToolCall]) -> Dict[str, str]:
        tool_contents = []
        for tool_call in tool_calls:
            tool_name_infos = await tool_manager.convert_name(tool_call.function.name)
            tool_name = tool_name_infos[1] if len(tool_name_infos) >= 2 else tool_name_infos[0]
            for i in range(3):
                try:
                    result = await tool_manager.execute(tool_call.function.name, tool_call.function.arguments)
                    break
                except RetryError as re:
                    result = f"call tool failed, exception: {str(re.last_attempt.exception())}"
                    if not tool_manager.is_retryable_tool(tool_name):
                        break
                except Exception as e:
                    result = f"call tool failed, exception: {str(e)}"
                    if not tool_manager.is_retryable_tool(tool_name):
                        break
            logger.info(f"[{self.name}] call tool, params: {tool_call}, result: {result}")
            tool_message = Message.tool_message(content=result, tool_call_id=tool_call.id)
            self.memory.append(tool_message)
            tool_contents.append(tool_message.format())
        return tool_contents
