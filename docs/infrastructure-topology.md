# Baltic-Nordic Infrastructure Topology

## Overview

The Baltic-Nordic energy grid forms a **serial chain** running from Finland south
through Estonia, Latvia, and Lithuania, with lateral connections to Sweden and Poland.
This linear topology creates distinctive vulnerability patterns: severing any link
in the chain isolates downstream countries from Nordic generation capacity.

```
                    ┌─────────┐
                    │ FINLAND │  (Nuclear: Olkiluoto 3 = 1,650 MW)
                    │  (FI)   │
                    └────┬────┘
                         │
              Estlink 1 (358 MW) ── submarine cable
              Estlink 2 (650 MW) ── submarine cable  ⚠️ SPOF #1
                         │
                    ┌────┴────┐
     ┌──────────────│ ESTONIA │
     │              │  (EE)   │
     │              └────┬────┘
     │                   │
Balticconnector    EE-LV Electric (1,500 MW)
(gas, 7.2 mcm/d)        │
  ⚠️ SPOF #2       ┌────┴────┐
     │              │ LATVIA  │
     │              │  (LV)   │
     │              └────┬────┘
     │                   │
     │              LV-LT Electric (1,500 MW)
     │                   │
     │              ┌────┴────┐
     └──────────────│LITHUANIA│──── LitPol Link (500 MW) ──── POLAND
                    │  (LT)   │
                    └────┬────┘
                         │
                    NordBalt (700 MW) ── submarine cable ⚠️ SPOF #3
                         │
                    ┌────┴────┐
                    │ SWEDEN  │
                    │ (SE-4)  │
                    └─────────┘
```

## Key Infrastructure

### Electric Interconnectors

| ID | Route | Capacity (MW) | Type | Submarine? | Status |
|----|-------|--------------|------|------------|--------|
| `estlink_1` | FI → EE | 358 | HVDC | Yes (105 km) | Operational |
| `estlink_2` | FI → EE | 650 | HVDC | Yes (170 km) | Operational (returned Apr 2025) |
| `ee_lv_electric` | EE → LV | 1,500 | AC | No | Operational |
| `lv_lt_electric` | LV → LT | 1,500 | AC | No | Operational |
| `nordbalt` | SE → LT | 700 | HVDC | Yes (450 km) | Operational |
| `litpol_link` | PL → LT | 500 | HVDC | No | Operational |

### Gas Infrastructure

| ID | Route | Capacity (mcm/day) | Type | Notes |
|----|-------|-------------------|------|-------|
| `balticconnector` | FI ↔ EE | 7.2 | Offshore pipeline | Severed Oct 2023, repaired Apr 2024 |
| `kiemenai` | Entry → LV | 6.0 | Pipeline | Latvia-Lithuania interconnection area |
| `gipl` | PL → LT | 2.4 | Pipeline | Gas Independence Pipeline (2022) |
| `klaipeda_lng` | LNG → LT | 3.5 | FSRU terminal | Independence FSRU |

### Planned Infrastructure

| Name | Route | Capacity | Status | Expected |
|------|-------|----------|--------|----------|
| Estlink 3 | FI → EE | ~700 MW | Planning | ~2035 |
| Harmony Link | PL → LT | 700 MW | Under construction | ~2028 |
| Baltic Wind Farm connections | Offshore → EE/LV | Variable | Planning | 2030+ |

## Single Points of Failure (SPOFs)

### SPOF #1: Estlink Submarine Cables

The two Estlink cables (combined 1,008 MW) are the **only** electric connection
between Finland and the Baltic states. Both are submarine cables in the Gulf of
Finland — a shallow, high-traffic waterway.

**Impact of loss:**
- Estlink 2 alone (650 MW): Estonia loses ~35% of import capacity.
  N-1 margin drops significantly. Demonstrated Dec 25, 2024 (Eagle S incident).
- Both Estlinks (1,008 MW): Estonia completely isolated from Nordic generation.
  Must rely solely on internal generation + southward flows from Latvia/Lithuania.
  Demonstrated Jan 20, 2026 (Kiisa battery fault).

**Vulnerability:** Submarine cables are exposed to anchor dragging, sabotage,
and seabed damage. The Gulf of Finland's shallow depth (60-100m) makes cables
accessible to surface vessel anchors.

### SPOF #2: Balticconnector Gas Pipeline

The only gas pipeline connecting Finland to the Baltic gas network. Runs 77 km
along the seabed of the Gulf of Finland.

**Impact of loss:** Finland loses its only pipeline gas supply from the Baltics.
Must rely entirely on LNG imports and domestic storage. Demonstrated Oct 8, 2023,
when the Newnew Polar Bear's anchor severed the pipeline and the parallel
Estonia-Finland telecom cable simultaneously.

### SPOF #3: NordBalt Cable

The only electric connection between Sweden and Lithuania (700 MW). Runs 450 km
under the Baltic Sea — the longest submarine cable in the Baltic.

**Impact of loss:** Lithuania loses its direct Nordic connection. Must rely on
LitPol Link (500 MW to Poland) and northward flows from Latvia.
Suspected anchor damage Nov 17, 2024.

### SPOF #4: Serial Chain Topology

The EE → LV → LT overland connections form a serial chain. While each link has
high capacity (1,500 MW), the topology means that a disruption anywhere in the
chain cascades structurally. Combined with submarine cable outages, this creates
compound failure scenarios.

### SPOF #5: Gulf of Finland Cable Corridor

Estlink 1, Estlink 2, Balticconnector, and the C-Lion1 telecom cable all traverse
the same narrow corridor in the Gulf of Finland. A single vessel dragging an anchor
through this corridor could damage multiple critical connections simultaneously —
as nearly occurred in the Eagle S incident (Dec 2024).

## Documented Disruption Events

| Date | Event | Infrastructure | Impact |
|------|-------|---------------|--------|
| 2023-10-08 | Balticconnector anchor damage | Gas pipeline | Finland gas supply cut for 6 months |
| 2024-01-26 | Estlink 2 technical fault | Electric cable | 650 MW lost for several weeks |
| 2024-11-17 | NordBalt suspected anchor damage | Electric cable | 700 MW capacity reduced |
| 2024-12-25 | Eagle S multi-cable severing | Estlink 2 + telecom | 650 MW + telecom lost |
| 2025-09-01 | Estlink 1 outage | Electric cable | 358 MW lost |
| 2026-01-20 | Kiisa battery fault | Both Estlinks trip | 1,008 MW total loss |

## N-1 Security Criterion

The Baltic synchronous area applies the N-1 security criterion: the system must
maintain stability after the loss of the single largest infeed. For the Baltics:

- **Reserve requirement:** ~1,500 MW across FI/EE/LV/LT (500 MW per Baltic state)
- **Largest single contingency:** Olkiluoto 3 (1,650 MW) or both Estlinks (1,008 MW)
- **Post-BRELL desynchronization (2025):** Baltic states desynchronized from the
  Russian grid, making Nordic connections even more critical

The GRIP margin calculator computes:
```
margin = generation + available_imports - demand - reserve - largest_single_failure
```

A negative margin indicates the N-1 criterion is violated.
