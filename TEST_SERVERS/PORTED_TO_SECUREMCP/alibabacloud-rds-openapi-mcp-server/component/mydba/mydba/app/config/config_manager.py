# -*- coding: utf-8 -*-
import configparser
from mydba.app.config.agent import agent_config
from mydba.app.config.database import database_config
from mydba.app.config.mcp_tool import mcp_config
from mydba.app.config.settings import settings as app_settings
from mydba.app.database.base_database import BaseDatabases
from mydba.common import encryption
from mydba.common.settings import settings as common_settings

async def load_config(conf_file: str='/usr/local/mydba/config_app.ini') -> None:
    """
    加载 MyDBA 配置信息，项目配置分为以下几类：
    1. 日志: 使用文件管理配置 (LOG_DIR, LOG_NAME, LOG_FILE_LEVEL)
    2. 模型: 使用文件管理配置 (API_KEY, API_BASE_URL, LLM_MODEL, MAX_TOKENS, TEMPERATURE)
    3. App: 使用文件管理配置 (REFRESH_INTERVAL, MAX_STEPS, SECURITY_KEY)
    4. Mcp: 使用 sqlite 管理配置 (McpConfig)
    5. Agent: 使用 sqlite 管理配置 (AgentConfig)
    6. Database: 使用 sqlite 管理配置 (DatabaseConfig)
    7. 其它: 使用文件管理配置 (DEBUG, CONFIG_DATABASE)
    Args:
        conf_file (str): 配置文件路径。
    """
    # 支持从配置文件获取工程配置
    load_from_conf(conf_file)

    if not app_settings.SECURITY_KEY:
        raise Exception("[config] config invalid, lost security key, please set it using config_app.ini or env(MYDBA_SECURITY_KEY)")

    # 从 db 读取 agent、mcp 配置
    await _load_from_db(database_uri=app_settings.CONFIG_DATABASE, security_key=app_settings.SECURITY_KEY)

async def init_config(database_uri: str) -> None:
    """
    初始化 MyDBA 配置，这里仅初始化表结构
    Args:
        database_uri (str): 数据库连接 URI。
    """
    db = BaseDatabases.create_database(uri=database_uri)
    # Agent 配置表
    sql = """
        CREATE TABLE IF NOT EXISTS agent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,                            -- Agent 名称
            mode TEXT NOT NULL,                            -- Agent 模式 (参考类 AgentMode)
            intent TEXT,                                   -- 意图名称, 用于意图识别 (除主 Agent 外, 都需要配置此信息)
            intent_description TEXT,                       -- 意图描述, 用于帮助 LLM 识别意图 (除主 Agent 外, 都需要配置此信息)
            prompts TEXT,                                  -- Agent 提示词 (JSON 格式) (可为空)
            mcps TEXT,                                     -- 绑定的 mcp 服务 (JSON 格式) (可为空)
            is_main INTEGER DEFAULT 0,                     -- 是否为主 Agent
            is_default INTEGER DEFAULT 0                   -- 是否为默认 Agent
        );
    """
    await db.execute(sql)
    sql = "CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_agent_name ON agent(name);"
    await db.execute(sql)

    # mcp 配置表
    sql = """
        CREATE TABLE IF NOT EXISTS mcp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,                     -- mcp 服务名称（全局唯一）
            transport TEXT NOT NULL DEFAULT 'sse',         -- mcp server 的传输协议
            description TEXT,                              -- 服务描述 (可为空)
            server_uri TEXT,                               -- mcp 服务器 URI (可为空)
            command TEXT,                                  -- mcp server 启动命令 (可为空)
            args TEXT,                                     -- mcp server 启动参数 (JSON 字符串格式，可为空)
            envs TEXT                                      -- mcp server 启动依赖的环境变量 (JSON 字符串格式，可为空)
        );
    """
    await db.execute(sql)
    sql = "CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_mcp_name ON mcp(name);"
    await db.execute(sql)

    # 数据库实例配置表
    sql = """
        CREATE TABLE IF NOT EXISTS db_instance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,          -- 主键，自增
            type TEXT DEFAULT NULL,                        -- 数据库类型，使用 TEXT 类型
            uri TEXT DEFAULT NULL,                         -- db 连接串
            host TEXT DEFAULT NULL,                        -- db 主机
            port INTEGER DEFAULT NULL,                     -- db 端口
            user TEXT DEFAULT NULL,                        -- 用户名
            password TEXT DEFAULT NULL,                    -- 密码
            charset TEXT DEFAULT NULL,                     -- db 字符集
            `database` TEXT DEFAULT NULL                   -- 库名称
        );
    """
    await db.execute(sql)
    sql = "CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_db_name ON db_instance(`database`);"
    await db.execute(sql)

    # memory 表
    sql = """
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT NOT NULL,                            -- 记录时间
            request_id TEXT NOT NULL,                      -- 请求标识
            user_name TEXT NOT NULL,                       -- 用户标识
            session TEXT NOT NULL,                         -- 会话标识
            agent_name TEXT NOT NULL,                      -- agent 标识
            system_content TEXT,                           -- 系统指令内容 (可为空)
            user_content TEXT,                             -- 用户查询内容 (可为空)
            assistant_content TEXT,                        -- 大模型返回的内容 (可为空)
            assistant_tool_calls TEXT,                     -- 大模型返回的工具调用列表，JSON 格式 (可为空)
            tool_contents TEXT                             -- 工具调用返回的内容列表，JSON 格式 (可为空)
        );
    """
    await db.execute(sql)
    sql = "CREATE INDEX IF NOT EXISTS idx_memory_username_agenname_time ON memory(user_name, session, agent_name, time);"
    await db.execute(sql)
    await db.clean()

def load_from_conf(conf_file: str) -> None:
    config = configparser.ConfigParser()
    config.read(conf_file)
    # 1. 日志配置 (LOG_DIR, LOG_NAME, LOG_FILE_LEVEL)
    config_value = config.get('log', 'dir')
    if config_value:
        common_settings.LOG_DIR = config_value
    config_value = config.get('log', 'name')
    if config_value:
        common_settings.LOG_NAME = config_value
    config_value = config.get('log', 'file_level')
    if config_value:
        common_settings.LOG_FILE_LEVEL = config_value
    # 2. 模型配置 (API_KEY, API_BASE_URL, LLM_MODEL, MAX_TOKENS, TEMPERATURE)
    config_value = config.get('model', 'api_key')
    if config_value:
        app_settings.API_KEY = config_value
    config_value = config.get('model', 'base_url')
    if config_value:
        app_settings.API_BASE_URL = config_value
    config_value = config.get('model', 'model')
    if config_value:
        app_settings.LLM_MODEL = config_value
    config_value = config.get('model', 'max_tokens')
    if config_value:
        app_settings.MAX_TOKENS = int(config_value)
    config_value = config.get('model', 'temperature')
    if config_value:
        app_settings.TEMPERATURE = float(config_value)
    # 3. App 配置 (REFRESH_INTERVAL, MAX_STEPS, SECURITY_KEY)
    config_value = config.get('app', 'refresh_interval')
    if config_value:
        app_settings.REFRESH_INTERVAL = int(config_value)
    config_value = config.get('app', 'max_steps')
    if config_value:
        app_settings.MAX_STEPS = int(config_value)
    security_key = config.get('app', 'security_key')
    if security_key:
        app_settings.SECURITY_KEY = security_key
    # 4. 其它配置 (DEBUG, CONFIG_DATABASE)
    config_value = config.get('common', 'debug')
    if config_value:
        common_settings.DEBUG = config_value == 'True'
    config_value = config.get('common', 'config_database')
    if config_value:
        app_settings.CONFIG_DATABASE = config_value
    
async def _load_from_db(database_uri: str, security_key: str) -> None:
    db = BaseDatabases.create_database(uri=database_uri)
    try:
        # 1. Agent 配置
        sql = 'SELECT * FROM agent'
        rows = await db.query(sql=sql)
        if not rows:
            raise Exception("Lost agent config in DB")
        for row in rows:
            agent_config.add_agent(name = row['name'],
                                   mode = row['mode'],
                                   intent = row['intent'],
                                   intent_description = row['intent_description'],
                                   prompts = row['prompts'],
                                   mcps = row['mcps'],
                                   is_main = row['is_main']==1,
                                   is_default = row['is_default']==1)
        
        # 2. mcp server 配置
        sql = 'SELECT * FROM mcp'
        rows = await db.query(sql=sql)
        if rows:
            for row in rows:
                args = row['args']
                if args and not args.startswith('['):
                    try:
                        args = encryption.decrypt(security_key, args)
                    except Exception:
                        pass
                envs = row['envs']
                if envs and not envs.startswith('{'):
                    try:
                        envs = encryption.decrypt(security_key, envs)
                    except Exception:
                        pass
                mcp_config.add_mcp(name = row['name'],
                                   transport = row['transport'],
                                   description = row['description'],
                                   server_uri = row['server_uri'],
                                   command = row['command'],
                                   args = args,
                                   envs = envs)
        
        # 3. mysql 信息配置
        sql = 'SELECT * FROM db_instance'
        rows = await db.query(sql=sql)
        if rows:
            for row in rows:
                password = encryption.decrypt(security_key, row['password'])
                database_config.add_database(database=row['database'], type=row['type'], uri=row['uri'],
                                             host=row['host'], port=row['port'], user=row['user'],
                                             password=password, charset=row['charset'])
    finally:
        await db.clean()
