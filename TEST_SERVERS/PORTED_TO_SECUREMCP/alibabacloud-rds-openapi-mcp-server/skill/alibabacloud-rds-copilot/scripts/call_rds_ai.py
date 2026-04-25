#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.7"
# dependencies = [
#     "alibabacloud_rdsai20250507>=1.0.0",
#     "alibabacloud_tea_openapi>=0.3.0",
#     "alibabacloud_tea_util>=0.3.0",
# ]
# ///
# -*- coding: utf-8 -*-
"""
阿里云 RDS AI 助手调用脚本
用于接收用户查询并调用 RDS AI 助手 API，流式返回结果
"""
import os
import sys
import argparse
import json
from typing import Optional

try:
    from alibabacloud_rdsai20250507.client import Client as RdsAi20250507Client
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_rdsai20250507 import models as rds_ai_20250507_models
    from alibabacloud_tea_util import models as util_models
except ImportError as e:
    print(f"错误: 缺少必要的依赖包。请先安装: pip install alibabacloud_rdsai20250507 alibabacloud_tea_openapi alibabacloud_tea_util", file=sys.stderr)
    print(f"详细错误: {e}", file=sys.stderr)
    sys.exit(1)


class RdsAiAssistant:
    """RDS AI 助手客户端封装"""
    
    def __init__(self, endpoint: str = "rdsai.aliyuncs.com"):
        """
        初始化 RDS AI 助手客户端
        
        Args:
            endpoint: API 端点，默认为 rdsai.aliyuncs.com
        """
        self.endpoint = endpoint
        self.client = self._create_client()
    
    def _create_client(self) -> RdsAi20250507Client:
        """创建阿里云 RDS AI 客户端"""
        access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        
        if not access_key_id or not access_key_secret:
            raise ValueError(
                "未找到阿里云访问凭证。请设置环境变量:\n"
                "  ALIBABA_CLOUD_ACCESS_KEY_ID\n"
                "  ALIBABA_CLOUD_ACCESS_KEY_SECRET"
            )
        
        config = open_api_models.Config(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
        )
        config.endpoint = self.endpoint
        return RdsAi20250507Client(config)
    
    def chat(
        self,
        query: str,
        region_id: str = "cn-hangzhou",
        language: str = "zh-CN",
        timezone: str = "Asia/Shanghai",
        custom_agent_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        stream: bool = True
    ) -> None:
        """
        与 RDS AI 助手对话
        
        Args:
            query: 用户查询内容
            region_id: 阿里云地域 ID，默认 cn-hangzhou
            language: 语言，默认 zh-CN
            timezone: 时区，默认 Asia/Shanghai
            custom_agent_id: 专属 Agent ID（可选）
            conversation_id: 会话 ID，用于多轮对话（可选）
            stream: 是否使用流式输出，默认 True
        """
        # 构造输入参数
        inputs_kwargs = {
            "language": language,
            "region_id": region_id,
            "timezone": timezone,
        }
        if custom_agent_id:
            inputs_kwargs["custom_agent_id"] = custom_agent_id
        
        inputs = rds_ai_20250507_models.ChatMessagesRequestInputs(**inputs_kwargs)
        
        # 构造请求
        request_kwargs = {
            "query": query,
            "event_mode": "separate",
            "inputs": inputs,
        }
        if conversation_id:
            request_kwargs["conversation_id"] = conversation_id
        
        chat_messages_request = rds_ai_20250507_models.ChatMessagesRequest(**request_kwargs)
        runtime = util_models.RuntimeOptions()
        
        try:
            if stream:
                # 流式输出
                print(f"[查询] {query}", file=sys.stderr)
                print(f"[地域] {region_id} | [语言] {language}", file=sys.stderr)
                if custom_agent_id:
                    print(f"[专属Agent] {custom_agent_id}", file=sys.stderr)
                if conversation_id:
                    print(f"[会话ID] {conversation_id}", file=sys.stderr)
                print("=" * 60, file=sys.stderr)
                print("[RDS AI 助手回答]", file=sys.stderr)
                
                chat_messages_response = self.client.chat_messages_with_sse(
                    tmp_req=chat_messages_request,
                    runtime=runtime,
                )
                
                for chunk in chat_messages_response:
                    body = chunk.body
                    if body is not None:
                        if body.event == "message" and body.answer:
                            print(body.answer, end="", flush=True)
                        elif body.event == "finish":
                            # 输出会话 ID（用于后续多轮对话）
                            if hasattr(body, 'conversation_id') and body.conversation_id:
                                print(f"\n\n[会话ID] {body.conversation_id}", file=sys.stderr)
                
                print()  # 换行
            else:
                # 非流式输出
                response = self.client.chat_messages(
                    request=chat_messages_request,
                    runtime=runtime,
                )
                print(response.body.answer)
                if hasattr(response.body, 'conversation_id') and response.body.conversation_id:
                    print(f"\n[会话ID] {response.body.conversation_id}", file=sys.stderr)
        
        except Exception as e:
            print(f"\n调用 RDS AI 助手时出错: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="阿里云 RDS AI 助手命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础查询
  python call_rds_ai.py "查询杭州地域的 RDS 实例列表"
  
  # 指定地域和语言
  python call_rds_ai.py "查询实例列表" --region cn-beijing --language en-US
  
  # 使用专属 Agent
  python call_rds_ai.py "优化这条SQL" --custom-agent-id "your-agent-id"
  
  # 多轮对话（使用上次返回的会话ID）
  python call_rds_ai.py "继续上面的分析" --conversation-id "conv-xxx"
  
  # 从标准输入读取查询
  echo "查询实例列表" | python call_rds_ai.py -
        """
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="要查询的内容。使用 '-' 从标准输入读取"
    )
    parser.add_argument(
        "--region", "--region-id",
        dest="region_id",
        default="cn-hangzhou",
        help="阿里云地域 ID (默认: cn-hangzhou)"
    )
    parser.add_argument(
        "--language", "--lang",
        dest="language",
        default="zh-CN",
        help="语言 (默认: zh-CN)"
    )
    parser.add_argument(
        "--timezone", "--tz",
        dest="timezone",
        default="Asia/Shanghai",
        help="时区 (默认: Asia/Shanghai)"
    )
    parser.add_argument(
        "--custom-agent-id",
        dest="custom_agent_id",
        help="专属 Agent ID（可选）"
    )
    parser.add_argument(
        "--conversation-id", "--conv-id",
        dest="conversation_id",
        help="会话 ID，用于多轮对话（可选）"
    )
    parser.add_argument(
        "--endpoint",
        default="rdsai.aliyuncs.com",
        help="API 端点 (默认: rdsai.aliyuncs.com)"
    )
    parser.add_argument(
        "--no-stream",
        dest="stream",
        action="store_false",
        help="禁用流式输出"
    )
    
    args = parser.parse_args()
    
    # 获取查询内容
    query = args.query
    if not query:
        parser.print_help()
        sys.exit(1)
    
    if query == "-":
        # 从标准输入读取
        query = sys.stdin.read().strip()
        if not query:
            print("错误: 未从标准输入读取到内容", file=sys.stderr)
            sys.exit(1)
    
    # 创建助手并执行查询
    assistant = RdsAiAssistant(endpoint=args.endpoint)
    assistant.chat(
        query=query,
        region_id=args.region_id,
        language=args.language,
        timezone=args.timezone,
        custom_agent_id=args.custom_agent_id,
        conversation_id=args.conversation_id,
        stream=args.stream
    )


if __name__ == "__main__":
    main()
