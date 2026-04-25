# -*- coding: utf-8 -*-
import json
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Optional

class DatabaseType(str, Enum):
    """数据库类型"""
    SQLITE = "sqlite"
    MYSQL = "mysql"
DATABASE_TYPE_VALUES = tuple(type.value for type in DatabaseType)
DATABASE_TYPE_TYPE = Literal[DATABASE_TYPE_VALUES]

class DatabaseInfo(BaseModel):
    type: Optional[DATABASE_TYPE_TYPE] = Field(None, description="数据库类型") # type: ignore
    uri: Optional[str] = Field(None, description="db 连接串")
    host: Optional[str] = Field(None, description="db 主机")
    port: Optional[int] = Field(None, description="db 端口")
    user: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    charset: Optional[str] = Field(None, description="db 字符集")
    database: Optional[str] = Field(None, description="库名称")
    def __repr__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)

class DatabaseConfig(BaseModel):
    info_map: Dict[str, DatabaseInfo] = Field(default_factory=dict, description="库名到实例信息的映射")

    def add_database(self, database: str, type: Optional[str] = None, uri: Optional[str] = None,
                     host: Optional[str] = None, port: Optional[int] = None, user: Optional[str] = None,
                     password: Optional[str] = None, charset: Optional[str] = None) -> None:
        """
        添加库信息。
        Args:
            database (str): 库名称。
            type (str): 数据库类型。
            uri (str): db 连接串。
            host (str): db 主机。
            port (int): db 端口。
            user (str): 用户名。
            password (str): 密码。
            charset (str): db 字符集。
        """
        if database in self.info_map:
            raise ValueError(f"Database {database} already exists.")
        database_info = DatabaseInfo(**{
            "type": type,
            "uri": uri,
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "charset": charset,
            "database": database
        })
        self.info_map[database.lower()] = database_info
    
    def get_database(self, database: str) -> Optional[DatabaseInfo]:
        """
        根据库名获取库信息。
        Args:
            database (str): 库名称。
        Returns:
            DatabaseInfo: 库信息。
        """
        return self.info_map.get(database.lower())
database_config = DatabaseConfig()
