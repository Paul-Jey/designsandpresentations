# 02 — AGENT BRIEF: Final Report + Final Deck (manufacturing pivot)

You are helping a 3-person EEE student team at SSN College of Engineering finish their final project report and final viva deck. Read `01_PROJECT_CONTEXT.md` first. Then follow this brief in order. Work in phases and **stop for the user's approval at each GATE**. Save every output as a file.

---

## PHASE 0 — Setup (no research yet)
1. Read: `01_PROJECT_CONTEXT.md`, the SSN guidelines PDF, the Review 3 deck PDF, the thesis template (.docx), and any existing simulation code.
2. Make a task list. Confirm which files are missing. Ask the user only for what blocks you.
3. **Confirm with the user:** cover page uses Annexure I-A ("PHASE I REPORT") or I-B ("A PROJECT REPORT")? Course is "Project Phase 1", so I-A is the likely choice. Do not guess silently.

---

## PHASE 1 — Research (target: 10–15 searches, cite everything)
Goal: build an evidence base for **Edge-AI idle-energy intelligence in manufacturing**. Use peer-reviewed papers, standards bodies, government data (BEE, CEA, IEA, US DOE), and real industry reports. Avoid blogs as primary evidence. Verify every number before use. Record each source with full citation in SSN format (Author (Year), 'Title', Journal, Vol, No, pp.).

### Research questions
1. **Size of the problem.** How much energy do machines use when idle or in standby vs processing? Look for: Gutowski et al. (2006, machine tool energy breakdown), Dahmus & Gutowski, Kara & Li, Zein/Herrmann (TU Braunschweig energy states), Mori et al. (2011, DMG Mori idle reduction), Fraunhofer studies, US DOE AMO data, IEA industry share. Want: % of machine-tool energy in non-productive states, typical idle power vs cutting power, real factory case results.
2. **Indian context.** Industry share of India's electricity (CEA General Review / IEA). BEE PAT scheme. MSME energy intensity (BEE SAMEEEKSHA / clusters). Tamil Nadu HT industrial tariff (TNERC current order) to replace the ₹8/kWh office assumption. CEA CO₂ EF v21 stays.
3. **Idle-load categories the camera can act on** (go beyond HVAC):
   - Machine tools / CNC / injection moulding left running with no operator and no part.
   - Conveyors running empty.
   - Compressed air (leaks, compressors running for idle lines) — DOE/Compressed Air Challenge data.
   - High-bay lighting in empty aisles/zones.
   - Exhaust / dust extraction / ventilation fans in empty zones.
   - Spot cooling / HVAC in shop floor.
4. **Standards and control paths for factories:** ISO 14955-1 (energy efficiency of machine tools), VDMA 34179 / energy states, PROFIenergy (PROFINET pause commands), OPC UA (umati), Modbus TCP, MQTT 5.0, ISO 50001 (EnMS), ISO 50006 (baselines/EnPIs), ISO 50015 / IPMVP (measurement and verification). Find what each does in one line.
5. **Vision-based machine state / operator presence literature:** camera detection of operator at workstation, machine activity recognition, fusion of vision with current sensing (NILM / CT clamps), edge AI on Jetson in factories. 4–6 papers.
6. **Safety and acceptance limits:** machines that must NOT be switched off automatically (thermal warm-up of CNC spindles, furnaces, process continuity). This drives the "recommend vs auto-act" design. Also privacy/worker-surveillance concerns.

### Output of Phase 1
`03_RESEARCH_FINDINGS.md` with: verified numbers table (value, unit, source, page), 15–25 references in SSN format, a short "what this means for our design" section.

**GATE 1 — show the user the findings summary (≤1 page) and wait.**

---

## PHASE 2 — Re-design the system for manufacturing (keep what is built)
Rule: **do not throw away the implemented pipeline.** Extend it. The person detector and filter still work; we add zones and machine context.

Proposed design to validate against research (adjust if evidence says otherwise):
- **Inputs per machine/zone:** (a) operator presence in a workstation ROI (existing ResNet10 detector + DeepStream `nvdsanalytics` ROI), (b) machine activity cue (motion in machine ROI, or CT-clamp current as a second sensor = sensor fusion), (c) optional part-present cue.
- **Machine state machine (replace the room state machine):**
  - PROCESSING — machine active (power P_proc)
  - IDLE-ATTENDED — machine not cutting, operator present (P_idle, no action)
  - IDLE-UNATTENDED — no activity, no operator for > T1 (e.g. 5 min) → action: recommend/auto standby (P_standby)
  - OFF / DEEP STANDBY — unattended > T2 (e.g. 30 min), only for machines marked safe to shut down (P_off)
  - Keep rise/fall hysteresis like the old 10 s / 30 s filter, but with factory-scale timers.
- **Multi-load actions** from the same occupancy map: zone lighting, conveyor stop when empty, compressor sequencing/valve isolation for idle line, extraction fans, spot cooling.
- **Two modes:** ADVISORY (dashboard alert to supervisor) and AUTO (via PROFIenergy / Modbus / relay) — only for whitelisted machines. This answers the safety question.
- Electrical KPIs: kWh, ₹, CO₂, load factor, idle-energy ratio (idle kWh / total kWh), and **maximum demand (kVA)** effect, since HT industrial bills charge demand.

Output: `04_SYSTEM_DESIGN.md` with block diagram description, state table (state, condition, power, action), and what is IMPLEMENTED / MODELLED / FUTURE.

**GATE 2 — confirm the design with the user.**

---

## PHASE 3 — Simulation model v2 (Python)
Build `sim_v2/` (reuse model v1 code if provided). Use only researched or clearly labelled assumed values.
1. **Reference factory:** small Indian MSME machining shop, e.g. 10 CNC machines + 1 conveyor line + compressor + high-bay lighting, 2 shifts (or 3), with breaks, shift change, material waits, tool changes, breakdowns. Power per state from research (cite).
2. **Simulations to produce (each one a figure + table):**
   - S1: one machine — activity and operator presence vs power over one shift (baseline vs controlled).
   - S2: whole shop cumulative energy, baseline vs controlled.
   - S3: energy breakdown by load type (machines, compressor, conveyor, lighting, ventilation) — stacked bar.
   - S4: load-duration curve + load factor + max demand.
   - S5: Monte-Carlo (≥1,000 shifts/days) with random idle events. Report mean, P5, P95.
   - S6: sensitivity tornado (idle fraction, idle power ratio, tariff, shifts/day, T1 timer).
   - S7: filter/timer study — false shutdown rate vs savings trade-off for different T1 values (this is a strong engineering result).
   - S8: payback per node (node cost vs machines covered per camera), net of node power.
   - S9 (keep): the original office/room case as a second application, shown briefly, to show generality.
3. Fixed seed, all assumptions in one `assumptions.yaml`, every chart labelled "MODELLED · model v2".
4. Check every number by running code. Never type numbers by hand into the report.

Output: figures (PNG, 300 dpi, white background, SSN style blue), `results_summary.md` with all key numbers.

**GATE 3 — show the results summary and 3–4 key charts.**

---

## PHASE 4 — Demo plan (viva needs a live demo)
Propose a cheap bench demo that fits the existing Jetson: e.g. a small motor/fan/drill as "machine", a CT clamp (SCT-013 + ADC or a smart plug with power reading) for activity, a workstation ROI for the operator. Demo flow: operator leaves → timer → IDLE-UNATTENDED → relay cuts the "machine" or dashboard alert → kWh and ₹ update live. List parts, cost in ₹, and what the team must code. Mark it clearly as optional if time is short.

Output: `05_DEMO_PLAN.md`.

---

## PHASE 5 — Report draft (.docx, follow SSN template exactly)
Formatting (from guidelines): A4; margins top 35, bottom 35, left 40, right 35 mm; Times New Roman 13 body, 1.5 spacing; abstract and bonafide in TNR 14 double spacing; chapter heading "CHAPTER n" centred 50 mm from top, title in caps 2 spaces below; numbering 2.3.4; figure captions below, centred, sentence case; table captions above, left; equations numbered (2.8) per chapter; page numbers top-right, roman for front matter; references alphabetical by first author, single spaced, SSN style. Month/year: NOVEMBER 2026.

Suggested chapter plan (~60 pages):
1. Introduction (6) — energy in Indian manufacturing, idle waste, objectives, scope, organisation.
2. Literature review & research gap (8) — vision occupancy, machine energy states, idle reduction studies, sensor fusion, standards; gap table.
3. System architecture (8) — edge node, pipeline, zones/ROIs, machine state machine, multi-load actions, advisory vs auto, privacy.
4. Implementation of the edge node (8) — Jetson, DeepStream, TensorRT, ResNet10, temporal filter, JSON, dashboard (photos, IMPLEMENTED).
5. Electrical energy modelling (8) — equations, state power table, tariff incl. demand charges, CO₂.
6. Simulation results & discussion (12) — S1–S9.
7. Economics, standards & deployment roadmap (5) — payback, ISO 50001/50006/IPMVP, PROFIenergy/OPC UA/MQTT/BACnet, M&V plan.
8. Conclusion & future work (3) — incl. SDG 7, 9, 12, 13 mapping.
References + Appendices (code listing excerpts, assumptions table, bill of materials).

### IMPORTANT — AI-detection limit is 10 %
The college runs Turnitin AI detection with a 10 % ceiling. Prose written by an AI will very likely fail it. So:
- Produce the report as a **technical draft**: full structure, all figures, tables, equations, numbers, references, and per-section **writing notes** (key points in bullet form plus a short sample paragraph).
- The team writes the final sentences in their own words. Do not try to disguise AI text; that is not the goal and it is risky.
- Mark each section with `[TEAM TO WRITE]` where prose is needed.

Output: `Final_Report_Draft.docx` + `report_outline.md`.

**GATE 4 — user reviews draft.**

---

## PHASE 6 — Final deck (max 15 slides, 10-minute talk)
Follow the Review 3 deck design exactly (SSN blue header style, status chips IMPLEMENTED / MODELLED / FUTURE, one takeaway box per slide). Cover all three phases. Suggested 15:
1 Title · 2 Problem (idle energy in manufacturing, Indian data) · 3 Objectives · 4 Literature & gap · 5 Journey across Phase 1–3 (timeline) · 6 System architecture · 7 Edge node implementation (photo) · 8 Machine state machine · 9 Energy model · 10 Shop-floor simulation (S2 + S3) · 11 Robustness (Monte-Carlo + timer trade-off) · 12 Economics & payback · 13 Standards & deployment roadmap · 14 Demo + results scorecard · 15 Conclusion & SDGs.
Output as .pptx (user's existing deck is a PowerPoint export).

---

## Working rules
- Cost control: use the cheaper model for drafting and code; use the strongest model only for design decisions and final QC.
- Never invent a citation or number. If not found, write `[NEEDS SOURCE]`.
- Keep the honesty labels. Do not claim measured savings.
- No em dashes in the report text.
- Last step of every phase: check numbers against code output and sources.
