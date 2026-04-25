# -*- coding: utf-8 -*-
from mcp.server.fastmcp import FastMCP
from mcp.server.session import ServerSession
from settings import settings
from vector_store import VectorStore

####################################################################################
# Temporary monkeypatch which avoids crashing when a POST message is received
# before a connection has been initialized, e.g: after a deployment.
# pylint: disable-next=protected-access
old__received_request = ServerSession._received_request


async def _received_request(self, *args, **kwargs):
    try:
        return await old__received_request(self, *args, **kwargs)
    except RuntimeError:
        pass


# pylint: disable-next=protected-access
ServerSession._received_request = _received_request
####################################################################################

settings.load_config(settings.CONFIG_FILE)
vectorestores = VectorStore(
    model_name=settings.RAG_EMBEDDING_MODEL,
    api_key=settings.RAG_API_KEY,
    base_url=settings.RAG_API_BASE_URL,
    dir_path=settings.RAG_DATA_DIR
)

mcp = FastMCP(
    name="MyBase Table Struct Tool",
    host="0.0.0.0",
    port=8006,
    description="根据用户的查询返回对应的表结构信息。",
    sse_path='/sse'
)

@mcp.tool()
async def get_table_struct(query: str, topk: int=10) -> str:
        """
        根据用户的输入获取与之关联的 k 个数据库表结构信息。
        Args:
            query (str): 用户的查询。
            topk (int): 返回的记录数。
        Return:
            res: 返回的表结构内容。
        """
        res = ""
        vectorestore = vectorestores.load_vectorstore_by_name("table_struct")
        if vectorestore is not None:
            docs = vectorestore.similarity_search(query, k=topk)
            res = "\n".join(doc.page_content for doc in docs)
        return res

if __name__ == "__main__":
    # 初始化并运行服务器
    try:
        print("Starting server...")
        mcp.run(transport='sse')
    except Exception as e:
        print(f"Error: {e}")