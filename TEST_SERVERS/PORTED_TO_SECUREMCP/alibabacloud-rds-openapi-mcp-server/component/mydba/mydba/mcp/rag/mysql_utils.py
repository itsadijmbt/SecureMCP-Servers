# -*- coding: utf-8 -*-
import base64
import decimal
import pymysql, time
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

BASE_DATABASES = ["information_schema", "information_schema", "mysql", "performance_schema", "sys"]

class MysqlUtils(BaseModel):
    """连接 mysql 数据库并执行 sql 语句"""
    host: str = Field("127.0.0.1", description="mysql 主机地址")
    username: str = Field(..., description="mysql 用户名")
    password: str = Field(..., description="mysql 密码")
    port: str = Field("3306", description="mysql 端口号")

    def save_sql_file(self, filename: str, database: Optional[str] = None, overwrite: bool=False) -> None:
        """
        保存数据库的建表语句到本地文件
        Args:
            filename (str): 文件名。
        """
        res = self.get_tables(database)
        if overwrite:
            mode = 'w'
        else:
            mode = 'a'
        with open(filename, mode=mode) as f:
            for item in res:
                f.write(f"## Database: {item['db']}\n")
                f.write(f"{item['create_table_sql']};\n")

    def get_tables(self, database: Optional[str] = None) -> List[Dict[str, str]]:
        """
        获取数据库的建表语句
        Args:
            accountName (str): 用户名。
            accountPasword (str): 密码。
            port (str): 端口号。
        Returns:
            list: 数据库的建表语句。
        """
        res = []
        databases = self._show_databases(database)
        for db in databases:
            db_name = db['db']
            show_tables_sql = "select table_name from information_schema.tables where table_schema = '%s'" % db_name
            table_names = self._exec_sql(show_tables_sql)
            for table in table_names:
                table_name = table['table_name']
                show_create_table = "show create table %s.%s" % (db_name, table_name)
                create_table_sql = self._exec_sql(show_create_table)
                res.append({
                    "db": db_name,
                    "create_table_sql": create_table_sql[0]['create table']
                })

        return res

    def _get_conn(self) -> pymysql.connections.Connection:
        max_retries_count = 3  # 设置最大重试次数
        conn_retries_count = 0  # 初始重试次数
        while conn_retries_count <= max_retries_count:
            try:
                conn = pymysql.connect(
                    host=self.host,
                    port=int(self.port),
                    user=self.username,
                    password=self.password,
                    charset="utf8mb4",
                    cursorclass=pymysql.cursors.DictCursor,
                    connect_timeout=3,
                    read_timeout=5
                )
                return conn
            except Exception:
                conn_retries_count += 1
                time.sleep(3)
        raise Exception("Can't connect to MySQL server")

    def _show_databases(self, database: Optional[str] = None) -> List[Dict[str, str]]:
        conn = self._get_conn()
        where_clause = "'%s'" % ("','".join(BASE_DATABASES), )
        try:
            with conn.cursor() as cursor:
                if database is not None:
                    sql = ("SELECT SCHEMA_NAME,DEFAULT_CHARACTER_SET_NAME FROM information_schema.SCHEMATA "
                           "WHERE SCHEMA_NAME NOT IN (%s) AND SCHEMA_NAME='%s' ORDER BY SCHEMA_NAME") % (
                              where_clause, database)
                else:
                    sql = ("SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
                            "WHERE SCHEMA_NAME NOT IN (%s) ORDER BY SCHEMA_NAME") % where_clause
                cursor.execute(sql)
                rows = cursor.fetchall()
                databases = []
                for row in rows:
                    row_iter = iter(row.values())
                    databases.append({'db': next(row_iter)})
        finally:
            conn.close()
        return databases

    def _exec_sql(self, sql: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        try:
            resp_datas = []
            with conn.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
                if not res:
                    conn.commit()
                    return None
                for item in res:
                    resp_data = {}
                    for key in item.keys():
                        value = item[key]
                        if isinstance(value, (datetime, decimal.Decimal)):
                            value = str(value)
                        if isinstance(value, set):
                            value = list(value)
                        if isinstance(value, bytes):
                            value = base64.b64encode(value).decode('utf-8')
                        resp_data[key.lower()] = value
                    resp_datas.append(resp_data)
            return resp_datas
        finally:
            conn.close()
