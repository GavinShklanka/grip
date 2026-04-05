# GRIP — Antigravity Intake Protocol

## Read before any build work

### Step 1: Ingest governance stack in this order

1. `03-grip-source-of-truth.md` — Constraints, glossary, decisions. **Law.**
2. `04-grip-system-architecture.md` — Components, requirements, data flow. **Implementation contract.**
3. `05-grip-mission-program.md` — 37 missions, phases, completion criteria. **Execution contract.**
4. `02-grip-master-execution-plan.md` — Baltic corridor data, verified infrastructure status. **Planning reference.**
5. `00-grip-build-brief.md` — Strategic context. **Background only.**
6. `01-grip-product-spec.md` — Original analytical design. **Background only.**

### Step 2: Anchor on these non-negotiable rules

- One region: Baltic-Nordic (FI, EE, LV, LT)
- One forecast target: P(interconnector disruption within 30 days)
- Batch data only — no streaming, no real-time claims
- All data sources free and open
- Config over code: weights, thresholds, topology in JSON, not Python
- Topology is the model: DAG = physical infrastructure, cascade = capacity arithmetic
- Engines are pure functions: DataFrames in, DataFrames out, no DB imports
- Forecasts and scenarios are separate: separate code, separate API routes, separate views
- Frontend computes nothing: every displayed number comes from the API
- Seed data enables full demo: DEMO_MODE=true works offline
- Build order: engine → validation → dashboard (enforced by phase gates)
- Honest failure > cosmetic success

### Step 3: Identify current mission

Check which mission to execute next. Do not skip prerequisites. Do not begin Phase N+1 before Phase N gate passes.

### Step 4: Execute

Produce files. Run tests. Verify completion criteria. Commit.

### Conflict resolution

Source of Truth > Architecture > Mission Program > Execution Plan > Product Spec > Build Brief.
If uncertain, flag as open question. Do not assume.

### Content preservation rule

Every redesign/cleanup/refactor MUST open with a content preservation block. No deleting charts, tables, KPIs, simulations, or analytical components. "Demote" = expander. "Reduce" = tighten labels. "Cut" = prose only, never visuals.
