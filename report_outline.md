# report_outline.md — Final_Report_Draft.docx

Built by `report/build_report.py`. Numbers are pulled from `sim_v2/results.json`, so rebuild the draft after any re-simulation.
Cover: **Annexure I-A ("PHASE I REPORT")**, NOVEMBER 2026. Bonafide: Annexure II-B layout.

## Page budget (Chapter 1 page 1 → last page of References must be 54 to 66 pages)

| Part | Draft now (pages) | Team prose to add (words) | Target final (pages) |
|---|---|---|---|
| Ch 1 Introduction | 3 | ~1,000 | 6 |
| Ch 2 Literature review and gap | 3 | ~2,100 | 8 |
| Ch 3 System architecture | 4 | ~1,500 | 8 |
| Ch 4 Edge node implementation | 3 | ~1,200 + code + measured values | 7 |
| Ch 5 Electrical energy modelling | 3 | ~400 | 6 |
| Ch 6 Simulation results and discussion | 9 | ~2,500 | 13 |
| Ch 7 Economics, standards, roadmap | 2 | ~700 | 5 |
| Ch 8 Conclusion and future work | 1 | ~700 | 3 |
| Appendices 1 to 4 | 8 | Appendix 3 code (~2 pp) | 8 |
| References | 3 | — | 3 |
| **Total** | **39** | **~10,000** | **≈ 60–66** |

At 1.5 spacing in TNR 13 a page holds about 330 words. When you replace the blue writing notes with your own prose, the draft should grow to about 60 pages. If it goes over 66 pages, shorten Appendix 1 (the full YAML) first.

## What is done vs what the team writes

| Item | Status |
|---|---|
| Cover, bonafide, front-matter structure, page numbering (roman → arabic) | Done. HOD name still to fill |
| TOC, list of tables, list of figures | Word fields: right-click → Update Field after the final edit; then reformat to the Annexure III table |
| 15 figures (9 simulation, 3 diagrams, 3 photos) with captions | Done |
| 17 tables with captions | Done |
| Equations (3.1–3.2, 5.1–5.10) numbered per chapter | Done |
| References (30, alphabetical, SSN style) | Done. Items marked [CHECK] need the page or author detail filled from the PDFs |
| Abstract, acknowledgement, all body prose | **[TEAM TO WRITE]**, guided by the writing notes and sample paragraphs. Delete the blue notes when you are done |
| Ch 4.5 measured FPS, latency, power, precision/recall | **[TEAM TO MEASURE]** |
| Appendix 3 Jetson code excerpts | **[TEAM TO INSERT]** |

## Rules to keep while writing
- No em dashes. The build script checks for them; keep it that way when you edit by hand.
- Keep the IMPLEMENTED / MODELLED / FUTURE labels. Never say "measured savings".
- Quote the Monte-Carlo mean as the headline figure. The reference day is only one sample.
- Write in your own words. The sample paragraphs show tone and content only (AI-detection limit is 10 %).
- Title: the cover keeps the registered title. If the guide approves a manufacturing title (e.g. "Edge-AI idle-energy intelligence for manufacturing using surveillance cameras"), change `TITLE` in `build_report.py` and rebuild.

## Formatting checks before printing
- Abstract and bonafide text: TNR 14, double spacing (set this after the team's text is in).
- Every chapter starts on a new page with "CHAPTER n" centred, title in capitals below it.
- Figure captions go below the figure and are centred; table captions go above the table and are left-aligned.
- Page numbers sit top right, with nothing printed on the title page.
