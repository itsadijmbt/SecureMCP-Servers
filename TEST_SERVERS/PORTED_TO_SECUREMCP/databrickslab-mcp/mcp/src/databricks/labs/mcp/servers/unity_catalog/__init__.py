import sys
from traceback import format_exc
from databricks.labs.mcp.servers.unity_catalog.server import start
from databricks.labs.mcp._version import __version__ as VERSION

from databricks.sdk.config import with_user_agent_extra


def main() -> None:
    with_user_agent_extra(key="unitycatalog-mcp", value=VERSION)
    start()


if __name__ == "__main__":
    try:
        main()
    except Exception as _:
        print(format_exc(), file=sys.stderr)
