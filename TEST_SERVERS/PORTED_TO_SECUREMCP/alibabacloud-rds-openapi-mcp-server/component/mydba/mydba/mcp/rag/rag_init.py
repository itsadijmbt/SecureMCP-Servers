# -*- coding: utf-8 -*-
import aiosqlite
import argparse
import asyncio
import importlib.util
import os
import sys
import subprocess
from typing import Any, List, Dict, Optional
from mysql_utils import MysqlUtils
from settings import settings
from vector_store import VectorStore

def import_file_as_module(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# 动态导入加密模块
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../common'))
encryption = import_file_as_module(parent_dir + "/encryption.py", 'encryption')

def kill_process(file_name: str) -> None:
    """
    杀死指定文件名的进程
    """
    # 执行 ps 命令并过滤出包含对应文件名的行（排除 grep 自身）
    cmd = "ps aux | grep '" + file_name + "' | grep -v 'grep'"
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    lines = result.stdout.strip().splitlines()
    
    if len(lines) > 0:
        for line in lines:
            pid = line.split()[1]
            # 使用 kill -9 杀死进程
            try:
                print(f"Killing process with PID: {pid}")
                subprocess.run(f"kill -9 {pid}", shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Failed to kill process {pid}: {e}")

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None

async def prepare_rag_config(db: str, key: str, vectorstore: VectorStore) -> None:
    filename = os.path.join(settings.RAG_DATA_DIR, 'create_table_sql.md')
    if os.path.exists(filename):
        os.remove(filename)
    sql = 'SELECT * FROM db_instance'
    rows = await _query(uri=db[9:], sql=sql)
    if rows:
        for row in rows:
            if row['type'] == 'mysql':
                password = encryption.decrypt(key, row['password'])
                username=row['user']
                host=row['host']
                port=row['port']
                database=row['database']
                mysql_utils = MysqlUtils(host=host, port=str(port), username=username, password=password)
                mysql_utils.save_sql_file(filename=filename, database=database, overwrite=False)
        vectorstore.create_vectorstore_by_file(file=filename,
                                                vectorstore_name='table_struct')

async def _query(uri: str, sql: str, parameters: Optional[List[Any]]=None) -> Optional[List[Dict[str, Any]]]:
        async with aiosqlite.connect(uri) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(sql, parameters) as cursor:
                results = []
                async for row in cursor:
                    results.append(dict(row))
                return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MyDBA RAG CLI")
    
    # Define subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Subparser for create_table_struct_vectorstore
    create_table_parser = subparsers.add_parser('get-table-struct', help='Create table structure vectorstore')
    create_table_parser.add_argument('--host', required=False, default="127.0.0.1", help='MySQL host address')
    create_table_parser.add_argument('--port', required=False, default="3306", help='MySQL port number')
    create_table_parser.add_argument('--username', required=True, help='MySQL username')
    create_table_parser.add_argument('--password', required=True, help='MySQL password')
    create_table_parser.add_argument('--database', required=False, default=None, help='MySQL database name')
    create_table_parser.add_argument('--overwrite', action='store_true', help='overwrite the sql file')
    create_table_parser.add_argument('--restart_rag', action='store_true', help='restart the rag tool')
    create_table_parser.add_argument('--config_file', required=False, default="/usr/local/mydba/config_app.ini", help='Path to the configuration file')

    # Subparser for create_vectorstore
    create_vector_parser = subparsers.add_parser('create-vectorstore', help='Create a vectorstore from a file')
    create_vector_parser.add_argument('--file', required=True, help='Path to the input file')
    create_vector_parser.add_argument('--vectorstore_name', required=True, help='Name of the vectorstore directory')
    create_vector_parser.add_argument('--restart_rag', action='store_true', help='restart the rag tool')
    create_vector_parser.add_argument('--config_file', required=False, default="/usr/local/mydba/config_app.ini", help='Path to the configuration file')

    init_config_parser = subparsers.add_parser('init-config', help='Initialize the configuration')
    init_config_parser.add_argument('--config_file', required=False, default="/usr/local/mydba/config_app.ini", help='Path to the configuration file')
    init_config_parser.add_argument('--restart_rag', action='store_true', help='restart the rag tool')

    args = parser.parse_args()
    settings.load_config(args.config_file)
    vector_store = VectorStore(model_name=settings.RAG_EMBEDDING_MODEL, api_key=settings.RAG_API_KEY,
                               base_url=settings.RAG_API_BASE_URL, dir_path=settings.RAG_DATA_DIR)

    if args.command == 'get-table-struct':
        filename = os.path.join(settings.RAG_DATA_DIR, 'create_table_sql.md')
        mysql_utils = MysqlUtils(host=args.host, port=args.port, username=args.username, password=args.password)
        mysql_utils.save_sql_file(filename=filename, database=args.database, overwrite=args.overwrite)
        vector_store.create_vectorstore_by_file(
            file=filename,
            vectorstore_name='table_struct'
        )
        if args.restart_rag:
            kill_process('rag_server.py')
            run_cmd('nohup uv run rag_server.py >> /usr/local/mydba/logs/rag.log 2>&1 &')

    elif args.command == 'create-vectorstore':
        vector_store.create_vectorstore_by_file(
            file=args.file,
            vectorstore_name=args.vectorstore_name
        )
        if args.restart_rag:
            kill_process('rag_server.py')
            run_cmd('nohup uv run rag_server.py >> /usr/local/mydba/logs/rag.log 2>&1 &')
    elif args.command == 'init-config':
        asyncio.run(prepare_rag_config(db=settings.CONFIG_DATABASE, key=settings.SECURITY_KEY, vectorstore=vector_store))
        if args.restart_rag:
            kill_process('rag_server.py')
            run_cmd('nohup uv run rag_server.py >> /usr/local/mydba/logs/rag.log 2>&1 &')
    else:
        parser.print_help()