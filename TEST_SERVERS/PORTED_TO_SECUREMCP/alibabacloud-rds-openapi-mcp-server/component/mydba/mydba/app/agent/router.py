# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import List, Optional
from mydba.app.agent.base import BaseAgent, cleanup_decorator
from mydba.app.config.agent import agent_config
from mydba.app.message.memory_history import MemoryInfo
from mydba.app.message.message import Message
from mydba.app.prompt import router
from mydba.common import stream
from mydba.common.logger import logger
from mydba.common.session import get_context

class RouterAgent(BaseAgent, BaseModel):
    """
    路由型 Agent
    """
    system_message: Optional[Message] = Field(None, description="路由型 Agent 的系统提示信息")
    
    def __init__(self, **data):
        super().__init__(**data)
        prompts = data.get("prompts")
        self.prompt_patterns["system"] = prompts.get("system")
        self.prompt_patterns["user"] = prompts.get("user")
        self.system_message = Message.system_message(self._get_system_prompt())
    
    @cleanup_decorator
    async def run(self, query: str, context_memory: Optional[List[MemoryInfo]] = None) -> str:
        sub_agents = agent_config.get_sub_agents()
        if len(sub_agents) == 1:
            # 只有一个子 Agent，直接使用
            agent_info = sub_agents[0]
        else:
            # 意图识别，结合历史上下文
            logger.info(f"[{self.name}] start to detect, query: {query}")
            intent = await self._predict_intent(query, context_memory)
            await stream.aprint(f"[A] 意图: {intent}")
            agent_info = agent_config.get_agent_by_intent(intent)
        action_agent = BaseAgent.create_agent(agent_info, self.llm)
        content = await action_agent.run(query, context_memory)
        await self.save_memory_history(system_content=self.system_message.content,
                                       user_content=query, assistant_content=content)
        return content

    async def _predict_intent(self, query: str, context_memory: Optional[List[MemoryInfo]] = None) -> str:
        """
        预测请求意图
        Args:
            query (str): 用户请求内容
            context_memory (list): 用户的上下文 memory
        Returns:
            str: The detected intent.
        """
        messages = []
        if context_memory:
            for mem in context_memory:
                messages.append(Message.user_message(mem.user_content))
                messages.append(Message.assistant_message(mem.assistant_content))
        prompt = self._get_user_prompt(query)
        messages.append(Message.user_message(prompt))
        context = get_context()
        content = await self.llm.ask(
            messages=messages,
            system_msgs=[self.system_message],
            stream=context.detail_info,
        )
        logger.info(f"[{self.name}] detect intent, result: {content}")
        agent_info = agent_config.get_agent_by_intent(content)
        if agent_info is None:
            logger.warning(f"[{self.name}] predict intent failed, using default agent, query: {query}, content: {content}")
            agent_info = agent_config.get_default_agent()
            return agent_info.intent
        return content

    def _get_system_prompt(self) -> str:
        system_prompt = self.prompt_patterns["system"]
        sub_agent_list = agent_config.get_sub_agents()
        system_prompt = system_prompt.format(intent_infos=router.pack_intent_info(sub_agent_list),
                                             default_intent=router.pack_default_intent(sub_agent_list),
                                             intent_names=router.pack_intent_name(sub_agent_list),
                                             conditions=router.pack_condition(sub_agent_list),
                                             shots=router.pack_shot(sub_agent_list))
        logger.debug(f"[{self.name}] system prompt: {system_prompt}")
        return system_prompt

    def _get_user_prompt(self, query: str) -> str:
        user_prompt = self.prompt_patterns["user"].format(query=query)
        logger.debug(f"[{self.name}] user prompt: {user_prompt}")
        return user_prompt
