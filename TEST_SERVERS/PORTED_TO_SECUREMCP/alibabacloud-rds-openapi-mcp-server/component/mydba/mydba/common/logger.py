# -*- coding: utf-8 -*-
import os
from datetime import datetime
from loguru import logger as _logger
from mydba.common.session import get_context
from mydba.common.settings import settings

def _custom_rotation(message, file):
    file = file.name
    file_size = os.path.getsize(file)
    current_date = datetime.now().strftime("%Y-%m-%d")
    # 如果文件超过 200 MB 或者日期发生变化，则轮转
    if file_size > 200 * 1024 * 1024 or not file.endswith(f"{current_date}.log"):
        return True
    return False

def _formatter(record):
    context = get_context()
    if context:
        record["extra"]["request_id"] = context.request_id
        record["extra"]["user_name"] = context.user_name
    else:
        record["extra"]["request_id"] = ""
        record["extra"]["user_name"] = ""
    format_str = "{time:YYYY-MM-DD HH:mm:ss}|{level}"
    if settings.DEBUG:
        format_str += "|{file}:{line}"
    format_str += "|{extra[user_name]}|{extra[request_id]}|"
    if record["message"] and isinstance(record["message"], str) and not record["message"].startswith("["):
        record["extra"]["file"] = record["file"].name.split('.')[0]
        format_str += "[{extra[file]}] "
    format_str += "{message}\n"
    return format_str

def init_logger(console_level: str, file_level: str, log_dir: str, log_name: str):
    """
    获取日志记录器
    Args:
        console_level (str): 控制台日志等级。
        file_level (str): 文件日志等级。
        log_dir (str): 日志文件存放地址。
        log_name (str): 日志文件名。
    Returns:
        logger: 日志记录器。
    """
    _logger.remove()
    _logger.add(
        log_dir + os.sep + log_name + "_{time:YYYY-MM-DD}.log",
        level=file_level,
        rotation=_custom_rotation,
        retention="7 days",
        enqueue=True,
        format=_formatter,
    )
    return _logger
logger = _logger
