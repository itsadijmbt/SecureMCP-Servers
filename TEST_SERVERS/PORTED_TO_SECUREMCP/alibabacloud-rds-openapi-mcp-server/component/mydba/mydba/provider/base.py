# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field

class BaseProvider(ABC, BaseModel):
    name: str = Field(..., description="名称")
    description: str = Field(..., description="描述")
    
    @abstractmethod
    async def run(self) -> None:
        return NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_user_info(self) -> str:
        return NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_session(self) -> str:
        return NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def get_request_info(self) -> str:
        return NotImplementedError("Subclasses must implement this method")
    