# -*- coding: utf-8 -*-
import contextvars
from pydantic import BaseModel, Field
from datetime import datetime

class RequestContext(BaseModel):
    request_id: str = Field(..., description="请求 ID")
    user_name: str = Field(..., description="用户名")
    session: str = Field('default', description="会话 ID")
    detail_info: bool = Field(True, description="信息展示开关，默认展示详细信息")
    time: datetime = Field(default_factory=datetime.now, description="请求时间")
_request_context = contextvars.ContextVar('request_context', default=None)

def get_context() -> RequestContext:
    """
    获取当前请求上下文
    Returns:
        RequestContext: 当前请求上下文
    """
    return _request_context.get()

def set_context(context: RequestContext):
    """
    设置当前请求上下文
    Args:
        context (RequestContext): 要设置的请求上下文
    """
    return _request_context.set(context)

def reset_context(token: contextvars.Token):
    """
    重置当前请求上下文
    Args:
        token (contextvars.Token): 上下文 token，用于恢复上下文
    """
    _request_context.reset(token)