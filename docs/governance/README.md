# GRIP Governance Stack

## Purpose

This folder contains the six governing documents for the GRIP project (Geopolitical Resilience Intelligence Platform). These documents were produced in a structured design session before any implementation code was written. They define the project's scope, constraints, terminology, architecture, and execution sequence.

**No implementation work may begin without reading this stack first.** No architectural decision may be made that contradicts these documents without updating the relevant document and noting the change. The documents form a hierarchy — when they conflict, the higher-authority document wins.

This is not documentation about the code. This is the constitutional layer that governs what the code is allowed to be.

---

## Authority Order

Documents are listed in descending authority. When two documents disagree, the higher-numbered authority wins.

| Authority | Document | Self-declared scope |
|---|---|---|
| **1 (highest)** | `03-grip-source-of-truth.md` | "This document governs all implementation decisions for the GRIP project. Where any prior document conflicts with this document, this document wins." |
| **2** | `04-grip-system-architecture.md` | "This document specifies the target system architecture. All implementation must conform to it. Deviations require updating this document first." |
| **3** | `05-grip-mission-program.md` | "No mission may begin until its prerequisites are met. No mission is 'done' until its completion criteria are satisfied. No phase gate is crossed until all missions in the phase pass." |
| **4** | `02-grip-master-execution-plan.md` | "This document supersedes the Build Brief and Product Specification for all implementation decisions. Those documents remain valid as strategic context." |
| **5** | `01-grip-product-spec.md` | Predecessor context. Defines schema, forecast targets, and dashboard workflow. Superseded by Execution Plan and Source of Truth where they diverge. |
| **6 (lowest)** | `00-grip-build-brief.md` | Predecessor context. Original strategic framing and problem statement. Superseded by all later documents. |

---

## Document Index

| File | Role | Lines | Governs | Use when | Must not override |
|---|---|---|---|---|---|
| `00-grip-build-brief.md` | Strategic context | 513 | Problem framing, target users, analytical layers, "why this matters" | Understanding why the project exists, what it demonstrates, what portfolio value it carries | Nothing — this is the lowest-authority document |
| `01-grip-product-spec.md` | Analytical design | 542 | Entity schema (original), forecast targets (original), dashboard workflow, descriptive/forecast/scenario classification | Understanding analytical methodology, entity relationships, and the reasoning behind structural choices | Nothing — predecessor document |
| `02-grip-master-execution-plan.md` | Reconciled planning | 562 | Region decision (Baltic), forecast target confirmation, DAG-as-physical-topology decision, phased build sequence, verified infrastructure status (Estlink 2, LitPol, Harmony Link), assumptions register | Planning implementation phases, understanding what changed from prior documents and why, infrastructure reference data | Source of Truth, System Architecture |
| `03-grip-source-of-truth.md` | **Law** | 274 | Non-negotiable constraints (N1–N14), out-of-scope items (X1–X12), critical assumptions (A1–A8), architecture principles (P1–P10), canonical glossary, domain definitions (8+1), resolved contradictions, binding decisions (D1–D8) | **Every decision.** Consult first when uncertain. All terminology defined here is canonical. | Nothing — this is the highest authority |
| `04-grip-system-architecture.md` | Implementation contract | 928 | Functional requirements (ING, SCR, SIM, FCT, API, DSH — 30+ testable requirements), non-functional requirements (NFR-1 through NFR-10), logical architecture (5 layers), component map with rationale/tradeoff for each decision, data flow, state transitions, external integrations, error handling, observability, folder structure | Implementing any component. Every architecture decision includes rationale, tradeoff, dependency impact, and implementation consequence. | Source of Truth |
| `05-grip-mission-program.md` | Execution contract | 919 | 37 missions across 5 phases, each with objective, prerequisites, inputs, outputs, files affected, risks, validation, completion criteria. Parallel-safe groups, human-review checkpoints, rework warnings, artifact-review gates. | Knowing what to build next, in what order, with what acceptance criteria. Every mission has a "done" definition. | Source of Truth, System Architecture |

---

## Conflict Resolution Rules

### Rule 1: Authority order resolves conflicts

If the Source of Truth says one region and the Build Brief says three regions, the answer is one region. If the System Architecture says logistic regression and the Product Spec says GBM, the answer is logistic regression. Authority descends from `03` → `04` → `05` → `02` → `01` → `00`.

### Rule 2: Later documents incorporate and supersede earlier ones

The Master Execution Plan (02) explicitly states it "supersedes the Build Brief and Product Specification for all implementation decisions." The Source of Truth (03) resolved eight named contradictions between prior documents. Those resolutions are binding.

### Rule 3: Specificity wins within the same authority level

If the System Architecture provides a detailed functional requirement (e.g., API-4: "POST with overrides returns current_state, simulated_state, cascade_trace") and the Mission Program references the same endpoint less precisely, the Architecture's specification governs the implementation.

### Rule 4: Silence is not permission

If a topic is not addressed in the governance stack, the builder should raise it as an open question — not assume the answer. The Source of Truth's out-of-scope list (X1–X12) and constraint list (N1–N14) define hard boundaries. Anything not explicitly permitted by the constraints and not excluded by the out-of-scope list may be in scope, but the builder should verify before investing time.

### Rule 5: Updating a governance document requires deliberate action

If implementation reveals that a governance document is wrong (a config schema doesn't work, a functional requirement is infeasible, an assumption fails validation), the correct response is: update the governance document first, then implement. Do not silently deviate and explain later.

---

## Build Implications

These are the binding architectural and process constraints extracted from the governance stack. Every one is traceable to a specific document and section.

### Scope locks

- **One region only:** Baltic-Nordic energy corridor (FI, EE, LV, LT). No other regions in any phase. *(Source of Truth N1)*
- **One primary forecast target:** Critical interconnector disruption probability, 30-day rolling window. *(Source of Truth N2)*
- **Batch data only:** No streaming, no websockets, no sub-hourly claims. *(Source of Truth N3)*
- **All data sources free and open:** No paid APIs. A reviewer can reproduce the pipeline without paying. *(Source of Truth N4)*

### Architecture rules

- **Configuration over code:** Weights, thresholds, topology, and scenarios live in JSON config files, not in Python source. *(Source of Truth P1)*
- **Topology is the model:** The infrastructure DAG is the physical network, not a statistical estimate. Cascade logic is capacity arithmetic. *(Source of Truth P4, System Architecture §7 Simulation Engine)*
- **Forecasts and scenarios are separate systems:** They share no code paths, occupy separate API routes, and render in separate dashboard views. *(Source of Truth N8, P5)*
- **Frontend performs zero analytics:** Every number on screen comes from the API. The dashboard does layout, color, and interaction — never scoring or inference. *(System Architecture §7 Presentation Layer, DSH-6)*
- **Engines are pure functions:** Scoring, cascade, and risk model receive DataFrames/dicts and return DataFrames/dicts. No SQLAlchemy imports in engine modules. No HTTP calls. No side effects. *(System Architecture §6)*
- **Seed data enables full demo:** `DEMO_MODE=true` runs the complete system from committed seed data with no external calls. *(Source of Truth N14, P2)*

### Process rules

- **Engine before dashboard:** No frontend code is written until scoring, simulation, and forecasting engines are tested. *(Source of Truth P10, Mission Program phase gates)*
- **Validation before polish:** The backtest notebook (M28) must be complete before dashboard views are built. *(Mission Program Phase 4 gate)*
- **Scenario and forecast separation:** These are never conflated in UI, API, or documentation. A scenario carries no probability of occurrence. A forecast always carries confidence intervals. *(Source of Truth N8, Decision D7)*
- **Honest failure beats cosmetic success:** If the risk model can't beat the base rate, document this. The backtest notebook is a portfolio asset regardless of the result. *(Source of Truth P9)*

---

## Missing Documents

**Status: All six governance documents are present and accounted for.**

| Expected file | Status | Notes |
|---|---|---|
| `00-grip-build-brief.md` | ✅ Present | 513 lines. Strategic context. Lowest authority. |
| `01-grip-product-spec.md` | ✅ Present | 542 lines. Analytical design predecessor. |
| `02-grip-master-execution-plan.md` | ✅ Present | 562 lines. Reconciled planning document. |
| `03-grip-source-of-truth.md` | ✅ Present | 274 lines. Highest authority. |
| `04-grip-system-architecture.md` | ✅ Present | 928 lines. Implementation contract. |
| `05-grip-mission-program.md` | ✅ Present | 919 lines. Execution contract. |

**Total governance corpus:** 3,738 lines across six documents.

If any of these files become unavailable in a future session, the minimum viable governance set is `03` + `04` + `05` (Source of Truth + Architecture + Mission Program). These three contain sufficient constraint, structure, and sequencing information to execute the build. The loss of `00`, `01`, or `02` degrades strategic context but does not block implementation.

---

## Recommended Repository Placement

```
grip/
├── docs/
│   ├── governance/                          ← This folder
│   │   ├── README.md                        ← This file
│   │   ├── 00-grip-build-brief.md
│   │   ├── 01-grip-product-spec.md
│   │   ├── 02-grip-master-execution-plan.md
│   │   ├── 03-grip-source-of-truth.md
│   │   ├── 04-grip-system-architecture.md
│   │   └── 05-grip-mission-program.md
│   ├── methodology.md                       ← Produced during M29
│   ├── data-dictionary.md                   ← Produced during M29
│   ├── infrastructure-topology.md           ← Produced during M29
│   ├── backtesting-report.md                ← Produced during M29
│   ├── limitations.md                       ← Produced during M29
│   └── assumptions-register.md              ← Produced during M29
```

The `docs/governance/` folder is read-only during implementation. Changes require deliberate review (see Rule 5 above). The `docs/` root contains working documentation produced during the build (Mission M29) which is informed by but distinct from the governance stack.

---

## Contributor Start Here

### If you are a new contributor or reviewer

1. **Read `03-grip-source-of-truth.md` first.** This is 274 lines and takes 10 minutes. It contains the glossary, constraints, domain definitions, and all binding decisions. After reading it, you will know what the project is, what it is not, and what terminology to use.

2. **Read `04-grip-system-architecture.md` second.** This is the implementation contract. Sections 4 (functional requirements), 6 (logical architecture), and 7 (component map) are the most important. Each architecture decision includes its rationale, tradeoff, and implementation consequence.

3. **Read `05-grip-mission-program.md` third.** This tells you the build sequence, what each mission produces, and what "done" means for each one. Section at the end covers parallelism, human-review checkpoints, and rework risks.

4. **Skim `02-grip-master-execution-plan.md` for context.** This explains why the Baltic corridor was chosen, what infrastructure data is available, and what was verified via web search. It also contains the assumptions register (v1.0).

5. **Reference `01` and `00` only if you need strategic background.** These are predecessor documents. They are useful for understanding the design reasoning but are superseded for all implementation decisions.

### If you are Gavin resuming work in a new session

1. Re-read `03-grip-source-of-truth.md` to re-anchor terminology and constraints.
2. Check which mission you last completed in `05-grip-mission-program.md`.
3. Verify the phase gate criteria for your current phase.
4. Proceed to the next mission.

---

## Antigravity Working Rules

These rules govern how a build agent (Claude, Antigravity, or any AI coding assistant) should behave when planning or implementing against this governance stack.

### Before any implementation

1. Read `03-grip-source-of-truth.md` in full. Internalize the glossary, constraints (N1–N14), exclusions (X1–X12), principles (P1–P10), and decisions (D1–D8).
2. Read the relevant mission from `05-grip-mission-program.md`. Note its prerequisites, inputs, outputs, files affected, risks, and completion criteria.
3. If the mission involves an architecture decision, consult `04-grip-system-architecture.md` for the rationale, tradeoff, and implementation consequence.

### During implementation

4. Do not create files outside the directory structure defined in `04-grip-system-architecture.md` §16 without updating the architecture document first.
5. Do not add dependencies not listed in `pyproject.toml` (Mission M01) without justification.
6. Do not hardcode analytical parameters (weights, thresholds, capacities) in Python source. They belong in `config/*.json` (Principle P1).
7. Do not import SQLAlchemy in engine modules (`scoring/`, `simulation/`, `forecasting/`). Engines receive DataFrames and return DataFrames (Architecture §6).
8. Do not write frontend code before the Phase 4 gate passes (P10, Mission Program phase gates).

### When encountering a conflict

9. Check the authority order. The higher-authority document wins.
10. If no governance document addresses the question, flag it as an open question — do not assume.
11. If implementation reveals a governance document is wrong, propose an update to the document. Do not silently deviate.

### When completing a mission

12. Verify every completion criterion listed in the mission.
13. Run `pytest` for all affected test files.
14. Commit with a message referencing the mission ID (e.g., `M12: domain scoring engine`).
15. If the mission is flagged for human review, stop and request review before proceeding.

### Content preservation (Antigravity prompt rule)

Per standing Antigravity rules: every redesign, cleanup, or refactor prompt must open with a content-preservation block. No deleting charts, tables, KPIs, simulations, or analytical components. "Demote" means move to expander. "Reduce" means tighten labels. "Cut" means prose only, never visuals. Confirm content renders after every change.

---

## Quick Reference: Key Numbers

| Metric | Value | Source |
|---|---|---|
| Focus countries | 4 (FI, EE, LV, LT) | Source of Truth §B1 |
| Context countries | 4 (SE, PL, RU, DE) | Source of Truth §B1 |
| Scored domains | 8 + 1 composite | Source of Truth §7 |
| Forecast target | P(interconnector disruption within 30 days) | Source of Truth §B2 |
| Backtesting events | 12 total, 6 energy-interconnector positive labels | Execution Plan §A, Source of Truth §B2 |
| Pre-built scenarios | 6 | Source of Truth §B4 |
| API endpoint groups | 5 (state, topology, scenario, forecast, meta) | Architecture §7 |
| Dashboard views | 5 | Architecture §7 |
| Total missions | 37 across 5 phases | Mission Program |
| Non-negotiable constraints | 14 | Source of Truth §2 |
| Permanent exclusions | 12 | Source of Truth §3 |
| Architecture principles | 10 | Source of Truth §5 |

---

*This README was generated during the governance-stack anchoring pass. It should be the first file read in any new build session.*
