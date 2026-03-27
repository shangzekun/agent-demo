from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

ToolFn = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: ToolFn


def detect_defect(*, image_path: str) -> dict[str, Any]:
    """Mock defect detector."""
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    has_defect = "defect" in Path(image_path).name.lower()
    score = 0.91 if has_defect else 0.11
    return {
        "image_path": image_path,
        "has_defect": has_defect,
        "confidence": score,
        "detections": [{"label": "surface_defect", "score": score}] if has_defect else [],
    }


def classify_part(*, image_path: str, defect_detected: bool) -> dict[str, Any]:
    """Mock part classifier that can consume previous-tool context."""
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    part = "bearing" if "bearing" in Path(image_path).name.lower() else "generic_component"
    quality = "reject" if defect_detected else "pass"
    return {
        "image_path": image_path,
        "part_class": part,
        "quality_decision": quality,
        "confidence": 0.87,
    }


TOOL_REGISTRY: dict[str, ToolSpec] = {
    "detect_defect": ToolSpec(
        name="detect_defect",
        description="Detect surface defects from an input image.",
        parameters={"type": "object", "required": ["image_path"], "properties": {"image_path": {"type": "string"}}},
        fn=detect_defect,
    ),
    "classify_part": ToolSpec(
        name="classify_part",
        description="Classify part type and quality decision using image and defect signal.",
        parameters={
            "type": "object",
            "required": ["image_path", "defect_detected"],
            "properties": {
                "image_path": {"type": "string"},
                "defect_detected": {"type": "boolean"},
            },
        },
        fn=classify_part,
    ),
}
