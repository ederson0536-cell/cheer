# Runtime Contracts (Executable Artifacts)

This folder contains executable artifacts extracted from `SYSTEM_FRAMEWORK_PROPOSAL.md`.

Core contracts and references:
- `contracts/task_subtask.schema.json`
- `contracts/skill_registry.schema.json`
- `contracts/memory_contract.yaml`
- `contracts/proposal_pipeline.schema.json`
- `contracts/decision_trace.schema.json`
- `contracts/canonical_field_dictionary.yaml`

Key examples:
- `examples/task_subtask.example.json`
- `examples/skill_registry.example.json`
- `examples/proposal_pipeline.example.json`
- `examples/decision_trace.example.json`
- `examples/golden/` (golden regression suite)

Validators and loop tests:
- `evoclaw/validators/validate_runtime_contracts.py`
- `evoclaw/validators/test_runtime_loops.py`
- `evoclaw/validators/test_real_sample_package.py`

## Quick checks

```bash
python3 evoclaw/validators/validate_runtime_contracts.py
python3 evoclaw/runtime/routing_score.py evoclaw/runtime/examples/skill_registry.example.json evoclaw/runtime/examples/routing_weights.example.json evoclaw/runtime/examples/decision_trace.from_routing.json
python3 evoclaw/validators/test_runtime_loops.py
python3 evoclaw/validators/test_real_sample_package.py
```

## Generated outputs

- `examples/decision_trace.loop_test.json`
- `examples/baseline.layered_dashboard.json`
- `examples/decision_trace.real_sample.json`
