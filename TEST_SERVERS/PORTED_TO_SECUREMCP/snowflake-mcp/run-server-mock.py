"""
Run snowflake-mcp under SecureMCP WITHOUT real Snowflake credentials.

Use case: smoke-test the port (TESTS 1, 3, 4 in client-test-macaw.py)
on a machine that has no Snowflake account.

How it works:
  Before importing the server module, we replace
  `snowflake.connector.connect` with a function that returns a MagicMock.
  MagicMock accepts any attribute access and method call without error.
  Result: SnowflakeService.__init__ thinks it has a connection, the
  server boots, registers on the mesh, registers tools, install_query_check
  runs.

  Tools that try to actually USE the connection at call time will get
  MagicMock responses (which won't be useful data). But for the SQL
  allow/deny tests, the wrapper rejects the call BEFORE reaching the
  tool body, so the mock is never touched.

This is a TEST-ONLY launcher. Do NOT use in production. Production
needs real Snowflake credentials and the regular entry point.

Usage:
    python3 run-server-mock.py --service-config-file services/configuration.yaml
"""

import sys
from unittest.mock import MagicMock

# ----------------------------------------------------------------------
# Patch BEFORE importing the server module. Order matters: the import
# of mcp_server_snowflake.server triggers SnowflakeService construction
# which calls snowflake.connector.connect(). If we patch after import,
# we're too late.
# ----------------------------------------------------------------------
import snowflake.connector

_real_connect = snowflake.connector.connect

def _mock_connect(**kwargs):
    print("[run-server-mock] snowflake.connector.connect intercepted; "
          "returning MagicMock (no real connection).")
    return MagicMock(name="MockSnowflakeConnection")

snowflake.connector.connect = _mock_connect

# Snowflake's snowflake.core.Root may also try to do real work on the
# connection. Replace it with a mock-returning factory too.
import snowflake.core
snowflake.core.Root = lambda conn: MagicMock(name="MockSnowflakeRoot")

# Now safe to import the real server.
from mcp_server_snowflake.server import main


if __name__ == "__main__":
    main()
