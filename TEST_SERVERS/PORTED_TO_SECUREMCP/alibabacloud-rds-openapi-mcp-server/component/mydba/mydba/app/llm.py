# -*- coding: utf-8 -*-
from openai import AsyncOpenAI, OpenAIError
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from mydba.app.config.mcp_tool import McpToolInfo
from mydba.app.message.message import Message
from mydba.common import stream as common_stream
from mydba.common.logger import logger

class ToolChoice(str, Enum):
    """定义工具调用的选择方式"""
    NONE = "none"
    AUTO = "auto"
    REQUIRED = "required"

TOOL_CHOICE_VALUES = tuple(choice.value for choice in ToolChoice)

class LLM(BaseModel):
    model: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    max_tokens: int = Field(4096, description="最大 token 数量")
    temperature: float = Field(1.0, description="温度")
    client: Optional[Any] = Field(None, description="openAI client，用于调用 llm")

    def __init__(self, **data):
        super().__init__(**data)
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def format_messages(self, messages: List[Message]) -> List[dict]:
        """格式化消息列表"""
        formatted_messages = []
        for message in messages:
            formatted_messages.append(message.format())
        return formatted_messages
    
    def format_tools(self, tools: List[McpToolInfo]) -> List[dict]:
        """格式化工具列表"""
        formatted_tools = []
        for tool in tools:
            formatted_tools.append(tool.format())
        return formatted_tools

    @retry(wait=wait_exponential(min=1, max=5), stop=stop_after_attempt(3))
    async def ask(self,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        stream: bool = True,
        timeout: int = 60
    ) -> str:
        """
        发送请求到 LLM 并获取响应，不使用函数调用。
        该方法支持流式返回。
        Args:
            messages: 对话消息列表
            system_msgs: 系统消息
            stream: 是否启用流式消息返回
            timeout: 请求超时时间
        Returns:
            str: LLM 的响应内容
        Raises:
            ValueError: 如果消息格式不正确或响应无效
            OpenAIError: 如果 API 调用失败
            Exception: 其他异常
        """
        try:
            if system_msgs:
                messages = system_msgs + messages
            messages = self.format_messages(messages)
            if not stream:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    timeout=timeout,
                    stream=False,
                )
                if not response.choices or not response.choices[0].message.content:
                    logger.warning(f"empty response from LLM")
                    raise ValueError("Empty or invalid response from LLM")
                result = response.choices[0].message.content
            else:
                await common_stream.aprint(f"[A] 请求大模型({self.model})")
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    timeout=timeout,
                    stream=True,
                )
                collected_messages = []
                async for chunk in response:
                    chunk_message = chunk.choices[0].delta.content or ""
                    if chunk_message:
                        await common_stream.aprint(chunk_message, end="")
                    collected_messages.append(chunk_message)
                result = "".join(collected_messages).strip()
                if not result:
                    logger.warning(f"empty response from LLM")
                    raise ValueError("Empty response from streaming LLM")
                else:
                    await common_stream.aprint("")
            logger.info(f"stream={stream}, timeout={timeout}, messages={messages}, result={result}")
            return result
        except ValueError as ve:
            logger.error(f"validation error: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"openAI API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"unexpected error in ask: {e}")
            raise
    
    @retry(wait=wait_exponential(min=1, max=5), stop=stop_after_attempt(3))
    async def ask_tool(
        self,
        messages: List[Message],
        system_msgs: Optional[List[Message]] = None,
        tools: List[McpToolInfo] = None,
        tool_choice: str = ToolChoice.REQUIRED,
        stream: bool = True,
        timeout: int = 60
    ) -> Message:
        """使用工具调用 LLM 并返回响应。不支持流式返回。
        该方法支持函数调用。
        Args:
            messages: 对话消息列表
            system_msgs: 系统消息
            tools: 工具列表
            tool_choice: 工具选择方式
            stream: 是否启用流式消息返回
            timeout: 请求超时时间
        Returns:
            Message: LLM 的响应消息
        Raises:
            ValueError: 如果工具选择方式无效或消息格式不正确
            OpenAIError: 如果 API 调用失败
            Exception: 其他异常
        """
        try:
            if tool_choice not in TOOL_CHOICE_VALUES:
                raise ValueError(f"Invalid tool_choice: {tool_choice}")
            if system_msgs:
                messages = system_msgs + messages
            messages = self.format_messages(messages)
            tools = self.format_tools(tools)
            if not stream:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=tools,
                    tool_choice=tool_choice,
                    timeout=timeout,
                    stream=False,
                )
                if not response.choices or not response.choices[0].message:
                    logger.warning(f"empty response from LLM")
                    raise ValueError("Invalid or empty response from LLM")
                result = Message.assistant_message(
                    content=response.choices[0].message.content,
                    tool_calls=response.choices[0].message.tool_calls
                )
            else:
                await common_stream.aprint(f"[A] 请求大模型({self.model})")
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=tools,
                    tool_choice=tool_choice,
                    timeout=timeout,
                    stream=True,
                )
                collected_messages = []
                collected_tool_calls = []
                has_content_msg = False
                async for chunk in response:
                    chunk_message = chunk.choices[0].delta.content or ""
                    if chunk_message:
                        has_content_msg = True
                        await common_stream.aprint(chunk_message, end="")
                    elif not has_content_msg:
                        await common_stream.aprint('.', end="")
                    collected_messages.append(chunk_message)
                    if chunk.choices[0].delta.tool_calls:
                        collected_tool_calls.extend(chunk.choices[0].delta.tool_calls)
                full_response = "".join(collected_messages).strip()
                await common_stream.aprint("")
                result = Message.assistant_message(
                    content=full_response,
                    tool_calls=self._merged_tool_calls(collected_tool_calls)
                )
            logger.info(f"stream={stream}, timeout={timeout}, messages={messages}, tools={tools}, tool_choice={tool_choice}, result={result}")
            return result
        except ValueError as ve:
            logger.error(f"validation error in ask_tool: {ve}")
            raise
        except OpenAIError as oe:
            logger.error(f"openAI API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"unexpected error in ask: {e}")
            raise

    def _merged_tool_calls(self, tool_calls : list) -> Optional[list]:
        """流式调用时，合并工具调用信息"""
        if not tool_calls:
            return None
        calls_index = []
        merged_calls = {}
        last_call_id = None
        for call in tool_calls:
            call_id = call.id
            if not call_id:
                if last_call_id:
                    call_id = last_call_id
                else:
                    logger.warning(f"Tool call without id: {call}")
                    raise ValueError("Tool call must have a call_id")
            else:
                if call_id not in calls_index:
                    calls_index.append(call_id)
                last_call_id = call_id
            if call_id not in merged_calls:
                merged_calls[call_id] = call
            else:
                base_call = merged_calls[call_id]
                base_call.function.name = self._safe_concat(base_call.function.name, call.function.name)
                base_call.function.arguments = self._safe_concat(base_call.function.arguments, call.function.arguments)
        return list(map(lambda call_id: merged_calls.get(call_id), calls_index))
    
    def _safe_concat(self, a: Optional[str], b: Optional[str]) -> Optional[str]:
        """安全连接两个字符串，处理 None 情况"""
        if a is None:
            return b
        if b is None:
            return a
        return a + b
