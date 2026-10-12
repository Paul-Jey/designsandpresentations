# 03 — RESEARCH FINDINGS (Phase 1)

Topic: Edge-AI idle-energy intelligence for manufacturing (Indian MSME machining shop).
Searches run: 26 (web search). Date: 12 Oct 2026.

**Verification note.** Direct page fetching is blocked in this environment, so full texts could not be opened.
Every number below was checked against search-result text. The `Level` column says how strong that check is:
- **P** = text seen from the primary source itself (publisher, standards body, government page, or the source's own abstract).
- **S** = number seen only in a secondary source that cites the primary. Team must check the primary before final submission.
- Page numbers: where the exact page could not be seen, it is marked `p. [CHECK]`. The team must fill these from the PDF (library access).

---

## 1. Summary (one page, for Gate 1)

1. **The problem is real and large.** In a studied automotive machining line only **14.8 %** of input energy went to actual cutting; **85.2 %** went to auxiliary and constant loads that run whether or not a part is being cut (Gutowski et al., S). Reviews report non-cutting states can take up to **80 %** of machine-tool energy (S). The "fixed" readiness load is recognised in CIRP literature as a distinct, under-studied energy block (Li, Zein, Kara and Herrmann 2011, P).
2. **Switching idle machines off works, but only for long enough idle periods.** Mouzon et al. (2007, P) showed large savings by turning off under-used (non-bottleneck) machines when the idle period exceeds a break-even time. Squeo et al. (2019, P) extended this to several sleep states per component on a 5-axis machining centre. This is exactly the timer logic (T1, T2) of our design.
3. **What the camera adds.** Existing policies decide on *time since last part*. Our node adds *is anyone at the machine / in the zone*. No paper found combines camera operator presence with machine standby control. Closest are vision occupancy for buildings (Tien et al. 2021, P) and current-based machine state recognition (NILM, Gebbe et al. 2019, Suzuki et al. 2017, P). **This is our research gap.**
4. **Beyond machines.** Compressed air is about **10 %** of a typical plant's electricity, 30 % or more in some (US DOE sourcebook, P); poorly maintained plants leak **20 to 30 %** of compressor output (DOE, S). Occupancy-based lighting control averages about **24 %** savings (LBNL meta-analysis, S). Same camera, more loads.
5. **Indian context.** Industry used about **42 %** of India's electricity in FY 2023-24 (CEA data, S). About 200 energy-intensive MSME clusters use roughly 25 % of national energy with about 15 % savings potential (TERI, S). Tamil Nadu HT-I industrial tariff from 1 Jul 2025: **₹7.50/kWh + ₹608/kVA/month** demand charge, billed on max(recorded kVA, 90 % of contract) (TNERC T.O. No. 6 of 2025, S). Grid EF **0.710 t CO₂/MWh** for FY 2024-25 (CEA v21.0, P).
6. **Safety drives "advise vs act".** Thermal effects cause up to **75 %** of geometric errors in machine tools (Fraunhofer IPK, S); switching spindles/coolers off forces energy-hungry warm-ups. So precision machines must default to ADVISORY mode, and only whitelisted loads (lights, fans, conveyors, idle compressors, non-precision machines) may be AUTO-switched.
7. **Control paths exist.** PROFIenergy (PROFINET) has standard pause/standby commands for planned and unplanned breaks (PI, P). ISO 14955-1:2017 is the machine-tool energy-efficiency design standard (ISO, P). ISO 50001/50006/50015 and IPMVP give the M&V frame.
8. **Privacy.** India's DPDP Act 2023 allows some employment-purpose processing but demands purpose limitation and minimisation; core provisions are due in force by 13 May 2027 (S). Our "only metadata leaves the device" design fits.

**What changes in the design:** machine state machine with factory timers (T1 standby, T2 off), operator-presence as a veto on shutdown, ADVISORY default with AUTO only on a whitelist, demand (kVA) as a KPI because HT bills charge it, and tariff ₹7.50/kWh instead of ₹8.

---

## 2. Verified numbers table

| # | Quantity | Value | Unit | Source | Page | Level |
|---|---|---|---|---|---|---|
| N1 | Share of input energy used for actual machining, automotive production line (Toyota survey) | 14.8 | % | Gutowski et al. (2005/2006), cited in secondary reviews | p. [CHECK] | S |
| N2 | Share to auxiliary / constant loads in same line | 85.2 | % | as N1 | p. [CHECK] | S |
| N3 | Non-cutting (idle, standby, auxiliary) share of machine-tool energy, upper value reported | up to 80 | % | Review on CNC standby/auxiliary power model (ResearchGate 2022) | p. [CHECK] | S |
| N4 | Idle power modelling assumption | 25 % of spindle (largest component) power | — | Procedia CIRP Vol. 69 (2018) | p. 259ff | P (assumption in paper) |
| N5 | Spindle share of energy during cutting | 40 to 60 | % | Bull. Pol. Acad. Sci. (spindle inherent energy paper) | p. [CHECK] | P (abstract) |
| N6 | Mean total power, roughing, example machining centre | 13 | kW | Heidenhain (2011), Aspects of Energy Efficiency in Machine Tools | p. [CHECK] | P |
| N7 | Coolant temperature control + pumping in same example | 5.1 | kW | as N6 | p. [CHECK] | P |
| N8 | Compressed air share of plant electricity, typical | ≈10 (≥30 at some sites) | % | US DOE (2003) Improving Compressed Air System Performance sourcebook | p. [CHECK] | P |
| N9 | Leak loss, poorly maintained plant | 20 to 30 | % of compressor output | DOE Compressed Air fact sheet #7 (via secondary) | — | S |
| N10 | Leak loss, well maintained | < 10 | % | as N9 | — | S |
| N11 | Savings from compressed-air system improvements | 20 to 50 | % | DOE sourcebook | p. [CHECK] | P |
| N12 | Average savings from occupancy sensors (lighting) | 24 | % | Williams et al. (2012) LBNL meta-analysis (240 estimates, 88 studies) | p. [CHECK] | S |
| N13 | Industry share of India's electricity consumption, FY 2023-24 | ≈42 | % | CEA General Review 2025, via ORF Energy News Monitor | Table 1.4 [CHECK] | S |
| N14 | MSME clusters' share of India's energy use | ≈25 | % | TERI National Summit on MSME (press release) | — | S |
| N15 | MSME energy-saving potential | ≈15 | % | as N14 | — | S |
| N16 | TN HT-I energy charge (from 1 Jul 2025) | 7.50 | ₹/kWh | TNERC Tariff Order No. 6 of 2025 (30 Jun 2025) | Tariff schedule [CHECK] | S |
| N17 | TN HT-I demand charge (from 1 Jul 2025) | 608 | ₹/kVA/month | as N16 | [CHECK] | S |
| N18 | Billing demand rule | max(recorded kVA, 90 % of contracted) | — | as N16 | [CHECK] | S |
| N19 | ToD: peak-hour surcharge / night rebate (HT industrial) | +25 / −5 | % of energy charge | as N16 (secondary summary) | [CHECK] | S |
| N20 | All-India weighted avg grid EF, FY 2024-25 | 0.710 | t CO₂/MWh | CEA CO₂ Baseline Database v21.0 User Guide | Table S [CHECK] | P |
| N21 | Same, FY 2023-24 (for context) | 0.727 | t CO₂/MWh | as N20 | — | P |
| N22 | Thermally induced share of geometric errors in machine tools | up to 75 | % | Fraunhofer IPK, Futur 2023-1 | — | S |
| N23 | BEE PAT Cycle I verified savings | 8.67 Mtoe (target 6.686), ≈31 Mt CO₂ | — | BEE PAT page | — | P |
| N24 | Vision occupancy + equipment detection accuracy (office) | 97.32 / 80.80 | % | Tien et al. (2021) Energies 14(1):156 | abstract | P |
| N25 | NILM for manufacturing loads, disaggregation accuracy | ≥ 85 for most loads | % | Gebbe et al. (2019) arXiv:1912.01500 | abstract | P |
| N26 | Cutting machine tools' share of world electricity | 1 to 3 (200 to 700 TWh) | % | MM Science Journal (Nov 2021) ML-based identification of EE measures for machine tools | p. [CHECK] | P |

**Numbers NOT found (do not use without a source):**
- Measured idle-to-cutting power ratio for a specific Indian CNC shop: `[NEEDS SOURCE]` → model v2 will use an **assumed** ratio, labelled, and swept in sensitivity (S6).
- Share of time a typical MSME CNC machine sits idle: `[NEEDS SOURCE]` → assumed, swept in S6.
- VDMA 34179 content (not surfaced by search): `[NEEDS SOURCE]`; cite only by title if at all.
- Exact page numbers for most journal items: `p. [CHECK]`.

---

## 3. Findings by research question

### Q1. Size of the problem
- Material removal is a small part of machine-tool energy. Gutowski, Dahmus and Thiriez (2006) showed that specific energy is not constant and that process rate is the main driver; constant "readiness" loads dominate at low rates. The automotive-line figure of 14.8 % (cutting) vs 85.2 % (auxiliary) is widely cited (N1, N2).
- Kara and Li (2011) model specific energy as SEC = C0 + C1/MRR: the C1/MRR term is the fixed load spread over output. When the machine is not producing, all of C1 is waste.
- Li, Zein, Kara and Herrmann (2011) name the stand-by / fixed energy as under-studied and assess it on six machine tools.
- Denkena et al. (2020, CIRP Annals keynote) review machine and process measures, including standby and switch-off strategies, and list retrofitting as an open question. Our node is a retrofit.
- Mori et al. (2011) (DMG Mori) cut machining-centre energy by changing cutting conditions and synchronising spindle and feed acceleration; this is a machine-side measure, complementary to ours.

### Q2. Indian context
- Industry ≈ 42 % of electricity (N13). PAT has delivered large verified savings in large designated consumers (N23), but MSMEs are mostly outside PAT; BEE's SME programme and SAMEEEKSHA platform target them (N14, N15).
- **Tariff for the model:** ₹7.50/kWh energy, ₹608/kVA/month demand (N16 to N18). Replace the old ₹8/kWh assumption. Demand charge means **peak kVA reduction has real money value** in a factory, unlike the office case.
- **EF:** keep 0.710 t/MWh (N20). Note v22.0 user guide (Aug 2026) exists; check if FY 2024-25 value was revised.

### Q3. Idle-load categories the camera can act on
| Load | Idle waste mechanism | Camera cue | Evidence |
|---|---|---|---|
| CNC / machining centre | Spindle cooling, coolant pumps, hydraulics, chip conveyor, drives run when no part / no operator | No operator in machine ROI + no motion in work area for > T1 | N1 to N7, Mouzon 2007, Squeo 2019 |
| Injection moulding | Barrel heaters and hydraulics stay hot during waits | Same, but **advisory only** (thermal process) | Thermal constraint (Q6) |
| Conveyors | Run empty between batches | No parts / no people along conveyor ROI | `[NEEDS SOURCE]` for % (model assumption) |
| Compressed air | Compressor serves idle line; leaks continue when line idle | Whole line zone empty → isolate line valve / step down compressor | N8 to N11 |
| High-bay lighting | Lit aisles with no one present | Zone occupancy (already implemented logic) | N12 |
| Extraction / ventilation fans | Run when no welding/grinding activity | Zone empty + machine idle | `[NEEDS SOURCE]` (model assumption) |
| Spot cooling / shop HVAC | Cools empty bays | Zone occupancy (v1 logic) | v1 model, Kong 2022, Lin 2023 |

### Q4. Standards and control paths (one line each)
| Standard | What it does | Our use |
|---|---|---|
| ISO 14955-1:2017 | Design method for energy-efficient machine tools (use stage); not for comparing machines | Reference for machine energy states |
| ISO 14955-2 | Practical methods to measure energy supplied to machine tools and components | M&V of machine kW in future work |
| VDMA 34179 | Measurement instruction for machine-tool energy (title level only) `[NEEDS SOURCE]` | Mention only |
| PROFIenergy (PI) | PROFINET profile: controller sends Start/End Pause; devices enter predefined low-power modes during planned/unplanned breaks | AUTO path for PROFINET machines |
| OPC UA (IEC 62541) / umati | Vendor-neutral machine data model | Read machine state as a 2nd sensor; future |
| Modbus TCP | Simple register read/write; most energy meters and VFDs speak it | Read CT meter, command relays/VFDs |
| MQTT 5.0 (OASIS 2019) | Lightweight publish/subscribe telemetry | Node → dashboard / SCADA |
| ISO 50001:2018 | Energy management system (Plan-Do-Check-Act) | Where the node sits in a plant EnMS |
| ISO 50006 | Energy baselines and EnPIs | Define idle-energy ratio as an EnPI |
| ISO 50015 / IPMVP | Measurement and verification of energy savings | M&V plan (Option B, retrofit isolation) |

### Q5. Vision for operator presence / machine state, fusion with current sensing
- Tien et al. (2021): Faster R-CNN on a camera detects occupancy (97.3 %) and equipment use (80.8 %) to cut building energy. Shows camera can tell *people* and *equipment use*.
- Hu et al. (2023), Choi et al. (2022): vision occupancy counting (from Review 3).
- Operating-state recognition of machine tools from power data with deep learning (Sensors 2022, PMC9460611): states = cutting, starting, standby. Gives our machine-activity cue from a CT clamp.
- Gebbe et al. (2019) NILM for manufacturing: ≥85 % accuracy on most loads from aggregate V and I.
- Suzuki, Kohmoto and Ogatsu (2017, EUSIPCO, NEC): one current sensor, several machines, factorial HMM.
- Industrial worker localisation by deep learning (Springer 2025 chapter): detects walking operators in about two-thirds of frames, showing occlusion is a real limit → justifies temporal filter + current fusion.
- **Gap:** no work fuses *camera operator presence* + *current-based machine state* to drive *standby decisions* on an edge node.

### Q6. Safety and acceptance limits
- Thermal stability: precision machines need warm-up after cold start; thermal effects dominate geometric error (N22). Standby of coolers changes spindle displacement (euspen 2026, KIMM). → precision machines: **ADVISORY** only, or a light "standby" that keeps thermal control on.
- Switching off only pays when idle time > break-even (Mouzon 2007). → T1/T2 timers, plus a minimum-off time.
- Process continuity: furnaces, moulding barrels, heat treatment, curing: never auto-off. → whitelist.
- Safety: no auto-start of machines from the node. Node may only request pause/standby; restart is by operator (machinery safety principle; cite IS/ISO 12100 as general reference `[CHECK]`).
- Privacy: DPDP Act 2023 legitimate use for employment purposes exists but purpose limitation applies; core provisions in force by 13 May 2027 (S). → process on device, store counts not images, no face recognition, signage, works-committee consent.

---

## 4. What this means for our design
1. Keep the implemented pipeline. Add ROIs per machine and per zone (DeepStream `nvdsanalytics`).
2. Machine state machine: PROCESSING, IDLE-ATTENDED, IDLE-UNATTENDED (after T1), DEEP STANDBY/OFF (after T2, whitelist only). Operator present = veto on shutdown.
3. Second sensor (CT clamp current) to confirm "machine active", because the camera alone cannot see cutting inside an enclosure.
4. Default ADVISORY. AUTO only for lights, fans, conveyors, compressor line valves, non-precision machines.
5. KPIs: kWh, ₹ (energy + demand), kVA max demand, load factor, idle-energy ratio (EnPI per ISO 50006), CO₂.
6. Tariff ₹7.50/kWh and ₹608/kVA/month (TN HT-I). EF 0.710.
7. Idle power ratio and idle fraction are **assumed** (no Indian measured source) and must be swept in sensitivity.

---

## 5. References (SSN format, alphabetical; to be checked against PDFs)

1. Central Electricity Authority (2025), 'CO₂ Baseline Database for the Indian Power Sector, User Guide Version 21.0', Ministry of Power, Government of India, New Delhi.
2. Central Electricity Authority (2025), 'All India Electricity Statistics, General Review 2025', Ministry of Power, Government of India, New Delhi.
3. Choi H. et al. (2022), Building and Environment, Vol. 223, 109496. `[CHECK full author list and title from Review 3 source]`
4. Denkena B., Abele E., Brecher C., Dittrich M.-A., Kara S. and Mori M. (2020), 'Energy efficient machine tools', CIRP Annals - Manufacturing Technology, Vol. 69, No. 2, pp. [CHECK].
5. Gebbe C. et al. (2019), 'Nonintrusive load monitoring for machines used in manufacturing', arXiv:1912.01500. `[CHECK full author list]`
6. Gutowski T., Dahmus J. and Thiriez A. (2006), 'Electrical energy requirements for manufacturing processes', Proc. 13th CIRP Int. Conf. on Life Cycle Engineering, Leuven, pp. 623-628.
7. Gutowski T., Murphy C., Allen D., Bauer D., Bras B., Piwonka T., Sheng P., Sutherland J., Thurston D. and Wolff E. (2005), 'Environmentally benign manufacturing: observations from Japan, Europe and the United States', Journal of Cleaner Production, Vol. 13, No. 1, pp. 1-17.
8. HEIDENHAIN (2011), 'Aspects of energy efficiency in machine tools', Technical Information, Dr. Johannes Heidenhain GmbH, Traunreut.
9. ISO (2017), 'ISO 14955-1:2017 Machine tools - Environmental evaluation of machine tools - Part 1: Design methodology for energy-efficient machine tools', International Organization for Standardization, Geneva.
10. ISO (2018), 'ISO 50001:2018 Energy management systems - Requirements with guidance for use', ISO, Geneva.
11. ISO (2014), 'ISO 50006:2014 Energy management systems - Measuring energy performance using energy baselines and energy performance indicators', ISO, Geneva.
12. ISO (2014), 'ISO 50015:2014 Energy management systems - Measurement and verification of energy performance of organizations', ISO, Geneva.
13. Kara S. and Li W. (2011), 'Unit process energy consumption models for material removal processes', CIRP Annals - Manufacturing Technology, Vol. 60, No. 1, pp. 37-40.
14. Kong M., Dong B., Zhang R. and O'Neill Z. (2022), 'HVAC energy savings, thermal comfort and air quality for occupant-centric control through a side-by-side experimental study', Applied Energy, Vol. 306, 117987.
15. Li W., Zein A., Kara S. and Herrmann C. (2011), 'An investigation into fixed energy consumption of machine tools', Proc. 18th CIRP Int. Conf. on Life Cycle Engineering, Braunschweig, pp. 268-273.
16. Lin G., Casillas A., Sheng M. and Granderson J. (2023), 'Performance evaluation of an occupancy-based HVAC control system in an office building', Energies, Vol. 16, No. 20, 7088.
17. Mori M., Fujishima M., Inamasu Y. and Oda Y. (2011), 'A study on energy efficiency improvement for machine tools', CIRP Annals - Manufacturing Technology, Vol. 60, No. 1, pp. 145-148.
18. Mouzon G., Yildirim M.B. and Twomey J. (2007), 'Operational methods for minimization of energy consumption of manufacturing equipment', International Journal of Production Research, Vol. 45, No. 18-19, pp. 4247-4271.
19. OASIS (2019), 'MQTT Version 5.0', OASIS Standard, 7 March 2019.
20. PROFIBUS & PROFINET International (2010), 'PROFIenergy - Technical specification for PROFINET', PI, Karlsruhe. `[CHECK version/year]`
21. Squeo M., Frigerio N. and Matta A. (2019), 'Multiple sleeping states for energy saving in CNC machining centers', Procedia CIRP, Vol. 80, pp. 144-149.
22. Suzuki R., Kohmoto S. and Ogatsu T. (2017), 'Non-intrusive condition monitoring for manufacturing systems', Proc. 25th European Signal Processing Conf. (EUSIPCO), Kos, pp. [CHECK].
23. Tamil Nadu Electricity Regulatory Commission (2025), 'Tariff Order No. 6 of 2025', TNERC, Chennai, 30 June 2025.
24. Tien P.W., Wei S., Calautit J.K., Darkwa J. and Wood C. (2021), 'A computer vision-based occupancy and equipment usage detection approach for reducing building energy demand', Energies, Vol. 14, No. 1, 156.
25. U.S. Department of Energy (2003), 'Improving compressed air system performance: a sourcebook for industry', DOE Industrial Technologies Program and Compressed Air Challenge, Washington DC.
26. Williams A., Atkinson B., Garbesi K., Page E. and Rubinstein F. (2012), 'Lighting controls in commercial buildings', LEUKOS, Vol. 8, No. 3, pp. 161-180. `[CHECK]`

Also usable (from Review 3): Hu et al. (2023) IEEE IoT J. 10(1):597-608; Calautit et al. (2024) J. Building Engineering; NVIDIA DeepStream SDK 6.0.1 documentation; ANSI/ASHRAE 135 (BACnet); Government of India (2023) Digital Personal Data Protection Act, No. 22 of 2023.

## 6. Sources consulted (links)
- Gutowski CIRP 2006 PDF: https://web.mit.edu/2.813/www/readings/Gutowski-CIRP.pdf
- Secondary for 14.8 %: https://www.researchgate.net/publication/293824067_ENERGY_CONSIDERATION_IN_METAL_MACHINING , https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8464692/
- Kara and Li 2011: https://findanexpert.unimelb.edu.au/scholarlywork/1390681-unit-process-energy-consumption-models-for-material-removal-processes
- Li, Zein, Kara, Herrmann 2011: https://findanexpert.unimelb.edu.au/scholarlywork/1390683-an-investigation-into-fixed-energy-consumption-of-machine-tools
- Mori et al. 2011: https://www.dmgmori.co.jp/en/trend/detail/id=1848
- Mouzon et al. 2007: https://soar.wichita.edu/items/d5a14914-38e7-4120-9fc1-43ccc83305fc
- Squeo et al. 2019: https://www.sciencedirect.com/science/article/pii/S221282711831299X
- Denkena et al. 2020: https://tubiblio.ulb.tu-darmstadt.de/122333/
- Non-cutting up to 80 %: https://www.researchgate.net/publication/359157887_A_new_empirical_standby_power_and_auxiliary_power_model_of_CNC_machine_tools
- Procedia CIRP 69 (2018) idle 25 %: https://www.sciencedirect.com/science/article/pii/S2212827117308107
- Heidenhain: https://www.heidenhain.us/wp-content/uploads/25-AspectsofEnergyEfficiencyinMT.pdf
- DOE compressed air sourcebook: https://www.energy.gov/sites/default/files/2014/05/f16/compressed_air_sourcebook.pdf ; leaks: https://reliamag.com/guides/compressed-air-leak-statistics/
- LBNL lighting meta-analysis: https://eta-publications.lbl.gov/bibcite/reference/23140
- CEA General Review 2024: https://cea.nic.in/wp-content/uploads/general/2024/General_Review_2024_2.pdf ; FY24 share via ORF: https://orfonline.org/research/energy-news-monitor-volume-xxii-issue-3
- CEA v21 EF: https://cea.nic.in/wp-content/uploads/baseline/2025/12/User_Guide_V_21.0.pdf
- TNERC 2025 tariff (secondary): https://pwrnxt.in/blog/tamil-nadu-ci-tariff-decoded , https://www.tristarenergy.in/blog/tangedco-electricity-tariff-rates-2026 ; FY24-25: https://tecaonline.in/pdfupload/Files/Cir%20No.17%20The%20Highlights%20of%20TNERC%20Tariff%20Revision%20Order%20for%20FY%202024-25.pdf
- BEE PAT: https://beeindia.gov.in/en/node/39347
- TERI MSME: https://www.teriin.org/sites/default/files/pressrelease/national-summit-on-MSME.pdf
- PROFIenergy: https://www.profibus.com/technology/profienergy/ , https://profinetuniversity.com/application-profiles/profienergy-profile/
- ISO 14955-1: https://www.iso.org/news/ref2262.html
- Tien et al. 2021: https://doi.org/10.3390/en14010156
- Machine-tool state recognition (Sensors 2022): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9460611/
- NILM manufacturing: https://ar5iv.arxiv.org/html/1912.01500 ; EUSIPCO 2017: https://new.eurasip.org/Proceedings/Eusipco/Eusipco2017/papers/1570347798.pdf
- Thermal warm-up: https://www.euspen.eu/knowledge-base/ICE26241.pdf , https://www.ipk.fraunhofer.de/en/media/futur/futur-2023-1/heat-pump-for-machines.html
- DPDP and workplace monitoring: https://ksandk.com/data-protection-and-data-privacy/can-employers-monitor-employees-dpdp-act/ , https://www.khuranaandkhurana.com/workplace-surveillance-productivity-software-and-employee-privacy
- MM Science 2021 (1 to 3 % world electricity): https://mmscience.eu/journal/issues/november-2021/articles/machine-learning-based-identification-of-energy-efficiency-measures-for-machine-tools-using-load-profiles-and-machine-specific-meta-data/download
