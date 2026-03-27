from __future__ import annotations

from dataclasses import dataclass

from executor import run_tool
from planner import BasePlanner
from state import AgentState, ToolEvent, now_iso
from storage import JsonStorage
from tools import TOOL_REGISTRY


@dataclass
class AgentWorkflow:
    planner: BasePlanner
    storage: JsonStorage
    max_steps: int = 8

    def run(self, state: AgentState) -> AgentState:
        stage = "INIT"
        state.add_history(stage, "Workflow initialized")
        self.storage.save_state(state)

        while state.status == "running":
            if state.current_step >= self.max_steps:
                state.status = "failed"
                state.error = f"Max steps exceeded ({self.max_steps})"
                state.add_history("FAILED", "Loop protection triggered", max_steps=self.max_steps)
                self.storage.save_state(state)
                break

            state.current_step += 1
            state.add_history("PLAN", "Request planner decision", step=state.current_step)
            decision = self.planner.next_action(state)
            state.add_history(
                "PLAN",
                "Planner decision created",
                action=decision.action,
                tool_name=decision.tool_name,
                rationale=decision.rationale,
                args=decision.args or {},
            )
            self.storage.save_state(state)

            if decision.action == "summarize":
                state.final_output = {
                    "goal": state.user_goal,
                    "tool_results": state.tool_results,
                    "summary": self._make_summary(state),
                }
                state.status = "done"
                state.add_history("SUMMARIZE", "Final response assembled")
                self.storage.save_state(state)
                break

            if decision.action != "run_tool" or not decision.tool_name:
                state.status = "failed"
                state.error = f"Unsupported decision: {decision}"
                state.add_history("FAILED", "Planner returned invalid action")
                self.storage.save_state(state)
                break

            tool = TOOL_REGISTRY.get(decision.tool_name)
            if tool is None:
                state.status = "failed"
                state.error = f"Unknown tool: {decision.tool_name}"
                state.add_history("FAILED", "Planner selected unavailable tool", tool_name=decision.tool_name)
                self.storage.save_state(state)
                break

            state.add_history("RUN_TOOL", "Executing tool", tool_name=tool.name, tool_input=decision.args or {})
            response = run_tool(tool, decision.args or {})
            state.tool_results[tool.name] = response

            event = ToolEvent(
                ts=now_iso(),
                task_id=state.task_id,
                step=state.current_step,
                tool_name=tool.name,
                tool_input=decision.args or {},
                tool_output=response,
                status=response["status"],
                error=response.get("error"),
                traceback=response.get("traceback"),
            )
            self.storage.append_tool_event(event)

            if response["status"] == "error":
                state.status = "failed"
                state.error = response["error"]
                state.add_history(
                    "FAILED",
                    "Tool execution failed",
                    tool_name=tool.name,
                    error=response["error"],
                    traceback=response.get("traceback"),
                )
            else:
                state.add_history("VALIDATE", "Tool result accepted", tool_name=tool.name)

            self.storage.save_state(state)

        return state

    @staticmethod
    def _make_summary(state: AgentState) -> str:
        detect = state.tool_results.get("detect_defect", {}).get("result", {})
        classify = state.tool_results.get("classify_part", {}).get("result", {})
        defect_text = "defect detected" if detect.get("has_defect") else "no defect detected"
        part = classify.get("part_class", "unknown")
        quality = classify.get("quality_decision", "unknown")
        return f"Inspection complete: {defect_text}; part={part}; quality_decision={quality}."
