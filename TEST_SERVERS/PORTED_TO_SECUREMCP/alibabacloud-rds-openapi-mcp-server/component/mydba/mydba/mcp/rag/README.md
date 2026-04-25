# RAG MCP Server

RAG MCP server for mydba

## Using Cline

```shell
# set env
export MYDBA_RAG_API_KEY=sk-xxx; # model api key, don't set it if you want to use local model
export MYDBA_RAG_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1; # model api base url
export MYDBA_RAG_EMBEDDING_MODEL=text-embedding-v2; # model name, it will download the specific model file if the api key is not set(default: maidalun/bce-embedding-base_v1), download url: https://modelscope.cn/models

# run mcp server
uv run rag_server.py
```
