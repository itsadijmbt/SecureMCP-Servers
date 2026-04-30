from fastapi import FastAPI

from databricks.labs.mcp.servers.unity_catalog.tools import get_prepared_mcp_app
from databricks.labs.mcp.utils import get_app_index_route


mcp = get_prepared_mcp_app()

app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)

streamable_app = mcp.streamable_http_app()

app.mount("/api", streamable_app)
app.mount("/", get_app_index_route())
