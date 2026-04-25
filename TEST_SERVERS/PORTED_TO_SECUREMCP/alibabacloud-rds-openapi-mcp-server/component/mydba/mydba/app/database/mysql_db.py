# -*- coding: utf-8 -*-
import asyncio
import aiomysql
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional, Tuple
from mydba.app.database.base_database import BaseDatabases

class MySQLDatabase(BaseDatabases, BaseModel):
    pool: Optional[Any] = Field(None, description="数据库连接池")
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock, description="连接池锁")

    async def query(self, sql: str, parameters: Optional[List[Any]]=None) -> Optional[List[Dict[str, Any]]]:
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # 连接检查
            await conn.ping()
            async with conn.cursor() as cursor:
                await cursor.execute(sql, parameters)
                return await cursor.fetchall()
    
    async def execute(self, sql: str, parameters: Optional[List[Any]]=None) -> int:
        affected_rows = 0
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # 连接检查
            await conn.ping()
            async with conn.cursor() as cursor:
                if parameters and (isinstance(parameters[0], List) or isinstance(parameters[0], Tuple)):
                    await cursor.executemany(sql, parameters)
                else:
                    await cursor.execute(sql, parameters)
                affected_rows = cursor.rowcount
        return affected_rows
    
    async def clean(self) -> None:
        if not self.pool:
            return
        async with self.lock:
            if not self.pool:
                return
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None
    
    async def _get_pool(self):
        if self.pool:
            return self.pool
        async with self.lock:
            if self.pool:
                return self.pool
            pool = await aiomysql.create_pool(
                host = self.database_info.host,
                port = 3306 if not self.database_info.port else self.database_info.port,
                user = self.database_info.user,
                password = self.database_info.password,
                charset = 'utf8mb4' if not self.database_info.charset else self.database_info.charset,
                db = self.database_info.database,
                autocommit = True,
                cursorclass = aiomysql.DictCursor,
                connect_timeout = 3,
                minsize = 1,
                maxsize = 3,
                pool_recycle = 3600
            )
            self.pool = pool
            return pool

    class Config:
        arbitrary_types_allowed = True
