# -*- coding: utf-8 -*-
import os

class Settings:
    """
    记录 MyDBA Agent 启动时依赖的环境变量。
    Attributes:
        CONFIG_FILE (str): 配置文件路径。
        CONFIG_DATABASE (str): 配置数据库 URI。
        REFRESH_INTERVAL (int): 缓存刷新间隔。
        MAX_STEPS (int): 执行步骤的最大次数。
        SECURITY_KEY (str): 数据加密 key，要求为 16 字节长度，保护数据安全，比如 mysql 的账密信息。
        API_KEY (str): 大模型的 api key。
        API_BASE_URL (str): 大模型的 base url。
        LLM_MODEL (str): 大模型名称。
        MAX_TOKENS (int): 大模型请求的最大 token 数量。
        TEMPERATURE (float): 大模型的温度。
    """
    CONFIG_FILE = os.getenv("MYDBA_CONFIG_FILE", "/usr/local/mydba/config_app.ini")
    CONFIG_DATABASE = os.getenv("MYDBA_CONFIG_DATABASE", "sqlite:///usr/local/mydba/sqlite_app.db")
    REFRESH_INTERVAL = int(os.getenv("MYDBA_REFRESH_INTERVAL", 60))
    MAX_STEPS = int(os.getenv("MYDBA_MAX_STEPS", 100))
    SECURITY_KEY = os.getenv("MYDBA_SECURITY_KEY", "")
    API_KEY = os.getenv("MYDBA_API_KEY", "")
    API_BASE_URL = os.getenv("MYDBA_API_BASE_URL", "")
    LLM_MODEL = os.getenv("MYDBA_LLM_MODEL", "")
    MAX_TOKENS = int(os.getenv("MYDBA_MAX_TOKENS", "1000"))
    TEMPERATURE = float(os.getenv("MYDBA_TEMPERATURE", "1.0"))
settings = Settings()