# 04 — SYSTEM DESIGN v2 (manufacturing)

Rule kept: **the implemented pipeline is not replaced, it is extended.** Status labels: IMPLEMENTED / MODELLED / FUTURE.

---

## 1. Block diagram (description for figure 3.1)

```
 IMPLEMENTED (edge node, Review 3)                       NEW in v2
 ┌────────┐  ┌──────┐  ┌──────────┐  ┌──────────────┐   ┌────────────────────┐
 │ Camera │→ │ V4L2 │→ │GStreamer │→ │ nvstreammux  │ → │ nvinfer ResNet10   │
 │ (C920 /│  └──────┘  └──────────┘  └──────────────┘   │ TensorRT FP16      │
 │  RTSP) │                                             └─────────┬──────────┘
 └────────┘                                                       ↓
                                           ┌──────────────────────────────────────┐
                                           │ nvdsanalytics ROIs (MODELLED→FUTURE) │
                                           │  ROI_k = operator zone of machine k   │
                                           │  Z_j   = floor zone j (aisle, bay)    │
                                           └──────────────────┬───────────────────┘
   CT clamp per machine (SCT-013) ──► ADC / Modbus meter ─────┤  machine activity a_k(t)
                                                              ↓
                       ┌────────────────────────────────────────────────────────┐
                       │ Temporal filter (rise/fall hold)   IMPLEMENTED (v1)     │
                       │ Machine state machine per k         MODELLED (v2)       │
                       │ Zone state machine per j            MODELLED (v1 logic) │
                       └───────────────┬────────────────────────────────────────┘
                                       ↓
                 ┌─────────────────────┴────────────────────┐
                 │ Action layer                              │
                 │  ADVISORY: dashboard alert to supervisor  │  MODELLED (+ demo)
                 │  AUTO (whitelist): relay / Modbus / VFD / │  FUTURE (PROFIenergy)
                 │        PROFIenergy Start_Pause            │
                 └─────────────────────┬────────────────────┘
                                       ↓
       live_state.json → MQTT 5.0 → dashboard: kW, kWh, ₹ (energy + demand), kVA, CO₂, idle-energy ratio
```

Only metadata (counts, states, kW) leaves the node. No frames stored.

## 2. Inputs per machine k and zone j

| Signal | Meaning | Source | Status |
|---|---|---|---|
| o_k(t) ∈ {0,1} | Operator present in machine ROI | ResNet10 person detections inside ROI_k | Detector IMPLEMENTED, ROI MODELLED |
| a_k(t) ∈ {0,1} | Machine active (cutting / cycling) | CT clamp current I_k > I_th (fusion) | MODELLED, demo FUTURE |
| n_j(t) | Persons in floor zone j | Person count in Z_j | Count IMPLEMENTED, zones MODELLED |
| p_k(t) (optional) | Part present on fixture | Object class / motion in ROI | FUTURE |

Why fusion: the camera cannot see cutting inside a closed enclosure, and a CT clamp cannot see whether a person is present. Together they separate "idle but attended" (no action) from "idle and abandoned" (act).

## 3. Machine state machine (replaces the 4-state room machine)

| State | Condition (after temporal filter) | Power (assumed, see assumptions.yaml) | Action |
|---|---|---|---|
| PROCESSING | a_k = 1 | P_proc = 7.5 kW | none |
| IDLE-ATTENDED | a_k = 0 and o_k = 1 | P_idle = 3.0 kW | none (set-up, measuring, tool change) |
| IDLE-UNATTENDED | a_k = 0 and o_k = 0 for t > T1 (3 min, chosen from S7) | P_sb = 1.2 kW (coolant pump, chip conveyor, hydraulics, lamp off; control and thermal control on) | ADVISORY alert; AUTO standby if whitelisted |
| DEEP STANDBY | unattended for t > T2 (30 min) **and** machine on whitelist | P_ds = 0.35 kW (CNC control only) | AUTO deep standby; operator restarts |

Transitions and filter:
- Presence rise hold 10 s (fast to serve the operator), presence fall hold 60 s (operator steps away briefly).
- Activity from CT: on if I_k > I_th for 5 s; off if below for 30 s.
- Any return of o_k = 1 or a_k = 1 → back to IDLE-ATTENDED / PROCESSING. **The node never starts a machine.** Leaving standby needs an operator action (machinery-safety principle).
- Warm-up penalty: leaving DEEP STANDBY costs E_wu = P_idle × t_wu (t_wu = 10 min assumed) because thermal stabilisation is needed. This is charged in the model, so the timer study (S7) is honest.

Whitelist (reference shop): 6 of 10 machines are general-purpose (AUTO allowed for standby and deep standby); 4 are precision machines (ADVISORY only, standby allowed only on supervisor click; never deep standby).

ADVISORY compliance (model): a supervisor acts on a fraction c = 0.6 of alerts after a delay of 3 min (assumed, swept).

## 4. Multi-load actions from the same occupancy map

| Load | Baseline (no node) | Rule with node | Mode |
|---|---|---|---|
| CNC machines (10) | ON whole shift; idle at P_idle during waits, breaks, breakdowns; 30 % left idle overnight | state machine above | AUTO (6), ADVISORY (4) |
| Conveyor line (2.2 kW) | runs whole shift | stop when no machine on the line is PROCESSING and line zone empty for > 2 min | AUTO |
| Compressor (22 kW screw, load/unload) | runs whole shift; unloaded power 30 % of full | demand follows active machines; when whole shop idle > 5 min, isolate line valve and stop compressor (leak load removed) | AUTO |
| High-bay lighting (4 zones × 3.6 kW LED) | all ON during shifts | zone empty > 2 min → dim to 10 % (aisle safety) | AUTO |
| Extraction fans (4 × 3.7 kW, one per zone) | ON whole shift | zone has no PROCESSING machine and empty > 5 min → OFF | AUTO |

## 5. Two operating modes
- **ADVISORY** (default for any new site and any precision/thermal process): the dashboard shows "M7 unattended 6 min, 3.0 kW, ₹/h lost" and the supervisor decides.
- **AUTO** (whitelist only): node sends a pause command (relay, Modbus coil, VFD stop, or PROFIenergy Start_Pause). Never furnaces, moulding barrels, heat treatment, or any machine with a cycle in progress.

## 6. Electrical KPIs
| KPI | Equation | Why |
|---|---|---|
| Energy | E = Σ P(t)·Δt | kWh bill |
| Energy cost | C_E = E × ₹7.50 | TN HT-I energy charge |
| Max demand | MD = max over 15-min blocks of mean P / PF | HT bill demand (kVA) |
| Demand cost | C_D = max(MD, 0.9 × CD) × ₹608 per month | TN HT-I |
| Load factor | LF = P_avg / P_peak | utilisation of supply |
| Idle-energy ratio (EnPI) | IER = E_non-processing / E_total | ISO 50006 style indicator |
| CO₂ | E_saved × 0.710 kg/kWh | CEA v21 |

## 7. What is IMPLEMENTED / MODELLED / FUTURE
| Item | Status |
|---|---|
| Jetson Nano + C920 + DeepStream + TensorRT FP16 + ResNet10 person detector | IMPLEMENTED |
| Person count, temporal filter, live_state.json, dashboard | IMPLEMENTED |
| Machine/zone ROIs (nvdsanalytics), machine state machine, multi-load rules | MODELLED (sim_v2) |
| CT-clamp activity sensing + relay action on a bench "machine" | FUTURE (bench demo plan in 05) |
| PROFIenergy / Modbus / OPC UA links to real machines, MQTT to SCADA | FUTURE |
| Measured savings (M&V per ISO 50015 / IPMVP Option B) | FUTURE |
