# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List, Optional
from mydba.app.agent.base import BaseAgent, cleanup_decorator
from mydba.app.config.settings import settings
from mydba.app.llm import ToolChoice
from mydba.app.message.memory_history import MemoryInfo
from mydba.app.message.message import Message
from mydba.app.tool.base_local_tool import LocalTool
from mydba.app.tool.tool_manager import tool_manager
from mydba.common import stream
from mydba.common.logger import logger
from mydba.common.session import get_context

class ReflectionAgent(BaseAgent, BaseModel):
    """
    反思型 Agent
    """
    system_message: Optional[Message] = Field(None, description="反思型 Agent 在回答问题时，使用的系统提示信息")
    reflection_system_message: Optional[Message] = Field(None, description="反思型 Agent 在反思答案时，使用的系统提示信息")
    
    def __init__(self, **data):
        super().__init__(**data)
        prompts = data.get("prompts", {})
        self.prompt_patterns["system"] = prompts.get("system")
        self.prompt_patterns["user"] = prompts.get("user")
        self.prompt_patterns["reflection_system"] = prompts.get("reflection_system")
        self.prompt_patterns["reflection_user"] = prompts.get("reflection_user")
        self.system_message = Message.system_message(self.prompt_patterns["system"])
        self.reflection_system_message = Message.system_message(self.prompt_patterns["reflection_system"])

    @cleanup_decorator
    async def run(self, query: str, context_memory: Optional[List[MemoryInfo]] = None) -> str:
        step_counter = 0
        content = None
        reflection = None
        logger.info(f"[{self.name}] start to query: {query}")
        while step_counter < 100:
            # 执行请求或者进行答案改进
            content = await self._act(query, context_memory, content, reflection)
            if content is None:
                logger.error(f"[{self.name}] act failed, query: {query}")
                raise Exception(f"Agent({self.name}) act failed, query: {query}")
            
            # 反思太多，直接返回
            if step_counter >= settings.MAX_STEPS:
                logger.error(f"[{self.name}] reflect too much, break loop, step_counter: {step_counter}, query: {query}, content: {content}, reflection: {reflection}")
                return content
            
            # 反思
            reflection = await self._reflect(query, content)
            if reflection is None:
                logger.info(f"[{self.name}] query over, query: {query}, content: {content}")
                return content
            step_counter += 1
        logger.error(f"[{self.name}] query failed, step_counter: {step_counter}, query: {query}, content: {content}, reflection: {reflection}")
        raise Exception(f"Agent({self.name}) query failed, step_counter: {step_counter}, query: {query}")

    async def _act(self, query: str, context_memory: Optional[List[MemoryInfo]],
                   answer: Optional[str], reflection: Optional[str]) -> str:
        """
        执行请求或者进行答案改进
        Args:
            query (str): 查询内容
            context_memory (list): 用户的上下文 memory
            answer (str): 上一轮生成的答案
            reflection (str): 反馈信息
        Returns:
            str: 执行结果
        """
        context = get_context()
        await stream.aprint(f"[A] {self.name} 执行中...")
        messages = self.format_memory(context_memory) if context_memory else []
        prompt = query if not reflection else self._get_user_prompt(query, answer, reflection)
        messages.append(Message.user_message(prompt))
        # 带上 interactive tool，实现 llm 和用户的交互
        tool = tool_manager.get_local_tool(LocalTool.INTERACTION)
        new_answer = None
        while True:
            llm_result = await self.llm.ask_tool(
                messages=messages,
                system_msgs=[self.system_message],
                tools=[tool],
                tool_choice=ToolChoice.AUTO,
                stream=context.detail_info,
            )
            #logger.info(f"[{self.name}] act, result: {llm_result}")
            if not llm_result.tool_calls:
                # 不需要调用工具，返回结果
                new_answer = llm_result.content
                break
            messages.append(llm_result)
            # 调用工具
            for tool_call in llm_result.tool_calls:
                try:
                    tool_result = await tool_manager.execute(tool_call.function.name, tool_call.function.arguments)
                    logger.info(f"[{self.name}] call tool, params: {tool_call}, result: {tool_result}")
                    tool_message = Message.tool_message(content=tool_result, tool_call_id=tool_call.id)
                except Exception as e:
                    tool_message = Message.tool_message(content=repr(e), tool_call_id=tool_call.id)
                messages.append(tool_message)
        await self.save_memory_history(system_content=self.system_message.content,
                                       user_content=prompt, assistant_content=new_answer)
        return new_answer
    
    async def _reflect(self, query: str, content: str) -> Optional[str]:
        """
        反思请求
        Args:
            query (str): 查询内容
            content (str): 执行结果
        Returns:
            str: 反思内容
        """
        context = get_context()
        await stream.aprint(f"[A] {self.name} 反思中...")
        prompt = self._get_reflection_user_prompt(query, content)
        message = Message.user_message(prompt)
        content = await self.llm.ask(
            messages=[message],
            system_msgs=[self.reflection_system_message],
            stream=context.detail_info,
        )
        #logger.info(f"[{self.name}] reflect, result: {content}")
        await self.save_memory_history(system_content=self.reflection_system_message.content,
                                       user_content=prompt, assistant_content=content)
        return None if content=="None" else content
    
    def _get_user_prompt(self, query: str, content: str, reflection: str) -> str:
        user_prompt = self.prompt_patterns["user"].format(query=query, content=content, reflection=reflection)
        logger.debug(f"[{self.name}] user prompt: {user_prompt}")
        return user_prompt
    
    def _get_reflection_user_prompt(self, query: str, content: str) -> str:
        reflection_user_prompt = self.prompt_patterns["reflection_user"].format(query=query, content=content)
        logger.debug(f"[{self.name}] reflection user prompt: {reflection_user_prompt}")
        return reflection_user_prompt
