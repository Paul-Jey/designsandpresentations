# Final report and viva deck: Edge-AI idle-energy intelligence (SSN EEE, Batch B2)

| File / folder | What it is | Phase |
|---|---|---|
| `inputs/` | Brief, project context, SSN guidelines, Review 3 deck | 0 |
| `00_PHASE0_SETUP.md` | Task list, missing files, extracted SSN formatting rules, v1 number check | 0 |
| `03_RESEARCH_FINDINGS.md` | Verified numbers table, 26 references (SSN style), design implications | 1 |
| `04_SYSTEM_DESIGN.md` | Machine state machine, multi-load rules, ADVISORY/AUTO, KPIs, status labels | 2 |
| `sim_v2/` | Model v2: `assumptions.yaml`, `model.py`, `run_all.py` (S1–S9), `make_summary.py`, `figures/`, `results.json`, `results_summary.md` | 3 |
| `05_DEMO_PLAN.md` | Bench demo: parts, cost, code to write, 90 s script | 4 |
| `Final_Report_Draft.docx` | SSN-format technical draft (Annexure I-A cover), built by `report/build_report.py` | 5 |
| `report_outline.md` | Page budget and what the team still writes | 5 |
| `deck_source/` | Source of the 15-slide viva deck (Claude Slides artifact) | 6 |

## Rebuild everything
```bash
pip install numpy matplotlib pyyaml python-docx
cd sim_v2 && python3 run_all.py && python3 make_summary.py      # about 5 min
cd ../report && python3 make_diagrams.py && python3 build_report.py
```
No number in the report is typed by hand. All of them come from `sim_v2/results.json`.

## Honesty labels
IMPLEMENTED: the Jetson edge node (live). MODELLED: everything in `sim_v2`. FUTURE: integration and metered M&V.
