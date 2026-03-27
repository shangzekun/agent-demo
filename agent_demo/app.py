from __future__ import annotations

import json
import uuid
from pathlib import Path

from planner import FakePlanner
from state import AgentState
from storage import JsonStorage
from workflow import AgentWorkflow


def bootstrap_demo_input() -> str:
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    image_path = sample_dir / "bearing_defect_sample.jpg"
    image_path.write_bytes(b"fake-image-content")
    return str(image_path)


def main() -> None:
    image_path = bootstrap_demo_input()
    task_id = f"task_{uuid.uuid4().hex[:8]}"

    state = AgentState(
        task_id=task_id,
        user_goal="Analyze image and return defect + part classification.",
        input_artifacts={"image_path": image_path},
    )

    workflow = AgentWorkflow(planner=FakePlanner(), storage=JsonStorage(base_dir="runs"), max_steps=6)
    final_state = workflow.run(state)

    print("=== FINAL STATE ===")
    print(json.dumps(final_state.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
