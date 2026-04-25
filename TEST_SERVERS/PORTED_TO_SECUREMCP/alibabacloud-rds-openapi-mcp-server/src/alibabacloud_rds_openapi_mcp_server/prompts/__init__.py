import os
import pkgutil
import importlib
from typing import Any, Callable

from ..core.context import global_mcp_instance


def prompt(*dargs: Any, **dkwargs: Any) -> Callable:
    mcp_instance = global_mcp_instance()
    return mcp_instance.prompt(*dargs, **dkwargs)

print("Initializing and discovering 'prompts' package...")

for _, module_name, _ in pkgutil.iter_modules(__path__, __name__ + '.'):
    try:
        importlib.import_module(module_name)
        print(f"  ✓ Discovered prompt module: {module_name}")
    except Exception as e:
        print(f"  ✗ Failed to discover prompt module {module_name}: {e}")