# -*- coding: utf-8 -*-
import asyncio
import json
import signal
from decimal import Decimal
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
from typing import Dict
from mydba.app.config.database import database_config
from mydba.app.database.base_database import BaseDatabases
from mydba.app.tool.base_local_tool import BaseLocalTool, LocalTool
from mydba.common.global_settings import global_settings
from mydba.common.logger import logger

class DatabaseCache(BaseModel):
    database_map: Dict[str, BaseDatabases] = Field(default_factory=dict, description="key 为实例连接信息，value 为 database")
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock, description="缓存锁")
    is_register: bool = Field(default=False, description="是否注册清理函数")

    async def get_database(self, database_name: str) -> BaseDatabases:
        """
        根据库名获取缓存的 db 对象
        Args:
            database_name (str): 库名称。
        Returns:
            BaseDatabases: 数据库操作对象。
        Raises:
            Exception: 如果库信息不存在
        """
        database_info = database_config.get_database(database_name)
        if not database_info:
            logger.error(f"[mysql_exec] Database {database_name} not found")
            raise Exception(f"Database {database_name} not found")
        async with self.lock:
            if self.is_register is False:
                await self._register_cleanup()
            key = f"{database_info.host}_{database_info.port}_{database_info.user}_{database_info.database}"
            key = database_info.uri if database_info.uri else key
            database = self.database_map.get(key)
            if database:
                return database
            database = BaseDatabases.create_database(database_info=database_info)
            self.database_map[key] = database
            return database
    
    async def _register_cleanup(self) -> None:
        asyncio.create_task(self._cleanup())
        self.is_register = True
        
    async def _cleanup(self) -> None:
        # 等待退出
        while True:
            try:
                await asyncio.sleep(1)
            except BaseException:
                pass
            if global_settings.IS_EXIT:
                break
        # 清理缓存
        async with self.lock:
            for db in self.database_map.values():
                try:
                    await db.clean()
                except Exception as e:
                    pass
            self.database_map.clear()
        return
    
    class Config:
        arbitrary_types_allowed = True
_database_cache = DatabaseCache()

class MySQLExecution(BaseLocalTool, BaseModel):
    tool_name: str = LocalTool.MYSQL_EXECUTION.value
    description: str = "MySQL执行器，用于查询MySQL数据库"
    input_schema: Dict = {
        "type" : "object",
        "properties" : {
            "database" : {
                "type" : "string",
                "description": "Database name."
            },
            "sql" : {
                "type" : "string",
                "description": "SQL query."
            }
        },
        "required": ["database", "sql"]
    }
    
    async def execute(self, arguments: str) -> str:
        args = self._parse_arguments(arguments=arguments)
        database_name = args.get("database")
        sql = args.get("sql")
        if not database_name or not sql:
            raise ValueError("Need paramater(database & sql), when query sql in mysql.")
        db = await _database_cache.get_database(database_name)
        results = await db.query(sql=sql)
        return json.dumps(results, cls=CustomJSONEncoder, ensure_ascii=False)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        if isinstance(obj, timedelta):
            total_seconds = int(obj.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        if isinstance(obj, bytes):
            return obj.hex()
        if isinstance(obj, set):
            return repr(obj)
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)
