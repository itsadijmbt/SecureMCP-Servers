# -*- coding: utf-8 -*-
import json
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional, Union

class AgentMode(str, Enum):
    """定义工具调用的选择方式"""
    CHAT = "chat" # 普通对话型 Agent
    ROUTER = "router" # 路由型 Agent
    REFLECTION = "reflection" # 反思型 Agent
    USING_TOOL = "using_tool" # 工具型 Agent

AGENT_MODE_VALUES = tuple(mode.value for mode in AgentMode)
AGENT_MODE_TYPE = Literal[AGENT_MODE_VALUES]

class AgentMcp(BaseModel):
    allow: Optional[List[str]] = Field(default=None, description="允许列表")
    deny: Optional[List[str]] = Field(default=None, description="拒绝列表")

class AgentInfo(BaseModel):
    name: str = Field(..., description="Agent 名称")
    mode: AGENT_MODE_TYPE = Field(..., description="Agent 模式") # type: ignore
    intent: Optional[str] = Field(None, description="意图名称，用于意图识别，除 Router agent 外，都需要配置此信息")
    intent_description: Optional[str] = Field(None, description="意图描述，用于帮助 LLM 识别意图，除 Router agent 外，都需要配置此信息")
    prompts: Optional[Dict[str, Union[str, List[str]]]] = Field(default=None, description="""Agent 提示词模版，包含键值:
                                                                1) system: 系统提示词或模版，
                                                                2) user: 用户提示词模版，在需要改写用户提示词的场景下使用，例如：REFLECTION 模式、ROUTER 模式，
                                                                3) reflection_system: 反思提示词，仅在 REFLECTION 模式下使用，
                                                                4) reflection_user: 反思提示词模版，仅在 REFLECTION 模式下使用，
                                                                5) condition: 条件提示词(List)，在意图识别时，描述意图的约束条件，
                                                                6) shot: 样本提示词(List)，在意图识别时，提供意图样本""")
    mcps: Optional[AgentMcp] = Field(default=None, description="绑定的 mcp 服务，USING_TOOL 模式下有效")
    is_main: bool = Field(default=False, description="是否为主 Agent")
    is_default: bool = Field(default=False, description="是否为默认 Agent")

class AgentConfig(BaseModel):
    agent_list: List[AgentInfo] = Field(default_factory=list, description="Agent 列表")
    config_map: Dict[str, AgentInfo] = Field(default_factory=dict, description="配置映射")

    def add_agent(self, name: str, mode: str, intent: Optional[str] = None, 
                  intent_description: Optional[str] = None, prompts: Optional[str] = None, 
                  mcps: Optional[str] = None, is_main: bool = False, is_default: bool = False) -> None:
        """
        添加 Agent 到列表。
        Args:
            name (str): Agent 名称。
            mode (str): Agent 模式。
            intent (str): 意图名称，用于意图识别，除 Router agent 外，都需要配置此信息。
            intent_description (str): 意图描述，用于帮助 LLM 识别意图，除 Router agent 外，都需要配置此信息。
            prompts (str): Agent 提示词。
            mcps (str): 绑定的 mcp 服务。
            is_main (bool): 是否为主 Agent。
            is_default (bool): 是否为默认 Agent。
        """
        if name in self.config_map:
            raise ValueError(f"Agent {name} already exists.")
        mcps = json.loads(mcps) if mcps else None
        agent_info = AgentInfo(**{
            "name": name,
            "mode": mode,
            "intent": intent,
            "intent_description": intent_description,
            "prompts": None if not prompts else json.loads(prompts),
            "mcps": None if not mcps else AgentMcp(**mcps),
            "is_main": is_main,
            "is_default": is_default
        })
        self.agent_list.append(agent_info)
        if intent:
            self.config_map[intent] = agent_info
    
    def get_agent_by_intent(self, intent: str) -> Optional[AgentInfo]:
        """
        根据意图获取 Agent。
        Args:
            name (str): Agent 名称。
        Returns:
            AgentInfo: Agent 信息。
        """
        return self.config_map.get(intent)
    
    def get_default_agent(self) -> Optional[AgentInfo]:
        """
        获取默认 Agent。
        Returns:
            AgentInfo: Agent 信息。
        """
        return next(filter(lambda agent: agent.is_default, self.agent_list), None)
    
    def get_main_agent(self) -> Optional[AgentInfo]:
        """
        获取主 Agent。
        Returns:
            AgentInfo: Agent 信息。
        """
        return next(filter(lambda agent: agent.is_main, self.agent_list), None)
    
    def get_sub_agents(self) -> List[AgentInfo]:
        """
        获取子 Agent。
        Returns:
            List[AgentInfo]: 子 Agent 列表。
        """
        return list(filter(lambda agent: not agent.is_main, self.agent_list))
agent_config = AgentConfig()
