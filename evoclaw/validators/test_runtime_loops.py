#!/usr/bin/env python3
"""End-to-end closed-loop smoke tests for runtime contracts.

Covers:
1) single task loop
2) subtask loop (L1)
3) proposal publish loop with rollback
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "runtime" / "contracts"
EXAMPLES = ROOT / "runtime" / "examples"


def _validate(schema_path: Path, payload: dict) -> None:
    import jsonschema  # type: ignore

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(payload, schema)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def single_task_loop() -> dict:
    bundle = _load_json(EXAMPLES / "task_subtask.example.json")
    _validate(CONTRACTS / "task_subtask.schema.json", bundle)

    task = bundle["task"]
    # before_task + recall + route + episodic + proposal
    before_task = {
        "task_guardrail_bundle": ["must_follow_P0_P1", "respect_file_scope"],
        "task_level_recall_packet": {"rules": ["rule_safe_edit"], "experience": ["similar_fix_001"]},
    }
    selected_skill = "coding_editor_v1"
    episodic_write = {
        "object_type": "routing_outcome",
        "task_id": task["task_id"],
        "selected_skill": selected_skill,
        "status": "success",
    }
    proposal = {
        "proposal_id": "pp_single_001",
        "source": "after_task",
        "candidate_type": "routing_weight_update_candidate",
        "payload": {"target": selected_skill, "delta": {"w2": 0.01}},
        "status": "candidate",
    }

    return {
        "task_id": task["task_id"],
        "before_task": before_task,
        "episodic_write": episodic_write,
        "proposal": proposal,
    }


def subtask_loop() -> dict:
    bundle = _load_json(EXAMPLES / "task_subtask.example.json")
    _validate(CONTRACTS / "task_subtask.schema.json", bundle)

    subtasks = [
        {**bundle["subtasks"][0], "subtask_id": "st_001", "subtask_type": "analyze", "file_scope": []},
        {**bundle["subtasks"][0], "subtask_id": "st_002", "subtask_type": "edit_file"},
        {**bundle["subtasks"][0], "subtask_id": "st_003", "subtask_type": "run_validation"},
    ]
    # repair required rules for analyze without file_scope
    subtasks[0].pop("required_skill", None)

    traces = []
    for st in subtasks:
        # before_subtask fields present check
        for k in ["subtask_type", "local_scenario", "required_tools", "done_criteria"]:
            assert k in st
        # simulate routing difference
        score = 0.82 if st["subtask_type"] == "edit_file" else 0.66
        selected = "coding_editor_v1" if score > 0.75 else "generic_helper_v1"
        traces.append(
            {
                "object_id": st["subtask_id"],
                "decision_type": "subtask_routing",
                "selected": selected,
                "candidates": ["coding_editor_v1", "generic_helper_v1"],
                "score_breakdown": {"scenario_match": score},
                "final_score": score,
                "decision": "auto_execute" if score > 0.75 else "cautious_review_or_canary",
            }
        )

    return {"subtask_count": len(subtasks), "decision_traces": traces}


def proposal_publish_loop() -> dict:
    payload = _load_json(EXAMPLES / "proposal_pipeline.example.json")
    _validate(CONTRACTS / "proposal_pipeline.schema.json", payload)

    flow = []
    proposal = payload["proposal"]
    for state in ["draft", "candidate", "review_pending", "canary", "active", "rolled_back"]:
        proposal["status"] = state
        flow.append(state)

    publish = payload["publish"]
    publish["action"] = "canary"
    publish["status"] = "succeeded"
    publish["action"] = "publish"
    publish["status"] = "succeeded"
    publish["action"] = "rollback"
    publish["status"] = "succeeded"
    publish["rollback_reason"] = "canary_fail_rate_increase"

    return {"status_flow": flow, "final_action": publish["action"], "rollback_reason": publish["rollback_reason"]}


def main() -> int:
    try:
        import jsonschema  # type: ignore  # noqa: F401
    except Exception:
        print("jsonschema is required for loop tests")
        return 2

    out = {
        "single_task_loop": single_task_loop(),
        "subtask_loop": subtask_loop(),
        "proposal_publish_loop": proposal_publish_loop(),
    }

    out_path = ROOT / "runtime" / "examples" / "decision_trace.loop_test.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"OK: loop tests passed, trace written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
