import pytest
from databricks.labs.mcp.servers.unity_catalog.cli import get_settings, CliSettings


@pytest.fixture(autouse=True)
def reset_settings_cache():
    CliSettings.model_config["env_file"] = ""
    get_settings.cache_clear()
