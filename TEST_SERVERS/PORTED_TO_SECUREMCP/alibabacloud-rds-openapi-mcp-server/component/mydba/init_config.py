# -*- coding: utf-8 -*-
import asyncio
import argparse
import configparser
import json
import os
import re
import textwrap
from argparse import Namespace
from string import Template
from typing import Any, Dict, List, Optional, Union
from mydba.app.config import config_manager
from mydba.app.config.agent import AgentMode
from mydba.app.config.mcp_tool import Transport
from mydba.app.config.settings import settings as app_settings
from mydba.app.database.base_database import BaseDatabases
from mydba.app.prompt import ask_table, chat, rds_agent, reflection, router
from mydba.common import encryption
from mydba.common.global_settings import global_settings

def get_agent_config() -> List[Dict]:
    """
    获取 agent 的配置信息，**编辑此部分内容，定制 agent**<br/>
    配置项中，prompts 为提示词模版，包含字段:
    1) system: 系统提示词模版，
    2) user: 用户提示词模版，在需要改写用户提示词的场景下使用，例如：REFLECTION 模式、ROUTER 模式，
    3) reflection_system: 反思提示词模版，仅在 REFLECTION 模式下使用，
    4) reflection_user: 反思提示词模版，仅在 REFLECTION 模式下使用，
    5) condition: 条件提示词(List)，在意图识别时，描述意图的约束条件，
    6) shot: 样本提示词(List)，在意图识别时，提供意图样本
    Returns:
        List[Dict]: Agent 的配置信息列表
    """
    main_agent = {
        "name": "main_agent",
        "mode": AgentMode.ROUTER,
        "intent": "识别意图",
        "intent_description": "识别用户的意图，并路由请求到相关 Agent",
        "prompts": {
            # 系统提示词模版
            "system": router.SYSTEM_PROMPT,
            # 用户提示词模版，意图识别时会改写用户指令
            "user": router.USER_PROMPT
        },
        "is_main": True,
        "is_default": False
    }
    rds_agent_ = {
        "name": "rds_agent",
        "mode": AgentMode.USING_TOOL,
        "intent": "阿里云RDS管理",
        "intent_description": "进行阿里云 RDS 数据库的管理运维，或者对阿里云 RDS 数据库进行问题诊断",
        "prompts": {
            # 系统提示词模版
            "system": rds_agent.SYSTEM_PROMPT,
            # 相关的意图约束条件，集成进意图识别提示词里，用于提升意图识别的准确度
            "condition": 
            [
                "用户明确希望进行阿里云 RDS 数据库相关的操作时，才能归类到阿里云RDS管理",
                "用户希望对阿里云 RDS 数据库进行问题诊断时，才能归类到阿里云RDS管理"
            ],
            # 相关的意图样例，集成进意图识别提示词里，用于提升意图识别的准确度
            "shot": 
            [
                "查下张北有多少RDS实例",
                "rm-8vb69ma75lpnug7hp 性能如何？",
                "创建一个阿里云 RDS 实例",
            ]
        },
        "mcps": {
            "allow": ["rds-openapi-mcp-server", "local-tool"]
        },
        "is_main": False,
        "is_default": False
    }
    ask_table_agent = {
        "name": "ask_table_agent",
        "mode": AgentMode.USING_TOOL,
        "intent": "数据查询",
        "intent_description": "帮助生成查询计划，执行数据库查询，最后完成数据的统计和分析",
        "prompts": {
            # 系统提示词模版
            "system": ask_table.SYSTEM_PROMPT,
            # 相关的意图约束条件，集成进意图识别提示词里，用于提升意图识别的准确度
            "condition": 
            [
                "用户希望进行数据计算和统计时，要归类到数据查询"
            ],
            # 相关的意图样例，集成进意图识别提示词里，用于提升意图识别的准确度
            "shot": 
            [
                "查询集群信息"
                "过去几天的售卖量",
                "有多少台主机"
            ]
        },
        "mcps": {
            "allow": ["rag", "local-tool"]
        },
        "is_main": False,
        "is_default": False
    }
    default_agent = {
        "name": "default_agent",
        "mode": AgentMode.CHAT,
        "intent": "默认",
        "intent_description": "无法匹配用户意图，使用此默认项",
        "prompts": {"system": chat.SYSTEM_PROMPT},
        "is_main": False,
        "is_default": True
    }
    agents = [main_agent, rds_agent_, ask_table_agent, default_agent]
    return agents

def get_mcp_config() -> List[Dict]:
    """获取 mcp 服务的配置信息，**编辑此部分内容，添加工具**"""
    # 目前 RDS MCP 采用代码的相对路径进行配置，如果不符合请手动调整
    base_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '..' + os.path.sep + '..' + os.path.sep + '..'
    aliyun_rds_dir = os.path.join(base_dir, 'alibabacloud-rds-openapi-mcp-server', 'src', 'alibabacloud_rds_openapi_mcp_server')
    mcp_aliyun_rds = {
        "name": "rds-openapi-mcp-server",
        "transport": Transport.STDIO,
        "description": "阿里云数据库 RDS 的服务。",
        "command": 'uv',
        "args": [
            "--directory",
            aliyun_rds_dir,
            "run",
            "server.py"
        ],
        "envs": {
            "FASTMCP_LOG_LEVEL": "CRITICAL",
            # 注意：此处的 $rds_access_id 和 $rds_access_key 会在命令行参数中传入
            # 需要在命令行中使用 --rds_access_id 和 --rds_access_key 参数传入
            "ALIBABA_CLOUD_ACCESS_KEY_ID": "$rds_access_id",
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "$rds_access_key",
        },
        "security": True # 启用加密保存，保护 ak 安全
    }
    mcp_rag = {
        "name": "rag",
        "transport": Transport.SSE,
        "description": "本地 RAG 知识库服务。",
        "server_uri": 'http://127.0.0.1:8006/sse'
    }
    return [mcp_aliyun_rds, mcp_rag]

def get_db_config() -> Optional[List[Dict]]:
    """
    获取数据库的配置信息。用于问询数据场景，包括：建设 RAG 知识库、执行数据库查询。
    **编辑此部分内容，增删数据库配置**
    """
    # test_db = {
    #     "type": "mysql",
    #     "host": "127.0.0.1",
    #     "port": 3306,
    #     "user": "test_user",
    #     "password": "123456",
    #     "charset": "utf8mb4",
    #     "database": "test_db"
    # }
    # dbs = [test_db, ]
    return []

async def prepare_agent_config(agents: List[Dict], db: BaseDatabases, reset: bool) -> None:
    """
    准备 agent 的配置信息
    Args:
        agents (List[Dict]): Agent 的配置信息列表
        db (BaseDatabases): 工程配置库实例
        reset (bool): 是否清空已存在的配置
    """
    sql_reset = 'DELETE FROM agent'
    sql_check = 'SELECT * FROM agent WHERE name=?'
    sql_update = 'UPDATE agent SET mode=?, intent=?, intent_description=?, prompts=?, mcps=?, is_main=?, is_default=? WHERE name=?'
    sql_insert = 'INSERT INTO agent (name, mode, intent, intent_description, prompts, mcps, is_main, is_default) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    if reset:
        await db.execute(sql_reset)
    for agent in agents:
        result = await db.query(sql_check, (agent["name"], ))
        if result:
            params = [
                agent["mode"].value,
                agent["intent"],
                agent["intent_description"],
                json.dumps(agent["prompts"], ensure_ascii=False) if agent.get("prompts") else None,
                json.dumps(agent["mcps"], ensure_ascii=False) if agent.get("mcps") else None,
                1 if agent["is_main"] else 0,
                1 if agent["is_default"] else 0,
                agent["name"]
            ]
            await db.execute(sql_update, params)
        else:
            params = [
                agent["name"],
                agent["mode"].value,
                agent["intent"],
                agent["intent_description"],
                json.dumps(agent["prompts"], ensure_ascii=False) if agent.get("prompts") else None,
                json.dumps(agent["mcps"], ensure_ascii=False) if agent.get("mcps") else None,
                1 if agent["is_main"] else 0,
                1 if agent["is_default"] else 0
            ]
            await db.execute(sql_insert, params)
    return

def handle_mcp_server_conf(
        options: Optional[Union[dict, list]],
        security: Optional[bool],
        args: Namespace) -> Optional[str]:
    """
    处理 mcp server 的 args、envs 配置项，利用命令行参数进行实例化，并根据需要进行加密保存
    Args:
        options (Optional[Union[dict, list]]): 待实例化的配置项
        security (Optional[bool]): 是否加密保存
        args (Namespace): 启动时传入的命令行参数，用于参数模版替换
    Returns:
        Optional[str]: 处理后的字符串
    """
    if not options:
        return None
    options_str = None
    if isinstance(options, dict):
        dict_options = {}
        for k, v in options.items():
            template = Template(v)
            v = template.safe_substitute(**args.__dict__)
            dict_options[k] = v
        options_str = json.dumps(dict_options, ensure_ascii=False)
    else:
        list_options = []
        for arg in options:
            template = Template(arg)
            arg = template.safe_substitute(**args.__dict__)
            list_options.append(arg)
        options_str = json.dumps(list_options, ensure_ascii=False)
    if security:
        options_str = encryption.encrypt(app_settings.SECURITY_KEY, options_str)
    return options_str

async def prepare_mcp_config(mcp_servers: List[Dict], db: BaseDatabases, reset: bool, args: Namespace) -> None:
    """
    准备 mcp server 的配置信息
    Args:
        mcp_servers (List[Dict]): mcp server 的配置信息列表
        db (BaseDatabases): 工程配置库实例
        reset (bool): 是否清空已存在的配置
        args (Namespace): 启动时传入的命令行参数，用于参数模版替换
    """
    sql_reset = 'DELETE FROM mcp'
    sql_check = 'SELECT * FROM mcp WHERE name=?'
    sql_update = 'UPDATE mcp SET transport=?, description=?, server_uri=?, command=?, args=?, envs=? WHERE name=?'
    sql_insert = 'INSERT INTO mcp (name, transport, description, server_uri, command, args, envs) VALUES (?, ?, ?, ?, ?, ?, ?)'
    if reset:
        await db.execute(sql_reset)
    for server in mcp_servers:
        server_args = handle_mcp_server_conf(server.get("args"), server.get("security"), args)
        server_envs = handle_mcp_server_conf(server.get("envs"), server.get("security"), args)
        result = await db.query(sql_check, (server["name"], ))
        if result:
            params = [
                server["transport"].value,
                server["description"],
                server.get("server_uri"),
                server.get("command"),
                server_args if server_args else None,
                server_envs if server_envs else None,
                server["name"]
            ]
            await db.execute(sql_update, params)
        else:
            params = [
                server["name"],
                server["transport"].value,
                server["description"],
                server.get("server_uri"),
                server.get("command"),
                server_args if server_args else None,
                server_envs if server_envs else None
            ]
            await db.execute(sql_insert, params)
    return

async def prepare_db_config(db_configs: Optional[List[Dict]], db: BaseDatabases, reset: bool) -> None:
    """
    准备数据库的配置信息
    Args:
        db_configs (Optional[List[Dict]]): 数据库的配置信息列表
        db (BaseDatabases): 工程配置库实例
        reset (bool): 是否清空已存在的配置
    """
    sql_reset = 'DELETE FROM db_instance'
    sql_check = 'SELECT * FROM db_instance WHERE `database`=?'
    sql_update = 'UPDATE db_instance SET type=?, uri=?, host=?, port=?, user=?, password=?, charset=? WHERE `database`=?'
    sql_insert = 'INSERT INTO db_instance (type, uri, host, port, user, password, charset, `database`) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
    if reset:
        await db.execute(sql_reset)
    if not db_configs:
        return
    for db_info in db_configs:
        result = await db.query(sql_check, (db_info["database"], ))
        password = encryption.encrypt(app_settings.SECURITY_KEY, db_info["password"])
        params = [
            db_info.get("type"),
            db_info.get("uri"),
            db_info.get("host"),
            db_info.get("port"),
            db_info.get("user"),
            password,
            db_info.get("charset"),
            db_info.get("database")
        ]
        if result:
            await db.execute(sql_update, params)
        else:
            await db.execute(sql_insert, params)
    return

async def init_config(args: Namespace) -> None:
    """
    初始化工程配置
    Args:
        args (Namespace): 命令行参数
    """
    await config_manager.init_config(database_uri=app_settings.CONFIG_DATABASE)
    db = BaseDatabases.create_database(uri=app_settings.CONFIG_DATABASE)

    agents = get_agent_config()
    await prepare_agent_config(agents=agents, db=db, reset=args.reset)

    mcp_servers = get_mcp_config()
    await prepare_mcp_config(mcp_servers=mcp_servers, db=db, reset=args.reset, args=args)

    db_configs = get_db_config()
    await prepare_db_config(db_configs=db_configs, db=db, reset=args.reset)

async def add_db_config(args: Namespace) -> None:
    """
    添加 db 配置
    Args:
        args (Namespace): 命令行参数
    """
    await config_manager.init_config(database_uri=app_settings.CONFIG_DATABASE)
    db = BaseDatabases.create_database(uri=app_settings.CONFIG_DATABASE)
    info = parse_db_info(args.db_info)
    db_info = {
        "type": info[0],
        "uri": info[1] if info[1] else None,
        "host": info[2] if info[2] else None,
        "port": int(info[3]) if info[3] else None,
        "user": info[4] if info[4] else None,
        "password": info[5] if info[5] else None,
        "charset": info[6] if info[6] else None,
        "database": info[7] if info[7] else None
    }
    await prepare_db_config(db_configs=[db_info], db=db, reset=False)

def parse_db_info(db_info: str) -> list:
    """
    解析 db_info 字符串
    Args:
        db_info (str): db_info 字符串，格式为 type##uri##host##port##user##password##charset##database
    Returns:
        list: 解析后的信息列表，包含 8 个元素
    """
    info = args.db_info.split('##')
    if len(info) != 8:
        raise Exception("db config invalid")
    info[5] = decrypt(info[5])
    return info

def decrypt(data: str) -> str:
    """
    对于部分敏感信息，传入时有可能做了加密处理，这里统一进行下解密处理
    例如：阿里云账号的 access_id 和 access_key，以及数据库的密码等。
    Args:
        data (str): 待解密的数据
    Returns:
        str: 解密后的数据，如果解密失败或不符合加密格式，则返回原数据
    """
    if not data or not bool(re.fullmatch(r'^[0-9a-fA-F]+$', data)) or len(data) <= 32:
        return data
    try:
        return encryption.decrypt(app_settings.SECURITY_KEY, data)
    except Exception as e:
        return data

def decrypt_args(args: Namespace) -> None:
    """
    解密命令行参数中的敏感信息
    Args:
        args (Namespace): 命令行参数
    """
    if hasattr(args, 'rds_access_id'):
        args.rds_access_id = decrypt(args.rds_access_id)
    if hasattr(args, 'rds_access_key'):
        args.rds_access_key = decrypt(args.rds_access_key)

async def main(args) -> None:
    """
    主函数，处理命令行参数并执行相应的操作
    Args:
        args (Namespace): 命令行参数
    """
    decrypt_args(args)
    error = False
    try:
        if args.command == 'init-project':
            await init_config(args)
        elif args.command == 'add-db':
            await add_db_config(args)
        else:
            raise Exception("command not support")
        global_settings.IS_EXIT = True
    except configparser.NoOptionError as noe:
        print(f"lost config option, error: {str(noe)}")
        error = True
    except Exception as e:
        print(f"something wrong, error: {str(e)}")
        error = True
    if error:
        print(f"{args.command} failed")
    else:
        print(f"{args.command} successfully")

def parse_arguments() -> Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="导入 agent、mcp、db_instance 配置",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    init_proj_parser = subparsers.add_parser('init-project', help='初始化工程配置')
    init_proj_parser.add_argument(
        "--config_file",
        type=str,
        default="/usr/local/mydba/config_app.ini",
        help="配置文件路径，默认: %(default)s"
    )
    init_proj_parser.add_argument(
        "--reset",
        action='store_true',
        default=False,
        help="清除已存在的配置内容"
    )
    # 以下参数为 mcp server 依赖的环境配置信息
    init_proj_parser.add_argument(
        "--rds_access_id",
        type=str,
        default='',
        help="阿里云 access_id，用于阿里云 RDS 管理功能"
    )
    init_proj_parser.add_argument(
        "--rds_access_key",
        type=str,
        default='',
        help="阿里云 access_key，用于阿里云 RDS 管理功能"
    )

    add_db_parser = subparsers.add_parser('add-db', help='添加 DB 配置，用于问询数据')
    add_db_parser.add_argument(
        "--config_file",
        type=str,
        default="/usr/local/mydba/config_app.ini",
        help="配置文件路径，默认: %(default)s"
    )
    add_db_parser.add_argument(
        "--db_info",
        type=str,
        required=True,
        help=textwrap.dedent(
            """\
            添加一个 db 配置，用于问询数据功能
            格式: type##uri##host##port##user##password##charset##database
            例如: mysql####127.0.0.1##3306##test_user##123456##utf8mb4##test_db"""
        )
    )
    return parser.parse_args()

def print_args(args: Namespace) -> None:
    """打印命令行参数"""
    print(f"args:")
    for key, value in args.__dict__.items():
        # 过滤敏感信息
        if key.startswith('rds_access'):
            value = mask_info(value)
        if key == 'db_info':
            v = value.split('##')
            v[5] = mask_info(v[5])
            value = '##'.join(v)
        # 打印参数
        if isinstance(value, str):
            print(f"  {key}: {value}")
        elif isinstance(value, list):
            print(f"  {key}:")
            for item in value:
                print(f"    - {item}")
        else:
            print(f"  {key}: {value}")

def mask_info(info: Optional[str]) -> Optional[str]:
    if not info:
        return info
    if len(info) > 4:
        return info[:2] + '*' * (len(info) - 4) + info[-2:]
    return info[:1]+ "**"

if __name__ == "__main__":
    args = parse_arguments()
    print_args(args)
    if not os.path.isfile(args.config_file):
        raise Exception("conf_file not exist")
    config_manager.load_from_conf(args.config_file)
    asyncio.run(main(args), debug=False)
