#!/usr/bin/env python3
"""Schema extraction script for dispatch agents.

This script is embedded in Docker containers during build time to extract
handler schemas and check typing compliance. It generates a schemas.json
artifact that can be read by the CLI and backend services.
"""

import inspect
import json
import os
import sys
import traceback
from typing import get_type_hints

# Import the listener which handles all agent loading and handler registration
# check if the /app folder exists for local development
if not os.path.exists("/app"):
    print("Warning: /app folder not found, assuming local development")
    # Check if we're running from project root (dispatch.yaml exists in current dir)
    if os.path.exists("./dispatch.yaml"):
        root_path = "."
    else:
        # Fallback to parent directory (this shouldn't typically happen)
        root_path = ".."
else:
    root_path = "/app"

sys.path.append(root_path)

# Load environment variables from .env file if it exists
# This supports Docker secret mounts at /app/.env during build time
env_file = os.path.join(root_path, ".env")
if os.path.exists(env_file):
    print(f"[extract_schemas] Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                value = value.strip().strip('"').strip("'")
                os.environ[key.strip()] = value
                print(f"[extract_schemas] Set {key.strip()}")

# Import SDK functions
from dispatch_agents import BasePayload, Message, get_handler_schemas


def extract_schemas_and_compliance():
    """Extract handler schemas and check typing compliance."""
    try:
        # Read entrypoint from dispatch.yaml
        import yaml

        config_path = os.path.join(root_path, "dispatch.yaml")
        with open(config_path) as f:
            config = yaml.safe_load(f)

        entrypoint = config.get("entrypoint", "agent.py")
        # Convert file path to module name (e.g., "agent.py" -> "agent")
        module_name = entrypoint.replace(".py", "").replace("/", ".")

        # Import the agent module to ensure handlers are registered
        __import__(module_name)

        # Get all handler schemas (both @on and @fn handlers)
        handler_schemas = get_handler_schemas()

        schemas = {}
        compliance_issues = []

        for handler_name, metadata in handler_schemas.items():
            # Extract schema information
            schemas[handler_name] = {
                "handler_name": handler_name,
                "input_schema": metadata.input_schema,
                "output_schema": metadata.output_schema,
                "handler_doc": metadata.handler_doc,
                "topics": metadata.topics,
            }

            # Check typing compliance for this handler
            if handler_name:
                compliance_issues.extend(
                    check_handler_compliance(handler_name, handler_name)
                )

        # Create combined artifact
        artifact = {
            "schemas": schemas,
            "compliance_issues": compliance_issues,
            "extraction_success": True,
            "error": None,
        }

        return artifact

    except Exception as e:
        print(f"[DEBUG] Exception during schema extraction: {e}")
        print(f"[DEBUG] Traceback: {traceback.format_exc()}")

        # Return error information in the artifact
        return {
            "schemas": {},
            "compliance_issues": [],
            "extraction_success": False,
            "error": {"message": str(e), "traceback": traceback.format_exc()},
        }


def check_handler_compliance(handler_name: str, topic: str) -> list:
    """Check typing compliance for a single handler."""
    try:
        # Get the handler function from the entrypoint module
        entrypoint_module = sys.modules["entrypoint_module"]
        if not hasattr(entrypoint_module, handler_name):
            return []

        handler_func = getattr(entrypoint_module, handler_name)

        # Inspect the function signature
        sig = inspect.signature(handler_func)
        type_hints = get_type_hints(handler_func)

        issues = []

        # Check parameters
        params = list(sig.parameters.values())
        if not params:
            issues.append(
                "Handler function has no parameters - should accept typed payload"
            )
        else:
            first_param = params[0]
            if first_param.name not in type_hints:
                issues.append(
                    f"Parameter '{first_param.name}' missing type annotation - should be a subclass of dispatch_agents.BasePayload"
                )
            else:
                param_type = type_hints[first_param.name]

                # Check if it's the old Message type (discouraged)
                if param_type is Message:
                    issues.append(
                        "Using 'dispatch_agents.Message' - should use a subclass of dispatch_agents.BasePayload instead"
                    )
                # Check if it's a subclass of BasePayload
                elif not (
                    inspect.isclass(param_type) and issubclass(param_type, BasePayload)
                ):
                    type_name = (
                        param_type.__name__
                        if hasattr(param_type, "__name__")
                        else str(param_type)
                    )
                    issues.append(
                        f"Parameter type '{type_name}' must be a subclass of dispatch_agents.BasePayload"
                    )

        # Check return type
        if "return" not in type_hints:
            issues.append(
                "Missing return type annotation - should specify output type or None"
            )

        # Return compliance issues for this handler
        if issues:
            return [{"topic": topic, "handler": handler_name, "issues": issues}]

        return []

    except Exception:
        # If compliance checking fails, don't fail the entire extraction
        return []


def main():
    """Main entry point for schema extraction."""
    # Extract schemas and compliance info
    artifact = extract_schemas_and_compliance()

    # Write schemas to container .dispatch directory
    os.makedirs("/app/.dispatch", exist_ok=True)
    with open("/app/.dispatch/schemas.json", "w") as f:
        json.dump(artifact, f, indent=2, default=str)

    # Print summary for build logs
    if artifact["extraction_success"]:
        schema_count = len(artifact["schemas"])
        issue_count = len(artifact["compliance_issues"])
        print(f"✓ Extracted {schema_count} handler schemas")
        if issue_count > 0:
            print(f"⚠ Found {issue_count} typing compliance issues")
        else:
            print("✓ All handlers have proper typing")
    else:
        print(f"✗ Schema extraction failed: {artifact['error']['message']}")

    # Always exit successfully - don't fail the Docker build if schema extraction fails
    sys.exit(0)


if __name__ == "__main__":
    main()
