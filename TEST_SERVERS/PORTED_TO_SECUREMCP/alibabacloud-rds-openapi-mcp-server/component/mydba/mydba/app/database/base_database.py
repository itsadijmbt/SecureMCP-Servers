# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Any, List, Dict, Optional
from mydba.app.config.database import DatabaseInfo, DatabaseType

class BaseDatabases(ABC, BaseModel):
    database_info: DatabaseInfo = Field(..., description="数据库信息")

    @abstractmethod
    async def query(self, sql: str, parameters: Optional[List[Any]]=None) -> Optional[List[Dict[str, Any]]]:
        """
        查询数据库
        Args:
            sql (str): 查询 sql。
            parameters (list): 绑定的参数。
        Returns:
            list: 查询结果。
        """
        return NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    async def execute(self, sql: str, parameters: Optional[List[Any]]=None) -> int:
        """
        变更数据库
        Args:
            sql (str): 变更 sql。
            parameters (list): 绑定的参数。
        Returns:
            int: 受影响行数。
        """
        return NotImplementedError("Subclasses must implement this method")
    
    async def clean(self) -> None:
        """资源清理，用于退出时释放资源，默认不做清理"""
        return
    
    @staticmethod
    def create_database(uri: Optional[str]=None, database_info: Optional[DatabaseInfo]=None) -> "BaseDatabases":
        if database_info is None:
            database_info = DatabaseInfo(uri=uri)
        database_type = database_info.type
        if database_type is None:
            if database_info.uri.startswith("sqlite://"):
                database_type = DatabaseType.SQLITE.value
            elif database_info.uri.startswith("jdbc:mysql:"):
                database_type = DatabaseType.MYSQL.value
            else:
                raise ValueError(f"database type unrecognized")
            database_info.type = database_type
        
        if database_type == DatabaseType.SQLITE.value:
            from mydba.app.database.sqlite_db import SqliteDatabase
            if database_info.uri and database_info.uri.startswith("sqlite://"):
                database_info.uri = database_info.uri[9:]
            return SqliteDatabase(database_info=database_info)
        elif database_type == DatabaseType.MYSQL.value:
            from mydba.app.database.mysql_db import MySQLDatabase
            return MySQLDatabase(database_info=database_info)
        raise ValueError(f"database type not supported")
