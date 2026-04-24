import importlib
import pkgutil
from macaw_adapters.mcp import SecureMCP


def load_tools():
    import src.tools as tools_pkg

    for _, module_name, _ in pkgutil.iter_modules(tools_pkg.__path__):
        importlib.import_module(f"src.tools.{module_name}")


# Initialize FastMCP server
mcp = SecureMCP("securemcp-Redis-mCP-server")

# Load tools
load_tools()
