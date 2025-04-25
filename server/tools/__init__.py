import os
import importlib

tools = {}
tool_schemas = []
metadata_map = {}
# Dynamically load all tools from the tools directory
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file != "__init__.py":
        module = importlib.import_module(f"tools.{file[:-3]}")
        if hasattr(module, "func_schema") and hasattr(module, "handler"):
            tool_schemas.append(module.func_schema)
            tools[module.func_schema["name"]] = module.handler
            if hasattr(module, "metadata"):
                metadata_map[module.func_schema["name"]] = module.metadata
