# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
from datetime import datetime, timedelta
from mydba.app.config.settings import settings
from mydba.app.config.agent import AgentInfo, AgentMode
from mydba.app.llm import LLM
from mydba.app.message import memory_history
from mydba.app.message.message import Message, ToolCall
from mydba.app.message.memory_history import MemoryInfo
from mydba.common.session import get_context

def cleanup_decorator(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        finally:
            if not isinstance(self, BaseAgent):
                raise TypeError("self must be an instance of BaseAgent")
            self.cleanup()
    return wrapper

class BaseAgent(ABC, BaseModel):
    """
    Base class for all agents.
    """
    name: str = Field(..., description="Agent 名称")
    intent: Optional[str] = Field(None, description="意图名称")
    intent_description: Optional[str] = Field(None, description="意图描述")
    is_main: bool = Field(..., description="是否主 Agent")
    memory: List[Message] = Field(default_factory=list, description="本次处理过程中的短期记忆")
    prompt_patterns: Dict[str, str] = Field(default_factory=dict, description="提示词模版，不同类型的 Agent 依赖的提示词模版会有不同")
    llm: LLM = Field(..., description="LLM 实例")
    
    @abstractmethod
    async def run(self, query: str, context_memory: Optional[List[MemoryInfo]] = None) -> str:
        """
        该方法用于执行 Agent 的主要逻辑。
        Args:
            query (str): 查询内容。
            context_memory (list): 用户的上下文 memory。
        Returns:
            str: 执行结果。
        """
        return NotImplementedError("Subclasses must implement this method")
    
    async def get_history_memory(self) -> List[MemoryInfo]:
        """
        该方法用于获取 Agent 的历史 memory。
        Returns:
            list: Agent 的历史 memory。
        """
        context = get_context()
        start_time = datetime.now() - timedelta(minutes=30)
        context_memory = await memory_history.get_memory(user_name=context.user_name, session=context.session,
                                                         agent_name=self.name, start_time=start_time)
        return context_memory[::-1]
    
    async def save_memory_history(self,
                                  system_content: Optional[str] = None, 
                                  user_content: Optional[str] = None,
                                  assistant_content: Optional[str] = None,
                                  assistant_tool_calls: Optional[List[ToolCall]] = None,
                                  tool_contents: Optional[List[Dict[str, str]]] = None) -> None:
        """
        该方法用于保存 Agent 的 memory。
        Args:
            system_content (str): 系统提示词。
            user_content (str): 用户提示词。
            assistant_content (str): 大模型返回内容。
            assistant_tool_calls (List[ToolCall]): 大模型返回的工具调用。
            tool_contents (List[Dict[str, str]): 工具调用的结果，结果信息的格式为 {"tool_call_id": "xxx", "content": "xxx"}。
        """
        context = get_context()
        await memory_history.save_memory(
            MemoryInfo(
                time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                request_id = context.request_id if context else '',
                user_name="" if not context else context.user_name,
                session="" if not context else context.session,
                agent_name=self.name,
                system_content=system_content,
                user_content=user_content,
                assistant_content=assistant_content,
                assistant_tool_calls=assistant_tool_calls,
                tool_contents=tool_contents
            )
        )
    
    def format_memory(self, context_memory: Optional[List[MemoryInfo]] = None) -> Optional[List[Message]]:
        messages = None
        if context_memory:
            messages = []
            for mem in context_memory:
                if mem.user_content:
                    messages.append(Message.user_message(mem.user_content))
                if mem.tool_contents:
                    for tool_content in mem.tool_contents:
                        messages.append(Message.tool_message(tool_content["content"],
                                                             tool_content["tool_call_id"]))
                if mem.assistant_content or mem.assistant_tool_calls:
                    messages.append(Message.assistant_message(mem.assistant_content,
                                                              mem.assistant_tool_calls))
        return messages
    
    def cleanup(self) -> None:
        """
        该方法用于清理 Agent 的状态和资源。
        """
        self.memory.clear()

    @staticmethod
    def create_agent(agent_info: AgentInfo, llm: LLM) -> "BaseAgent":
        """
        创建 Agent 实例
        Args:
            agent_info (dict): Agent 信息
            llm (LLM): 在同一个请求会话中里，复用 llm
        Returns:
            BaseAgent: Agent 实例
        """
        from mydba.app.agent.chat import ChatAgent
        from mydba.app.agent.router import RouterAgent
        from mydba.app.agent.reflection import ReflectionAgent
        from mydba.app.agent.using_tool import UsingToolAgent
        agent_factory = {
            AgentMode.CHAT.value: ChatAgent,
            AgentMode.ROUTER.value: RouterAgent,
            AgentMode.REFLECTION.value: ReflectionAgent,
            AgentMode.USING_TOOL.value: UsingToolAgent,
        }
        if agent_info.mode not in agent_factory:
            raise ValueError(f"Agent mode {agent_info.mode} not supported")
        return agent_factory[agent_info.mode](llm=llm, **agent_info.dict())
