import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from alibabacloud_rds_openapi_mcp_server.core.mcp import RdsMCP, FastMCP, Prompt
from alibabacloud_rds_openapi_mcp_server.core.context import set_mcp_instance

DEFAULT_TOOL_GROUP = 'rds'


@pytest.fixture
def mcp_instance(monkeypatch) -> RdsMCP:
    mocked_add_tool = MagicMock()
    mocked_add_prompt = MagicMock()

    monkeypatch.setattr(FastMCP, "add_tool", mocked_add_tool)
    monkeypatch.setattr(FastMCP, "add_prompt", mocked_add_prompt)

    mcp = RdsMCP("dummy_server")

    mcp.add_tool = mocked_add_tool
    mcp.add_prompt = mocked_add_prompt

    set_mcp_instance(mcp)
    yield mcp
    # Teardown: Clear the global context
    set_mcp_instance(None)


@pytest.fixture
def populated_mcp(mcp_instance: RdsMCP):
    """
    A fixture that populates the MCP instance with several deferred
    component definitions.
    """

    def rds_tool_a(): pass

    def rds_tool_b(): pass

    def custom_tool_a(): pass

    def custom_prompt_a(): return "prompt content"

    mcp_instance.tool(rds_tool_a)
    mcp_instance.tool(group="rds")(rds_tool_b)
    mcp_instance.tool(group="rds_custom")(custom_tool_a)
    mcp_instance.prompt(group="rds_custom", name="custom_prompt")(custom_prompt_a)

    mcp_instance._test_funcs = {
        "rds_tool_a": rds_tool_a,
        "rds_tool_b": rds_tool_b,
        "custom_tool_a": custom_tool_a,
        "custom_prompt_a": custom_prompt_a,
    }
    return mcp_instance


# --- Corrected Test Cases ---

def test_activate_should_register_default_tools_when_default_group_is_passed(populated_mcp: RdsMCP):
    mcp = populated_mcp
    test_funcs = mcp._test_funcs

    mcp.activate(enabled_groups=[DEFAULT_TOOL_GROUP])

    # Assert that the mock attached to the instance was called correctly
    assert mcp.add_tool.call_count == 2
    mcp.add_tool.assert_any_call(test_funcs["rds_tool_a"], name="rds_tool_a")
    mcp.add_tool.assert_any_call(test_funcs["rds_tool_b"], name="rds_tool_b")
    mcp.add_prompt.assert_not_called()


def test_activate_should_register_only_specified_groups(populated_mcp: RdsMCP):
    mcp = populated_mcp
    test_funcs = mcp._test_funcs

    mcp.activate(enabled_groups=["rds_custom"])

    assert mcp.add_tool.call_count == 1
    mcp.add_tool.assert_called_once_with(test_funcs["custom_tool_a"], name="custom_tool_a")

    assert mcp.add_prompt.call_count == 1
    registered_prompt_obj = mcp.add_prompt.call_args.args[0]
    assert isinstance(registered_prompt_obj, Prompt)
    assert registered_prompt_obj.name == "custom_prompt"


def test_activate_should_raise_value_error_when_an_unknown_group_is_passed(populated_mcp: RdsMCP):
    with pytest.raises(ValueError, match="Unknown group\\(s\\): \\['invalid_group'\\]"):
        populated_mcp.activate(enabled_groups=["rds", "invalid_group"])


def test_activate_should_do_nothing_when_called_a_second_time(populated_mcp: RdsMCP):
    """
    Tests that the internal activation logic only runs once.
    """
    mcp = populated_mcp

    mcp.activate(enabled_groups=["rds"])
    # Initial registration count should be 2
    assert mcp.add_tool.call_count == 2
    assert mcp.add_prompt.call_count == 0

    # Call activate again with a different group
    mcp.activate(enabled_groups=["rds_custom"])

    # Assert that the call counts have NOT changed, because it was already activated
    assert mcp.add_tool.call_count == 2
    assert mcp.add_prompt.call_count == 0

def test_activate_should_not_register_duplicates_when_enabled_groups_contain_duplicates(populated_mcp: RdsMCP):
    mcp = populated_mcp

    # Enable 'rds' group twice.
    mcp.activate(enabled_groups=['rds', 'rds_custom', 'rds'])

    assert mcp.add_tool.call_count == 3
    # We expect 1 prompt from 'rds_custom'.
    assert mcp.add_prompt.call_count == 1


def test_activate_should_succeed_gracefully_when_activating_an_empty_group(mcp_instance: RdsMCP):
    """
    Tests that the system runs without error when an enabled group
    is valid but contains no components.
    """
    mcp = mcp_instance

    # Define a tool in 'group_a' but leave 'group_b' empty
    def my_tool():
        pass

    mcp.tool(group='group_a')(my_tool)

    try:
        mcp.activate(enabled_groups=['group_a'])
    except ValueError:
        pytest.fail("activate() raised ValueError unexpectedly for a valid, non-empty group.")
    assert mcp.add_tool.call_count == 1
    mcp.add_tool.assert_called_once_with(my_tool, name='my_tool')
