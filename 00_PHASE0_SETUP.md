# 00 — PHASE 0 SETUP (status, task list, open questions)

Project: Edge-AI idle-energy intelligence (manufacturing pivot), SSN EEE, UEE2718, Batch B2.
Date of this note: 12 Oct 2026. Submission month on cover: NOVEMBER 2026.

---

## 1. Inputs received and read

| File | Status | Notes |
|---|---|---|
| `01_PROJECT_CONTEXT.md` | Read | Team, Review 3 state, expert pivot, dept rules |
| `02_AGENT_BRIEF.md` | Read | Phases 0 to 6 with gates |
| `Guidelines_UG_Project_Report.pdf` (13 pp) | Read | Formatting rules extracted below |
| `Review3_FIXED_1.pdf` (23 slides) | Read | Design language and v1 numbers extracted below |

## 2. Inputs MISSING

| Missing item | Needed for | Blocks? |
|---|---|---|
| SSN thesis template `.docx` (COE website / LMS) | Phase 5 report draft | Not now. I can build a `.docx` from the guidelines if it never arrives, but the official template is safer |
| Model v1 Python simulation code | Phase 3 (reuse logic, S9 office case) | Not now. I can rebuild v1 from the numbers on slides 9 to 17 if needed |
| Review 3 deck as `.pptx` (not PDF) | Phase 6 (copy master, chips, colours exactly) | Not now. PDF is enough to imitate; the `.pptx` gives an exact match |
| Jetson code (DeepStream config, PyDS probe, filter, dashboard) | Ch 4 + Appendix code listings | Not now (needed by Phase 5) |
| Original photos / screenshots (bench setup, live detection, dashboard) at full resolution | Ch 4 figures, deck slide 7 | Not now (needed by Phase 5) |
| HOD name and designation | Bonafide certificate | Not now (needed by Phase 5) |

## 3. Formatting rules extracted from the SSN guidelines

- A4. Margins: top 35 mm, bottom 35 mm, left 40 mm, right 35 mm.
- Body: Times New Roman 13, 1.5 spacing. Single spacing for long tables, long quotations, footnotes, multi-line captions, references.
- Bonafide and Abstract: TNR 14, double spacing. Abstract max 2 pages. Acknowledgement max 1 page, double spacing, student signatures bottom right.
- Order: Cover and Title page, Bonafide, Abstract, Acknowledgement, Table of Contents, List of Tables, List of Figures, List of Symbols/Abbreviations, Chapters, Appendices, References.
- Front-matter headings (items 2 to 10): CAPITALS, no punctuation, centred at top, text 2 spaces below.
- Chapter page: "CHAPTER n" centred 50 mm from top; title in CAPITALS 2 spaces below; text starts 4 spaces below title.
- Division headings left-justified, numbered 2.3.4; body below headings offset 20 mm (template convention).
- Page numbers: top right, 20 mm from top, no punctuation. Roman lower case for front matter (title page = i, not printed). Arabic from Chapter 1.
- Figures: numbered per chapter (3.4), caption BELOW, centred, sentence case. Tables: caption ABOVE, left aligned. Continued table: "Table 2.1 (continued)". Appendix figures: "Figure A 2.3".
- Equations numbered per chapter, (2.8), referred to as "Equation (2.8)".
- References: alphabetical by first author, single spaced, left justified, format
  `Author A.B. and Author C.D. (Year), 'Title', Journal, Vol. x, No. y, pp. a-b.`
  In-text: "(Tsychiya 1980)" or "Shin et al (1984)".
- Size: 60 pages ±10 % (54 to 66 pages) from Chapter 1 page 1 to last page of References.
- Sub-heading at page bottom needs at least 2 lines below it; no hyphenated last word on a page.
- Photographs in colour.

Cover page options:
- **Annexure I-A**: "PHASE I REPORT" under the title; bonafide Annexure II-A/II-B is labelled "for Phase I Report".
- **Annexure I-B**: "A PROJECT REPORT".

## 4. Review 3 deck: design language to reuse in Phase 6

- 4:3 slides. White body, SSN blue title text (approx #2F4F8F), slide number top right in blue.
- Footer: light blue + dark blue diagonal band with SSN logo bottom right.
- Status chip top left: IMPLEMENTED (green solid border), MODELLED (blue dashed), FUTURE (grey dashed), REFERENCE (grey).
- One takeaway box per slide: dashed blue border, pale blue fill, bold italic dark-blue sentence.
- Charts: white background, footnote line in small grey italics "MODELLED SIMULATION · model v1 · ...".
- Tables: dark-blue header row, alternating pale rows.

## 5. Model v1 number check (arithmetic only, from slides)

| Claim | Check | OK? |
|---|---|---|
| 17.0 kWh baseline | 1.70 kW × 10 h | Yes |
| 13.8 kWh controlled | 0.30×2 + 1.20×2 + 1.70×4 + 2.00×2 | Yes |
| 18.8 % saving | 3.2 / 17.0 | Yes |
| 1,168 kWh/yr | 3.2 × 365 | Yes |
| ₹9,344/yr | 1,168 × 8 | Yes |
| 0.83 t CO₂/yr | 1,168 × 0.710 = 829 kg | Yes |
| 90.6 % retained | (3.2 − 0.3) / 3.2 | Yes |
| 29.4 % Economy cut | (1.70 − 1.20) / 1.70 | Yes |
| Load factor 0.69 | 1.38 / 2.00 | Yes |
| 1.45 A empty, 9.7 A peak at 230 V | implies PF ≈ 0.9 (0.30 kW / (230 × 0.9)) | Yes, but PF 0.9 is not stated on the slide |
| Payback 22.5 months | 17,500 / 9,344 × 12 | Arithmetic yes, **but uses GROSS saving**. Net of node load: 2.9 × 365 × 8 = ₹8,468/yr → **24.8 months**. Fix in v2 (S8 is "net of node power"). |

## 6. Task list

### Phase 0 (this file)
- [x] Read context, brief, guidelines, Review 3 deck
- [x] List missing files
- [x] Extract formatting rules and deck design language
- [x] Re-check v1 numbers
- [ ] **User confirms cover page variant (I-A vs I-B)** ← GATE

### Phase 1 Research → `03_RESEARCH_FINDINGS.md` → GATE 1
- [ ] Q1 Size of idle problem (Gutowski 2006, Dahmus & Gutowski, Kara & Li, Herrmann/Zein, Mori 2011, Fraunhofer, DOE, IEA)
- [ ] Q2 Indian context (CEA General Review, IEA, BEE PAT, SAMEEEKSHA/MSME clusters, TNERC HT tariff incl. demand charge, CEA EF v21)
- [ ] Q3 Idle-load categories (CNC/injection moulding, conveyors, compressed air via DOE/CAC, high-bay lighting, extraction fans, spot cooling)
- [ ] Q4 Standards (ISO 14955-1, VDMA 34179, PROFIenergy, OPC UA/umati, Modbus TCP, MQTT 5.0, ISO 50001/50006/50015, IPMVP)
- [ ] Q5 Vision for operator presence / machine state, vision + CT/NILM fusion, Jetson in factories (4 to 6 papers)
- [ ] Q6 Safety limits (warm-up, furnaces, process continuity), worker-privacy concerns
- [ ] Numbers table with source and page; 15 to 25 references in SSN format

### Phase 2 Design → `04_SYSTEM_DESIGN.md` → GATE 2
### Phase 3 Simulation v2 → `sim_v2/`, figures S1 to S9, `results_summary.md` → GATE 3
### Phase 4 Demo plan → `05_DEMO_PLAN.md`
### Phase 5 Report draft → `Final_Report_Draft.docx`, `report_outline.md` → GATE 4
### Phase 6 Final deck (≤15 slides) → `.pptx`

## 7. Notes and risks

- AI-detection ceiling 10 %: report will be a technical draft with `[TEAM TO WRITE]` markers and sample paragraphs, as the brief says. Prose must be rewritten by the team.
- "Phase I REPORT" vs "final thesis": the context calls it a final thesis, but the course code is Project Phase 1 and both bonafide specimens say "for Phase I Report". I-A looks right; needs your confirmation.
- No em dashes in report text (will enforce in Phase 5).
