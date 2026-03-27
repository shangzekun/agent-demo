from __future__ import annotations

import traceback
from typing import Any

from tools import ToolSpec


class ToolExecutionError(ValueError):
    pass


def _validate_parameters(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    missing = [name for name in required if name not in payload]
    if missing:
        raise ToolExecutionError(f"Missing required parameters: {missing}")

    type_map = {"string": str, "boolean": bool, "number": (int, float), "integer": int, "object": dict, "array": list}
    for key, value in payload.items():
        if key not in properties:
            raise ToolExecutionError(f"Unknown parameter '{key}'")
        expected_type = properties[key].get("type")
        if expected_type in type_map and not isinstance(value, type_map[expected_type]):
            raise ToolExecutionError(
                f"Parameter '{key}' expects {expected_type}, got {type(value).__name__}"
            )


def run_tool(tool: ToolSpec, payload: dict[str, Any]) -> dict[str, Any]:
    """Run a tool with schema validation and normalized output envelope."""
    try:
        _validate_parameters(tool.parameters, payload)
        result = tool.fn(**payload)
        return {"status": "ok", "result": result, "error": None, "traceback": None}
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "result": None,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
