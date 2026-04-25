import os
import pkgutil
import importlib
from typing import Any, Callable

from ..core.context import global_mcp_instance


def tool(*dargs: Any, **dkwargs: Any) -> Callable:
    mcp_instance = global_mcp_instance()
    return mcp_instance.tool(*dargs, **dkwargs)

print("Initializing and discovering 'tools' package...")

for _, module_name, _ in pkgutil.iter_modules(__path__, __name__ + '.'):
    try:
        importlib.import_module(module_name)
        print(f"  ✓ Discovered tool module: {module_name}")
    except Exception as e:
        print(f"  ✗ Failed to discover tool module {module_name}: {e}")