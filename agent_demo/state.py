from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


AgentStatus = Literal["running", "failed", "done"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class HistoryEvent:
    ts: str
    stage: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolEvent:
    ts: str
    task_id: str
    step: int
    tool_name: str
    tool_input: dict[str, Any]
    tool_output: dict[str, Any]
    status: Literal["ok", "error"]
    error: str | None = None
    traceback: str | None = None


@dataclass
class AgentState:
    task_id: str
    user_goal: str
    input_artifacts: dict[str, Any]
    tool_results: dict[str, Any] = field(default_factory=dict)
    current_step: int = 0
    status: AgentStatus = "running"
    error: str | None = None
    final_output: dict[str, Any] | None = None
    history: list[HistoryEvent] = field(default_factory=list)

    def add_history(self, stage: str, message: str, **data: Any) -> None:
        self.history.append(HistoryEvent(ts=now_iso(), stage=stage, message=message, data=data))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
