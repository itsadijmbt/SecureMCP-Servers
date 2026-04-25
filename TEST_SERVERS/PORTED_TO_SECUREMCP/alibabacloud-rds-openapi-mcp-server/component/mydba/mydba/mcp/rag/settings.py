# -*- coding: utf-8 -*-
import configparser
import os

class Settings:
    """
    记录 RAG MCP 启动时依赖的环境变量。
    Attributes:
        CONFIG_FILE (str): 配置文件路径。
        CONFIG_DATABASE (str): 配置数据库 URI。
        SECURITY_KEY (str): 数据加密 key。
        RAG_API_KEY (str): 向量模型的 api key。
        RAG_API_BASE_URL (str): 向量模型的 base url。
        RAG_EMBEDDING_MODEL (str): 向量模型名称。
        RAG_DATA_DIR (str): 向量库数据存储目录。
    """
    CONFIG_FILE = os.getenv("MYDBA_CONFIG_FILE", "/usr/local/mydba/config_app.ini")
    CONFIG_DATABASE = os.getenv("MYDBA_CONFIG_DATABASE", "sqlite:///usr/local/mydba/sqlite_app.db")
    SECURITY_KEY = os.getenv("MYDBA_SECURITY_KEY", "")
    RAG_API_KEY = os.getenv("MYDBA_RAG_API_KEY", "")
    RAG_API_BASE_URL = os.getenv("MYDBA_RAG_API_BASE_URL", "")
    RAG_EMBEDDING_MODEL = os.getenv("MYDBA_RAG_EMBEDDING_MODEL", "")
    RAG_DATA_DIR = os.getenv("MYDBA_RAG_DATA_DIR", "/usr/local/mydba/vector_store")

    def load_config(self, config_file: str) -> None:
        config = configparser.ConfigParser()
        config.read(config_file)
        config_value = config.get('common', 'config_database')
        if config_value:
            self.CONFIG_DATABASE = config_value
        config_value = config.get('app', 'security_key')
        if config_value:
            self.SECURITY_KEY = config_value
        config_value = config.get('rag', 'api_key')
        if config_value:
            self.RAG_API_KEY = config_value
        config_value = config.get('rag', 'base_url')
        if config_value:
            self.RAG_API_BASE_URL = config_value
        config_value = config.get('rag', 'embedding')
        if config_value:
            self.RAG_EMBEDDING_MODEL = config_value
        config_value = config.get('rag', 'data_dir')
        if config_value:
            self.RAG_DATA_DIR = config_value
settings = Settings()