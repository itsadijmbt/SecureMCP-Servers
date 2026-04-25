#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import uuid

from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_openapi import utils_models as open_api_util_models
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_util.models import RuntimeOptions

markdown_code_languages = [
    # 编程语言
    "python",
    "javascript",
    "js",
    "typescript",
    "ts",
    "java",
    "c",
    "cpp",
    "csharp",
    "cs",
    "go",
    "golang",
    "rust",
    "ruby",
    "php",
    "swift",
    "kotlin",
    "scala",
    "r",
    "perl",
    "haskell",
    "lua",
    "matlab",
    "fortran",
    "objective-c",
    "objc",
    "dart",
    "elixir",
    "erlang",
    "clojure",
    "fsharp",
    "vbnet",
    "assembly",
    "asm",

    # 脚本与配置
    "bash",
    "shell",
    "zsh",
    "powershell",
    "ps1",
    "batch",
    "bat",
    "cmd",

    # 标记与数据格式
    "html",
    "xml",
    "svg",
    "mathml",
    "xhtml",
    "markdown",
    "md",
    "json",
    "yaml",
    "yml",
    "toml",
    "ini",
    "properties",
    "dotenv",
    "env",

    # 样式表
    "css",
    "scss",
    "sass",
    "less",
    "stylus",

    # 模板与 DSL
    "jinja2",
    "django",
    "liquid",
    "handlebars",
    "hbs",
    "mustache",
    "twig",
    "pug",
    "jade",

    # 数据库与查询语言
    "sql",
    "mysql",
    "pgsql",
    "plsql",
    "sqlite",
    "cql",

    # 其他常用
    "diff",
    "patch",
    "makefile",
    "dockerfile",
    "docker",
    "nginx",
    "apache",
    "http",
    "graphql",
    "protobuf",
    "terraform",
    "hcl",
    "log",
    "plaintext",
    "text",
    "ascii",
]


class ChatMessageParams(open_api_util_models.Params):
    def __init__(self):
        super().__init__()
        self.action = 'ChatMessages'
        self.version = '2025-05-07'
        self.protocol = 'HTTPS'
        self.method = 'POST'


class ChatMessagesStopParams(open_api_util_models.Params):
    def __init__(self):
        super().__init__()
        self.action = 'ChatMessagesTaskStop'
        self.version = '2025-05-07'
        self.protocol = 'HTTPS'
        self.method = 'POST'


class BaseEvent:
    def __init__(self, task_id, conversion_id):
        self.task_id = task_id
        self.conversion_id = conversion_id


class MessageEvent(BaseEvent):
    def __init__(self, task_id, conversion_id, text):
        super().__init__(task_id, conversion_id)
        self.text = text


class ToolCallStart(BaseEvent):
    def __init__(self, task_id, conversion_id, title, text, tool_call_id):
        super().__init__(task_id, conversion_id)
        self.title = title
        self.text = text
        self.tool_call_id = f"t{tool_call_id.split('-')[-1]}"


class ToolCallPending(BaseEvent):
    def __init__(self, task_id, conversion_id, title, text, tool_call_id):
        super().__init__(task_id, conversion_id)
        self.title = title
        self.text = text
        self.tool_call_id = f"t{tool_call_id.split('-')[-1]}"


class ToolCallEnd(BaseEvent):
    def __init__(self, task_id, conversion_id, title, text, tool_call_id):
        super().__init__(task_id, conversion_id)
        self.title = title
        self.text = text
        self.tool_call_id = f"t{tool_call_id.split('-')[-1]}"


class DocumentEvent(BaseEvent):
    def __init__(self, task_id, conversion_id, title, text):
        super().__init__(task_id, conversion_id)
        self.document_id = f"d{str(uuid.uuid4()).split('-')[-1]}"
        self.title = title
        self.text = text


class SubTaskStartEvent(BaseEvent):
    def __init__(self, task_id, conversion_id, title, text):
        super().__init__(task_id, conversion_id)
        self.subtask_id = f"s{title.replace('_', '')}".lower()[:20]
        self.title = title
        self.text = text


class SubTaskEndEvent(BaseEvent):
    def __init__(self, task_id, conversion_id, title, text):
        super().__init__(task_id, conversion_id)
        self.subtask_id = f"s{title.replace('_', '')}".lower()[:20]
        self.title = title
        self.text = text


class ChartEvent(BaseEvent):
    def __init__(self, task_id, conversion_id, title, x_field, y_field, data):
        super().__init__(task_id, conversion_id)
        self.title = title
        self.x_field = x_field
        self.y_field = y_field
        self.data = data


class RdsCopilot:
    def __init__(self):

        # 初始化OpenAPI配置
        config = open_api_models.Config(
            access_key_id=os.getenv('ACCESS_KEY_ID'),
            access_key_secret=os.getenv('ACCESS_SECRET'),
            protocol='https',
            region_id='cn-hangzhou',
            endpoint='rdsai.aliyuncs.com',
            read_timeout=600_000,
            connect_timeout=10_000
        )
        self.app_id = 'app-iBuGU1VxEY42zrQRQfNAn3oj'
        self.client = OpenApiClient(config)
        self.code_mask_start = '```'
        self.code_mask_end = '```\n'

    def _emit_tool_call_event(self, task_id, conversion_id, payload):
        """根据 tool_call 事件的 status 返回对应事件类型（EventMode=separate 时 payload 为单条事件体）"""
        tool_call_name = payload.get('tool_call_name') or payload.get('ToolCallName', '')
        status = payload.get('status') or payload.get('Status', '')
        tool_call_id = payload.get('tool_call_id') or payload.get('ToolCallId', '')
        text = json.dumps(payload, ensure_ascii=False)
        if status == 'start':
            return ToolCallStart(task_id, conversion_id, title=tool_call_name, text=text, tool_call_id=tool_call_id)
        if status == 'pending':
            return ToolCallPending(task_id, conversion_id, title=tool_call_name, text=text, tool_call_id=tool_call_id)
        return ToolCallEnd(task_id, conversion_id, title=tool_call_name, text=text, tool_call_id=tool_call_id)

    def stop_task(self, task_id):
        # 发送停止请求
        stop_query_params = {
            'TaskId': task_id,
            'ApiId': self.app_id
        }
        stop_request = open_api_util_models.OpenApiRequest(query=stop_query_params)
        response = self.client.do_request(
            ChatMessagesStopParams(),
            stop_request,
            RuntimeOptions()
        )

    def chat(self, query, conversion_id=''):
        """流式对话，使用 EventMode=separate：message / tool_call / doc 等各自独立事件，便于渲染与推送。
        
        Args:
            query: 用户查询文本
            conversion_id: 对话 ID，用于保持上下文
            
        Yields:
            各种事件对象（MessageEvent, ToolCallStart, ToolCallPending, ToolCallEnd, DocumentEvent）
            
        Returns:
            str: 最终的 conversation_id（注意：API 返回的是 ConversationId 或 ConversionId）
        """
        task_id = ""
        final_conversion_id = conversion_id
        try:
            query_params = {
                'Query': query,
                'ConversationId': conversion_id,
                'ApiId': self.app_id,
                'EventMode': 'separate',
            }
            chat_message_params = ChatMessageParams()
            chat_message_request = open_api_util_models.OpenApiRequest(query=query_params)
            responses = self.client.call_sseapi(chat_message_params, chat_message_request, RuntimeOptions())

            for response in responses:
                response_body = json.loads(response.event.data)
                if 'TaskId' in response_body:
                    task_id = response_body['TaskId']
                if 'ConversationId' in response_body:
                    final_conversion_id = response_body['ConversationId']
                elif 'ConversionId' in response_body:
                    final_conversion_id = response_body['ConversionId']

                event_type = (response_body.get('Event') or response_body.get('event') or '').strip().lower()
                # 打印每条 Copilot 响应，便于排查 tool_call 未推动卡片的原因
                if event_type == 'message':
                    answer_preview = (response_body.get('Answer') or '')[:80]
                    print(f"[RDS 响应] Event={response_body.get('Event')} Answer={answer_preview!r}...")
                else:
                    print(f"[RDS 响应] Event={response_body.get('Event')} keys={list(response_body.keys())}")

                if event_type == 'message':
                    if response_body.get('Answer'):
                        yield MessageEvent(task_id, final_conversion_id, response_body['Answer'])

                elif event_type in ('tool_call', 'toolcall'):
                    # tool_call_name / status / tool_call_id 在 Answer 的 value 中，需解析 Answer（JSON 字符串）
                    answer_raw = response_body.get('Answer') or response_body.get('answer') or ''
                    payload = {}
                    try:
                        answer_obj = json.loads(answer_raw) if isinstance(answer_raw, str) else answer_raw
                        if isinstance(answer_obj, dict):
                            payload = {
                                'tool_call_name': answer_obj.get('tool_call_name') or answer_obj.get('ToolCallName', ''),
                                'status': answer_obj.get('status') or answer_obj.get('Status', ''),
                                'tool_call_id': answer_obj.get('tool_call_id') or answer_obj.get('ToolCallId', ''),
                            }
                            if 'response' in answer_obj:
                                payload['response'] = answer_obj['response']
                            if 'Response' in answer_obj:
                                payload['response'] = answer_obj['Response']
                    except (json.JSONDecodeError, TypeError):
                        payload = {
                            'tool_call_name': response_body.get('tool_call_name') or '',
                            'status': response_body.get('status') or '',
                            'tool_call_id': response_body.get('tool_call_id') or '',
                        }
                    tool_call_name = payload.get('tool_call_name', '')
                    status = payload.get('status', '')
                    print(f"[RDS] tool_call 事件: name={tool_call_name}, status={status}, tool_call_id={payload.get('tool_call_id', '')}")
                    yield self._emit_tool_call_event(task_id, final_conversion_id, payload)

                elif event_type == 'doc':
                    yield DocumentEvent(
                        task_id, final_conversion_id,
                        title=response_body.get('title', 'Documents'),
                        text=json.dumps(response_body, ensure_ascii=False)
                    )
        except Exception as e:
            print(e)
            raise e
        
        # 生成器结束时返回最终的 conversion_id
        return final_conversion_id