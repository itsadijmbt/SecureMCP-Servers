# -*- coding: utf-8 -*-
import argparse
import os
import pwd
import sys
from pydantic import BaseModel, Field
from tenacity import RetryError
from typing import Optional, Tuple
from contextlib import asynccontextmanager
from mydba.app.agent.base import BaseAgent
from mydba.app.config.agent import agent_config
from mydba.app.config.settings import settings
from mydba.app.llm import LLM
from mydba.common import stream
from mydba.common.logger import logger
from mydba.common.session import get_context, set_context, reset_context, RequestContext
from mydba.provider.base import BaseProvider

class CommandLineProvider(BaseProvider, BaseModel):
    name: str = Field("CommandLine", description="名称")
    description: str = Field("通过命令行接入", description="描述")

    async def run(self) -> None:
        await self._welcome_message()
        async with self._get_context() as context:
            while True:
                query = await self._get_query()
                if query is None:
                    await stream.aprint("[A] 退出助手")
                    return
                logger.info(f"[cmd] get user query: {query}")
                agent = self._get_main_agent()
                context_memory = await agent.get_history_memory()
                has_error = True
                try:
                    content = await agent.run(query=query, context_memory=context_memory)
                    has_error = False
                except RetryError as re:
                    content = str(re.last_attempt.exception())
                except Exception as e:
                    content = str(e)
                if has_error:
                    await stream.aprint(f"[A] 查询异常: \n{content}")
                elif not context.detail_info:
                    await self._send_response(content)

    def get_user_info(self) -> str:
        return pwd.getpwuid(os.getuid()).pw_name

    def get_session(self) -> str:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-s",
            type=str,
            default="default",
            help="会话名称，默认: %(default)s"
        )
        args = parser.parse_args()
        return args.s
    
    def get_request_info(self) -> str:
        try:
            tty_name = os.ttyname(sys.stdin.fileno())
        except OSError:
            tty_name = 'unknown'
        tty_name = tty_name.split("/")[-1]
        sid = os.getsid(os.getpid())
        return f'{tty_name}_{sid}'
    
    def _get_main_agent(self) -> BaseAgent:
        main_agent_info = agent_config.get_main_agent()
        if main_agent_info is None:
            logger.error("[cmd] main agent not found")
            raise Exception("main agent not found")
        llm = LLM(model=settings.LLM_MODEL, base_url=settings.API_BASE_URL,
                  api_key=settings.API_KEY, max_tokens=settings.MAX_TOKENS,
                  temperature=settings.TEMPERATURE)
        return BaseAgent.create_agent(main_agent_info, llm)
    
    async def _get_query(self) -> Optional[str]:
        while True:
            await stream.aprint("[A] 输入指令:")
            try:
                query = await stream.ainput(">> ")
            except KeyboardInterrupt:
                query = None
            except BaseException:
                await stream.aprint()
                query = None
            retry, query = await self._handle_query(query)
            if not retry:
                return query
    
    async def _handle_query(self, query: Optional[str]) -> Tuple[bool, Optional[str]]:
        """处理查询
        Args:
            query (str): 用户输入的查询内容
        Returns:
            bool: 是否继续输入
            str: 处理后的查询内容
        """
        if not query.strip():
            return True, None
        if await self._handle_quit(query):
            return False, None
        if await self._handle_detail_info(query):
            return True, None
        if await self._handle_session(query):
            return True, None
        if await self._handle_help(query):
            return True, None
        return False, query.strip()
    
    async def _handle_quit(self, query: str) -> bool:
        query = query.strip().lower()
        if query in ["/exit", "/quit", "/e", "/q"]:
            return True
        return False
    
    async def _handle_detail_info(self, query: str) -> bool:
        context = get_context()
        query = query.strip().lower()
        if query in ["/i", "/info"]:
            context.detail_info = not context.detail_info
            if context.detail_info:
                await stream.aprint(f"开启详细信息")
            else:
                await stream.aprint(f"关闭详细信息")
            return True
        return False
    
    async def _handle_session(self, query: str) -> bool:
        query = query.strip().lower()
        if query.startswith('/s ') or query == '/s':
            items = query.split(" ")
            session = next((s for s in items[1:] if s), None)
            context = get_context()
            if session:
                await stream.aprint(f"切换会话: {session}")
                context.session = session
            else:
                usage = f"当前会话: {context.session}\n切换方法: /s [session_name]"
                await stream.aprint(f"{usage}")
            return True
        return False
    
    async def _handle_help(self, query: str) -> bool:
        query = query.strip().lower()
        if query in ["/help", "/h", "/?", "/？"]:
            await self._welcome_message()
            return True
        if query.startswith('/'):
            await stream.aprint("快捷命令有误")
            await stream.aprint("输入 [/h] 或 [/?] 查看帮助")
            await stream.aprint("输入 [/e] 或 [/q] 退出助手")
            await stream.aprint("输入 [/i] 关闭或打开详细信息")
            await stream.aprint("输入 [/s] 切换会话，默认 `default`")
            return True
        return False
    
    async def _welcome_message(self) -> None:
        functions = "、".join([agent.intent for agent in filter(lambda agent: not agent.is_main and not agent.is_default, agent_config.agent_list)])
        await stream.aprint("欢迎使用阿里云数据库智能助手 MyDBA")
        await stream.aprint(f"我能帮您：{functions}")
        await stream.aprint("快捷命令:")
        await stream.aprint("输入 [/h] 或 [/?] 查看帮助")
        await stream.aprint("输入 [/e] 或 [/q] 退出助手")
        await stream.aprint("输入 [/i] 关闭或打开详细信息")
        await stream.aprint("输入 [/s session] 切换会话，默认 `default`")

    async def _send_response(self, content: str) -> None:
        await stream.aprint(f"[A] 查询结果: \n{content}")
        pass

    @asynccontextmanager
    async def _get_context(self):
        context = RequestContext(request_id=self.get_request_info(),
                                 user_name=self.get_user_info(),
                                 session=self.get_session())
        token = set_context(context)
        yield context
        reset_context(token)
