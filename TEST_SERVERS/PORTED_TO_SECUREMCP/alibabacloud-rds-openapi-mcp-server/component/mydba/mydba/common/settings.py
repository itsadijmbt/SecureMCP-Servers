# -*- coding: utf-8 -*-
import os

class Settings:
    """
    记录 MyDBA 启动时依赖的环境变量。
    Attributes:
        DEBUG (bool): 是否开启调试模式。
        LOG_DIR (str): 日志文件存放地址。
        LOG_NAME (str): 日志文件名。
        LOG_FILE_LEVEL (str): 文件日志等级。
        LOG_CONSOLE_LEVEL (str): 控制台日志等级。
    """
    DEBUG = os.getenv("MYDBA_DEBUG", "False") == "True"
    LOG_DIR = os.getenv("MYDBA_LOG_DIR", "/usr/local/mydba/logs")
    LOG_NAME = os.getenv("MYDBA_LOG_NAME", "mydba")
    LOG_FILE_LEVEL = os.getenv("MYDBA_LOG_FILE_LEVEL", "INFO")
    LOG_CONSOLE_LEVEL = os.getenv("MYDBA_LOG_CONSOLE_LEVEL", "CRITICAL")
settings = Settings()