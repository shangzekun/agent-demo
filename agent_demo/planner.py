from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from state import AgentState

PlannerAction = Literal["run_tool", "summarize"]


@dataclass
class PlanDecision:
    action: PlannerAction
    tool_name: str | None = None
    args: dict[str, Any] | None = None
    rationale: str = ""


class BasePlanner:
    def next_action(self, state: AgentState) -> PlanDecision:  # pragma: no cover - interface
        raise NotImplementedError


class FakePlanner(BasePlanner):
    """Rule-based planner, intentionally replaceable by future LLM planner."""

    def next_action(self, state: AgentState) -> PlanDecision:
        image_path = state.input_artifacts.get("image_path", "")

        if "detect_defect" not in state.tool_results:
            return PlanDecision(
                action="run_tool",
                tool_name="detect_defect",
                args={"image_path": image_path},
                rationale="Need defect signal before downstream decisions.",
            )

        if "classify_part" not in state.tool_results:
            defect_result = state.tool_results["detect_defect"]["result"]
            return PlanDecision(
                action="run_tool",
                tool_name="classify_part",
                args={"image_path": image_path, "defect_detected": defect_result["has_defect"]},
                rationale="Use defect context to classify part and quality.",
            )

        return PlanDecision(action="summarize", rationale="All required tools have run.")
