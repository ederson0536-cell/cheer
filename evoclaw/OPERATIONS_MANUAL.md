# EvoClaw Runtime 落地实施手册

> 目标：把现有 contracts + validators + 样本集，变成可持续执行的日常运维流程（不是一次性跑完）。

## 1. 落地原则（如何保证实施）

要保证实施，核心是 **“固定节奏 + 固定门禁 + 固定产物”**：

- 固定节奏：按日/按周定时运行检查。
- 固定门禁：`regression_report.json` 出现 `fail` 直接阻断发布。
- 固定产物：每轮都必须产出 trace/report，避免“口头说跑过”。

---

## 2. 推荐定时任务（Cron）

## 2.1 每日（staging 健康巡检）

建议每天运行：

1. contract 校验
2. 闭环测试（含 failure injection）
3. 真实样本包测试
4. 回归报告生成
5. staging trial（低风险样本）

示例（每日 09:10）：

```bash
10 9 * * * cd /workspace/cheer && \
  python3 evoclaw/validators/validate_runtime_contracts.py && \
  python3 evoclaw/validators/test_runtime_loops.py && \
  python3 evoclaw/validators/test_real_sample_package.py && \
  python3 evoclaw/validators/generate_regression_report.py && \
  python3 evoclaw/validators/staging_trial_run.py
```

## 2.2 每周（回归与基线复核）

示例（周一 09:30）：

```bash
30 9 * * 1 cd /workspace/cheer && \
  python3 evoclaw/validators/generate_regression_report.py
```

建议周会固定查看：
- `baseline.layered_dashboard.json`
- `regression_report.json`
- `decision_trace.loop_test.json`

---

## 3. 发布门禁（Go / No-Go）

发布前至少满足：

- `regression_report.json.summary.fail == 0`
- 脏输入中 `expected=fail` 的样本不得误判为 `pass`
- staging trial 无新增高风险异常

建议策略：

- **Go**：`fail=0` 且 warning 可解释
- **No-Go**：`fail>0`
- **Canary-Only**：`fail=0` 但 warning 明显上升

---

## 4. 详细使用手册（一步一步）

## 4.0 验证器清单确认（避免“脚本不存在”）

先确认本地可用验证器：

```bash
cd /workspace/cheer
find evoclaw/validators -maxdepth 1 -type f -name "*.py" | sort
```

> 当前仓库同时包含：
> - Runtime validators（如 `validate_runtime_contracts.py`、`test_runtime_loops.py`）
> - EvoClaw pipeline validators（如 `validate_experience.py`、`validate_reflection.py`、`validate_proposal.py` 等）

## 4.1 初始化检查

```bash
cd /workspace/cheer
python3 evoclaw/validators/validate_runtime_contracts.py
```

## 4.2 跑路由评分并产出决策 trace

```bash
python3 evoclaw/runtime/routing_score.py \
  evoclaw/runtime/examples/skill_registry.example.json \
  evoclaw/runtime/examples/routing_weights.example.json \
  evoclaw/runtime/examples/decision_trace.from_routing.json
```

## 4.3 跑三闭环（含 failure injection + 分层看板）

```bash
python3 evoclaw/validators/test_runtime_loops.py
```

产物：
- `evoclaw/runtime/examples/decision_trace.loop_test.json`
- `evoclaw/runtime/examples/baseline.layered_dashboard.json`

## 4.4 跑真实样本包

```bash
python3 evoclaw/validators/test_real_sample_package.py
```

产物：
- `evoclaw/runtime/examples/decision_trace.real_sample.json`

## 4.5 生成回归判定报告（pass/warning/fail）

```bash
python3 evoclaw/validators/generate_regression_report.py
```

产物：
- `evoclaw/runtime/examples/regression_report.json`

## 4.6 staging 试运行

```bash
python3 evoclaw/validators/staging_trial_run.py
```

产物：
- `evoclaw/runtime/examples/staging_trial_report.json`

---

## 5. 目录树（关键目录）

```text
evoclaw/
├── OPERATIONS_MANUAL.md
├── runtime/
│   ├── README.md
│   ├── routing_score.py
│   ├── contracts/
│   │   ├── task_subtask.schema.json
│   │   ├── skill_registry.schema.json
│   │   ├── proposal_pipeline.schema.json
│   │   ├── decision_trace.schema.json
│   │   ├── memory_contract.yaml
│   │   ├── canonical_field_dictionary.yaml
│   │   ├── expectations/
│   │   │   └── failure_injection_expectations.json
│   │   └── service/
│   │       └── persistence_boundary.yaml
│   └── examples/
│       ├── baseline.layered_dashboard.json
│       ├── regression_report.json
│       ├── staging_trial_report.json
│       ├── decision_trace.*.json
│       ├── golden/
│       │   ├── golden_manifest.json
│       │   └── *.json
│       └── dirty/
│           ├── dirty_manifest.json
│           └── *.json
└── validators/
    ├── validate_runtime_contracts.py
    ├── test_runtime_loops.py
    ├── test_real_sample_package.py
    ├── generate_regression_report.py
    └── staging_trial_run.py
```

---

## 6. 常见执行策略

- 先 `validate_runtime_contracts.py`，再跑其它测试。
- 每次改 schema/router/policy/gate 参数都跑 golden + dirty。
- 回归报告中 `fail` 不为 0 时，禁止推进发布。
- 每周至少一次审阅 `baseline.layered_dashboard.json` 的分层指标。
