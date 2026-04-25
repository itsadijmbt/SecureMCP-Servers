# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

from macaw_adapters.mcp import SecureMCP
import os
from enum import Enum

# from mcp.server.fastmcp.prompts import Prompt
from .context import set_mcp_instance


class _ComponentType(Enum):
    """Defines the valid types of components that can be registered."""
    TOOL = 'tool'
    PROMPT = 'prompt'
    RESOURCE = 'resource'

@dataclass
class _RegistrableItem:
    func: Callable
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    group: str
    item_type: _ComponentType


# PORT: RdsMCP no longer inherits from FastMCP. It WRAPS a SecureMCP
# instance via composition (see __init__ below). All inherited methods
# from FastMCP that the original code reached via `super().X(...)` are
# now reached via `self._mcp.X(...)` instead.
class RdsMCP:
    """ An enhanced FastMCP that supports grouping and delayed registration of
    components like tools, prompts, and resources.

    This class introduces a two-phase workflow for component management:
    1.  **Definition Phase:** Use decorators like `@mcp.tool()` to *define* a
        component and assign it to a logical group (e.g., 'database', 'api').
        At this stage, the component is only cataloged internally and is NOT yet
        active in the underlying FastMCP system.
    2.  **Activation Phase:** Call the `.activate()` method with a list of group
        names. Only the components from these specified groups are then validated
        and formally registered with the FastMCP, making them live.

     **Usage Workflow:**
    The expected lifecycle is as follows:
    1.  Instantiate `RdsMCP`: `mcp = RdsMCP()`
    2.  Define components using decorators: `@mcp.tool(...)`
    3.  Finalize the setup by calling the activation method:
        `mcp.activate(enabled_groups=['group1', 'group2'])`
    """
    

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the engine with an internal list for pending registrations."""
        self._pending_registrations: List[_RegistrableItem] = []
        self._is_activated = False
        # not for securemcp
        # super().__init__(*args, **kwargs)
        self._mcp=SecureMCP(*args, **kwargs)
        set_mcp_instance(self)

        # Now since there is no inheritance super() -> self.
    # _SECUREMCP_TOOL_KWARGS = {"name", "description", "prompts"}                                                                                                                                 
    # _SECUREMCP_PROMPT_KWARGS = {"name", "description"}

    '''
    Decorate a tool and store it for later registration.

    This method overrides the mcp.tool() registration mechanism.
    All tools not explicitly assigned to specific groups will be automatically categorized into the
    "rds" group. This ensures that when launching without tools parameters, these default tools are automatically loaded.
    '''
    def tool(self, *dargs: Any, group: str = 'rds', **dkwargs: Any) -> Callable:
        #Decorator used without parentheses, e.g., @mcp.tool
        if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
            func = dargs[0]
            item = _RegistrableItem(
                func=func, group=group, item_type=_ComponentType.TOOL,
                args=(), kwargs={}
            )
            self._pending_registrations.append(item)
            return func

        #Decorator used with parentheses, e.g., @mcp.tool(group='db')
        def decorator(fn: Callable) -> Callable:
            item = _RegistrableItem(
                func=fn, group=group, item_type=_ComponentType.TOOL,
                args=dargs, kwargs=dkwargs
            )
            self._pending_registrations.append(item)
            return fn

        return decorator

    def prompt(self, *dargs: Any, group: str = 'rds', **dkwargs: Any) -> Callable:
        if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
            func = dargs[0]
            item = _RegistrableItem(
                func=func, group=group, item_type=_ComponentType.PROMPT,
                args=(), kwargs={}
            )
            self._pending_registrations.append(item)
            return func

        def decorator(fn: Callable) -> Callable:
            item = _RegistrableItem(
                func=fn, group=group, item_type=_ComponentType.PROMPT,
                args=dargs, kwargs=dkwargs
            )
            self._pending_registrations.append(item)
            return fn

        return decorator


    def activate(self, enabled_groups: list[str]) -> None:
        """
        Finalizes the setup by activating all deferred components.
        """
        if self._is_activated:
            print("Warning: MCP engine has already been activated. Ignoring subsequent calls.")
            return

        self._validate_groups(enabled_groups)
        print(f"\n--- Activating Component Groups: {enabled_groups} ---")

        activated_items: List[_RegistrableItem] = []
        for item in self._pending_registrations:
            if item.group in enabled_groups:
                print(f"Activating {item.item_type.value} '{item.func.__name__}' from group '{item.group}'...")

                final_kwargs = item.kwargs.copy()
                final_kwargs.setdefault('name', item.func.__name__)

                # PORT: SecureMCP's .tool() and .prompt() decorators have a
                # narrower signature than FastMCP's add_tool/add_prompt. They
                # accept only (name, description, prompts) for tools and
                # (name, description) for prompts. Anything else (e.g.
                # `annotations=READ_ONLY_TOOL` from the original code) would
                # raise TypeError, so we filter to the accepted keys here.
                if item.item_type == _ComponentType.TOOL:
                    tool_kwargs = {
                        k: v for k, v in final_kwargs.items()
                        if k in ("name", "description", "prompts")
                    }
                    # PORT: was `super().add_tool(item.func, **final_kwargs)`.
                    # SecureMCP exposes .tool() as a decorator-factory only
                    # (no imperative add_tool). Use the decorator-as-function
                    # form: `decorator(...)(fn)`.
                    self._mcp.tool(**tool_kwargs)(item.func)

                elif item.item_type == _ComponentType.PROMPT:
                    prompt_kwargs = {
                        k: v for k, v in final_kwargs.items()
                        if k in ("name", "description")
                    }
                    # PORT: was `super().add_prompt(Prompt(fn=..., **final_kwargs))`.
                    # SecureMCP doesn't use a Prompt wrapper object — its
                    # .prompt() decorator stores the function directly.
                    self._mcp.prompt(**prompt_kwargs)(item.func)

                activated_items.append(item)

        self._is_activated = True
        print("--- Activation Complete ---")
        self._run_debug_output(enabled_groups, activated_items)

    # PORT: forward run() to the inner SecureMCP. Required because RdsMCP
    # no longer inherits from FastMCP, so callers' `mcp.run(...)` would
    # otherwise fail with AttributeError.
    def run(self, transport: str = "stdio") -> None:
        return self._mcp.run(transport)

    def _validate_groups(self, enabled_groups: list[str]) -> None:
        """Checks if all requested groups are valid before activation."""
        all_defined_groups = {item.group for item in self._pending_registrations}
        invalid_groups = set(enabled_groups) - all_defined_groups
        if invalid_groups:
            raise ValueError(
                f"Unknown group(s): {sorted(list(invalid_groups))}. "
                f"Available groups: {sorted(list(all_defined_groups))}"
            )

    def _run_debug_output(self, enabled_groups: list[str], activated_items: list[_RegistrableItem]):
        """Prints debug information for all component types if the env var is set."""
        if os.getenv('TOOLSET_DEBUG', '').lower() in ('1', 'true', 'yes', 'on'):
            all_groups = sorted(list({item.group for item in self._pending_registrations}))

            print("\n--- COMPONENT DEBUG OUTPUT ---")
            print(f"All defined groups: {all_groups}")
            print(f"Enabled groups for this activation: {sorted(enabled_groups)}")

            output_by_type: Dict[str, List[_RegistrableItem]] = {}
            for item in activated_items:
                output_by_type.setdefault(item.item_type.value.upper() + 'S', []).append(item)

            if not output_by_type:
                print("No components were activated.")

            for item_type_str, items in sorted(output_by_type.items()):
                print(f"Activated {item_type_str}:")
                grouped_items: Dict[str, List[str]] = {}
                for item in items:
                    grouped_items.setdefault(item.group, []).append(item.func.__name__)

                for group in sorted(grouped_items.keys()):
                    print(f"  - Group: {group}")
                    for item_name in sorted(grouped_items[group]):
                        print(f"    • {item_name}")

            print("----------------------------\n")

