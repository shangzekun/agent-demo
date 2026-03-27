from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from state import AgentState, ToolEvent


class JsonStorage:
    def __init__(self, base_dir: str = "runs") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _task_dir(self, task_id: str) -> Path:
        task_dir = self.base_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir

    def save_state(self, state: AgentState) -> Path:
        out_path = self._task_dir(state.task_id) / "state.json"
        out_path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return out_path

    def append_tool_event(self, event: ToolEvent) -> Path:
        out_path = self._task_dir(event.task_id) / "tool_events.jsonl"
        with out_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        return out_path
