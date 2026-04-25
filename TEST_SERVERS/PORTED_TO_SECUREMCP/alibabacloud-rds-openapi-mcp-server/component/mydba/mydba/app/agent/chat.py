# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List, Optional
from mydba.app.agent.base import BaseAgent, cleanup_decorator
from mydba.app.message.memory_history import MemoryInfo
from mydba.app.message.message import Message
from mydba.common.logger import logger
from mydba.common.session import get_context

class ChatAgent(BaseAgent, BaseModel):
    """
    普通对话型 Agent
    """
    system_message: Optional[Message] = Field(None, description="对话 Agent 的系统提示信息")
    
    def __init__(self, **data):
        super().__init__(**data)
        prompts = data.get("prompts", {})
        self.prompt_patterns["system"] = prompts.get("system")
        self.system_message = Message.system_message(self.prompt_patterns["system"])

    @cleanup_decorator
    async def run(self, query: str, context_memory: Optional[List[MemoryInfo]] = None) -> str:
        logger.info(f"[{self.name}] start to query: {query}")
        content = await self._execute_model(query, context_memory)
        if content is None:
            logger.error(f"[{self.name}] query model failed, query: {query}")
            raise Exception(f"Agent({self.name}) query model failed, query: {query}")
        #logger.info(f"[{self.name}] query over, result: {content}")
        await self.save_memory_history(system_content=self.system_message.content,
                                       user_content=query, assistant_content=content)
        return content

    async def _execute_model(self, query: str, context_memory: Optional[List[MemoryInfo]]) -> str:
        context = get_context()
        messages = self.format_memory(context_memory) if context_memory else []
        messages.append(Message.user_message(query))
        result = await self.llm.ask(
            messages=messages,
            system_msgs=[self.system_message],
            stream=context.detail_info,
        )
        return result
