# -*- coding: utf-8 -*-
from langchain_community.embeddings import OpenAIEmbeddings
from typing import List, Optional

'''
CompatibleEmbeddings 兼容 OpenAI Embedding API
'''
class CompatibleEmbeddings(OpenAIEmbeddings):

    def _tokenize(self, texts: List[str], chunk_size: int) -> tuple:
        """
        禁用 Tokenization，直接返回原始文本和索引
        """
        indices = list(range(len(texts)))
        return (range(0, len(texts), chunk_size), texts, indices)

    def _get_len_safe_embeddings(
            self, texts: List[str], *, engine: str, chunk_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        直接传递原始文本，跳过 Token 化步骤
        """
        _chunk_size = chunk_size or self.chunk_size
        batched_embeddings: List[List[float]] = []

        # 直接遍历原始文本分块
        for i in range(0, len(texts), _chunk_size):
            chunk = texts[i: i + _chunk_size]

            # 关键修改：input 直接使用文本列表
            response = self.client.create(
                input=chunk,  # 直接使用原始文本列表
                model=self.model,  # 显式传递模型参数
                **{k: v for k, v in self._invocation_params.items() if k != "model"}
            )

            if not isinstance(response, dict):
                response = response.model_dump()
            batched_embeddings.extend(r["embedding"] for r in response["data"])

        # 跳过空文本处理（Ollama 不需要）
        return batched_embeddings

    async def _aget_len_safe_embeddings(
            self, texts: List[str], *, engine: str, chunk_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        异步版本处理逻辑
        """
        _chunk_size = chunk_size or self.chunk_size
        batched_embeddings: List[List[float]] = []

        for i in range(0, len(texts), _chunk_size):
            chunk = texts[i: i + _chunk_size]

            response = await self.async_client.create(
                input=chunk,
                model=self.model,
                **{k: v for k, v in self._invocation_params.items() if k != "model"}
            )

            if not isinstance(response, dict):
                response = response.model_dump()
            batched_embeddings.extend(r["embedding"] for r in response["data"])  # 注意: 实际应为 "embedding"

        return batched_embeddings
