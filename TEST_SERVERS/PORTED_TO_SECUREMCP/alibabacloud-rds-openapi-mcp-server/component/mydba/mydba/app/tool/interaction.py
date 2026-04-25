# -*- coding: utf-8 -*-
from mydba.common import stream
from typing import Dict
from pydantic import BaseModel
from mydba.app.tool.base_local_tool import BaseLocalTool, LocalTool
from mydba.common.logger import logger

class Interaction(BaseLocalTool, BaseModel):
    tool_name: str = LocalTool.INTERACTION.value
    description: str = "命令行交互工具，可快速与用户沟通，引导用户澄清需求"
    input_schema: Dict = {
        "type" : "object",
        "properties" : {
            "message" : {
                "type" : "string",
                "description": "A prompt message used to guide the user during an interaction."
            }
        },
        "required": ["message"]
    }

    async def execute(self, arguments: str) -> str:
        args = self._parse_arguments(arguments=arguments)
        if not args.get("message"):
            raise ValueError("When interacting with the user, it is necessary to display a prompt message.")
        await stream.aprint(f"[A] {args['message']}")
        response = await stream.ainput(">> ")
        return response