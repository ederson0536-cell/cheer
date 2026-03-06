# Runtime Contracts (Executable Artifacts)

This folder contains the first 4 implementation artifacts extracted from `SYSTEM_FRAMEWORK_PROPOSAL.md`:

1. **Task / Subtask schema**
   - `contracts/task_subtask.schema.json`
   - `examples/task_subtask.example.json`

2. **Skill Registry + Routing Score**
   - `contracts/skill_registry.schema.json`
   - `routing_score.py`
   - `examples/skill_registry.example.json`

3. **Memory write/read contract**
   - `contracts/memory_contract.yaml`

4. **Proposal -> Review -> Publish flow**
   - `contracts/proposal_pipeline.schema.json`
   - `examples/proposal_pipeline.example.json`

Additional governance/debug artifacts:
- `contracts/canonical_field_dictionary.yaml`
- `contracts/decision_trace.schema.json`
- `examples/decision_trace.example.json`

## Quick checks

```bash
python3 evoclaw/validators/validate_runtime_contracts.py
python3 evoclaw/runtime/routing_score.py evoclaw/runtime/examples/skill_registry.example.json evoclaw/runtime/examples/routing_weights.example.json evoclaw/runtime/examples/decision_trace.from_routing.json
python3 evoclaw/validators/test_runtime_loops.py
python3 evoclaw/validators/test_real_sample_package.py
```
