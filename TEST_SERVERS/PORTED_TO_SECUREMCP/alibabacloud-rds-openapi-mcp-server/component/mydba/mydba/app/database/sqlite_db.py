# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import asyncio
import aiosqlite
from aiosqlite.core import Connection
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional, Tuple
from mydba.app.database.base_database import BaseDatabases

class SqliteDatabase(BaseDatabases, BaseModel):
    async def query(self, sql: str, parameters: Optional[List[Any]]=None) -> Optional[List[Dict[str, Any]]]:
        async with aiosqlite.connect(self.database_info.uri) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, parameters) as cursor:
                results = []
                async for row in cursor:
                    results.append(dict(row))
                return results
    
    async def execute(self, sql: str, parameters: Optional[List[Any]]=None) -> int:
        affected_rows = 0
        async with aiosqlite.connect(self.database_info.uri) as db:
            if parameters and (isinstance(parameters[0], List) or isinstance(parameters[0], Tuple)):
                async with db.executemany(sql, parameters) as cursor:
                    affected_rows = cursor.rowcount
            else:
                async with db.execute(sql, parameters) as cursor:
                    affected_rows = cursor.rowcount
            await db.commit()
        return affected_rows
