"""Build Final_Report_Draft.docx in SSN format (Annexure I-A cover).

Technical draft: structure, figures, tables, equations, numbers and references are filled in.
Prose is marked [TEAM TO WRITE] with writing notes and a short sample paragraph that the team
must rewrite in their own words (Turnitin AI-detection limit 10 %).
All numbers come from sim_v2/results.json and sim_v2/assumptions.yaml.
"""
import json
from pathlib import Path

import yaml
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

HERE = Path(__file__).parent
ROOT = HERE.parent
SIM = ROOT / "sim_v2"
FIG = SIM / "figures"
AS = HERE / "assets"
R = json.load(open(SIM / "results.json"))
C = yaml.safe_load(open(SIM / "assumptions.yaml"))
s5, a5, s8, s9, rd = R["S5"], R["S5"]["annual"], R["S8"], R["S9"], R["reference_day"]
f0 = lambda x: f"{x:,.0f}"
f1 = lambda x: f"{x:,.1f}"
f2 = lambda x: f"{x:,.2f}"

TITLE = "AI DATA ANALYTICS LAYER FOR SURVEILLANCE SYSTEMS USING EDGE AI FOR ENERGY MANAGEMENT SYSTEMS"
TEAM = [("PAUL JEY SANJITH J", "3122233001069"), ("OVIYAN P S", "3122233001067"), ("THIRSNA S", "3122233001309")]
DEPT = "Department of Electrical and Electronics Engineering"
NOTE_BLUE = RGBColor(0x1F, 0x3A, 0x68)
RED = RGBColor(0xB0, 0x00, 0x20)

doc = Document()

# ------------------------------------------------------------------ styles
st = doc.styles
normal = st["Normal"]
normal.font.name = "Times New Roman"
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.font.size = Pt(13)
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

for name, size, align in [("Heading 1", 14, WD_ALIGN_PARAGRAPH.CENTER), ("Heading 2", 13, WD_ALIGN_PARAGRAPH.LEFT),
                          ("Heading 3", 13, WD_ALIGN_PARAGRAPH.LEFT)]:
    h = st[name]
    h.font.name = "Times New Roman"
    h.element.rPr.rFonts.set(qn("w:asciiTheme"), "") if False else None
    rpr = h.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(k), "Times New Roman")
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(k)) is not None:
            del rf.attrib[qn(k)]
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.italic = False
    h.font.color.rgb = RGBColor(0, 0, 0)
    h.paragraph_format.alignment = align
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(12)
    h.paragraph_format.line_spacing = 1.5
    h.paragraph_format.keep_with_next = True


def add_style(name, size=13, bold=False, italic=False, align=None, color=None, spacing=1.5, base="Normal"):
    s = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = st[base]
    s.font.name = "Times New Roman"
    s.font.size = Pt(size)
    s.font.bold = bold
    s.font.italic = italic
    if color:
        s.font.color.rgb = color
    if align is not None:
        s.paragraph_format.alignment = align
    s.paragraph_format.line_spacing = spacing
    return s


add_style("Chapter Label", 14, True, align=WD_ALIGN_PARAGRAPH.CENTER).paragraph_format.space_before = Mm(15)
add_style("Figure Caption", 12, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0).paragraph_format.space_after = Pt(14)
fc = add_style("Table Caption", 12, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0)
fc.paragraph_format.space_before = Pt(10)
fc.paragraph_format.keep_with_next = True
add_style("Writing Note", 11, italic=True, color=NOTE_BLUE, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.15)
add_style("Sample Para", 12, color=RGBColor(0x44, 0x44, 0x44), spacing=1.5)
add_style("Ref", 12, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0).paragraph_format.space_after = Pt(6)
add_style("Equation", 13, align=WD_ALIGN_PARAGRAPH.CENTER)
add_style("Front Heading", 14, True, align=WD_ALIGN_PARAGRAPH.CENTER)
add_style("Table Text", 11, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0).paragraph_format.space_after = Pt(0)


# ------------------------------------------------------------------ low-level helpers
def field(par, instr):
    r = par.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    i = OxmlElement("w:instrText"); i.set(qn("xml:space"), "preserve"); i.text = instr
    s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t"); t.text = "Right-click and choose Update Field"
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    r._r.append(b); r._r.append(i); r._r.append(s); r._r.append(t); r._r.append(e)


def set_margins(sec):
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin, sec.bottom_margin = Mm(35), Mm(35)
    sec.left_margin, sec.right_margin = Mm(40), Mm(35)
    sec.header_distance = Mm(20)


def page_numbering(sec, fmt, start=None, show=True):
    sectPr = sec._sectPr
    pg = sectPr.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType"); sectPr.append(pg)
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    sec.header.is_linked_to_previous = False
    hp = sec.header.paragraphs[0]
    for r in list(hp.runs):
        r._r.getparent().remove(r._r)
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if show:
        field(hp, "PAGE")
        for r in hp.runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(12)


def para(text="", style="Normal", bold=False, italic=False, size=None, align=None, space_after=None):
    p = _apply_pb(doc.add_paragraph(style=style))
    if text:
        r = p.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


PB = {"next": False}


def page_break():
    """Mark the next paragraph to start on a new page (avoids blank pages when a page is full)."""
    PB["next"] = True


def _apply_pb(p):
    if PB["next"]:
        p.paragraph_format.page_break_before = True
        PB["next"] = False
    return p


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)


def team(text="[TEAM TO WRITE]"):
    p = doc.add_paragraph(style="Normal")
    r = p.add_run(text)
    r.bold = True
    r.font.color.rgb = RED
    return p


def notes(points, sample=None, words=None):
    """Writing notes block: bullets + optional sample paragraph. Team rewrites in own words."""
    hdr = "Writing notes" + (f" (target about {words} words)" if words else "")
    para(hdr, "Writing Note", bold=True)
    for pt in points:
        para("•  " + pt, "Writing Note")
    if sample:
        para("Sample paragraph (rewrite fully in your own words; do not paste):", "Writing Note", bold=True)
        para(sample, "Sample Para")
    team()


# figure / table / equation counters
CH = {"n": 0, "fig": 0, "tab": 0, "eq": 0}
FIGLIST, TABLIST = [], []


def figure(path, caption, width_cm=13.5):
    CH["fig"] += 1
    num = f"{CH['n']}.{CH['fig']}"
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Cm(width_cm))
    para(f"Figure {num} {caption}", "Figure Caption")
    FIGLIST.append(num)
    return num


def table(caption, header, rows, widths_cm=None, note=None):
    CH["tab"] += 1
    num = f"{CH['n']}.{CH['tab']}"
    para(f"Table {num} {caption}", "Table Caption")
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(str(h)); r.bold = True; r.font.size = Pt(11); r.font.name = "Times New Roman"
        c.paragraphs[0].style = st["Table Text"]
        shade(c, "D9E2F3")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].style = st["Table Text"]
            r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(11); r.font.name = "Times New Roman"
    if widths_cm:
        t.autofit = False
        for i, w in enumerate(widths_cm):
            t.columns[i].width = Cm(w)
        for row in t.rows:
            for i, w in enumerate(widths_cm):
                row.cells[i].width = Cm(w)
    if note:
        para(note, "Table Text", italic=True, size=10)
    doc.add_paragraph(style="Table Text")
    TABLIST.append(num)
    return num


def eq(expr):
    CH["eq"] += 1
    num = f"({CH['n']}.{CH['eq']})"
    p = doc.add_paragraph(style="Equation")
    p.paragraph_format.tab_stops.add_tab_stop(Cm(13.5), alignment=2)
    r = p.add_run("\t" + expr + "\t" + num)
    r.italic = False
    p.paragraph_format.tab_stops.add_tab_stop(Cm(6.75), alignment=1)
    return num


def chapter(n, title):
    CH.update(n=n, fig=0, tab=0, eq=0)
    if n > 1:
        page_break()
    para(f"CHAPTER {n}", "Chapter Label")
    h = doc.add_heading(title.upper(), level=1)
    h.paragraph_format.space_after = Pt(30)


def h2(t):
    doc.add_heading(t.upper(), level=2)


def h3(t):
    doc.add_heading(t, level=3)


# ================================================================== TITLE PAGE (Annexure I-A)
sec = doc.sections[0]
set_margins(sec)
page_numbering(sec, "lowerRoman", start=1, show=False)
sec.different_first_page_header_footer = True


def tp(text, size, bold=True, italic=False, after=6, spacing=1.15):
    p = para(text, "Normal", bold=bold, italic=italic, size=size, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=after)
    p.paragraph_format.line_spacing = spacing
    return p


tp(TITLE, 18, after=18, spacing=1.5)
tp("PHASE I REPORT", 14, after=18)
tp("Submitted by", 14, italic=True, after=4)
for n_, r_ in TEAM:
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(f"{n_}   ({r_})"); r.bold = True; r.font.size = Pt(16)

tp("in partial fulfillment for the award of the degree of", 14, bold=True, italic=True, after=12)
tp("BACHELOR OF ENGINEERING", 16, after=0)
tp("in", 14, after=0)
tp("ELECTRICAL AND ELECTRONICS ENGINEERING", 16, after=8)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(AS / "ssn_logo.png"), width=Cm(3.2))
tp("Department of", 16, after=0)
tp("Electrical and Electronics Engineering", 16, after=0)
tp("Sri Sivasubramaniya Nadar College of Engineering", 16, after=0)
tp("(An Autonomous Institution, Affiliated to Anna University)", 12, after=0)
tp("Rajiv Gandhi Salai (OMR), Kalavakkam - 603 110", 14, after=12)
tp("NOVEMBER 2026", 14, after=0)

# ================================================================== BONAFIDE (Annexure II-B layout)
page_break()
tp("Sri Sivasubramaniya Nadar College of Engineering", 16, after=0)
tp("(An Autonomous Institution, Affiliated to Anna University)", 12, after=18)
tp("BONAFIDE CERTIFICATE", 16, after=18)
p = doc.add_paragraph(style="Normal")
p.paragraph_format.line_spacing = 1.9
p.paragraph_format.first_line_indent = Cm(1.27)
def _r(t, b=False):
    r = p.add_run(t); r.bold = b; r.font.size = Pt(14)
_r("Certified that this Report titled “"); _r(TITLE, True); _r("” is the bonafide work of “")
for i, (n_, r_) in enumerate(TEAM):
    _r(n_.title(), True); _r(f" ({r_})" + (", " if i < 1 else (" and " if i == 1 else "")))
_r("” who carried out the project work under my supervision.")
p = doc.add_paragraph(style="Normal")
p.paragraph_format.line_spacing = 2.0
p.paragraph_format.first_line_indent = Cm(1.27)
r = p.add_run("Certified further that to the best of my knowledge the work reported herein does not form part of any "
              "other thesis or dissertation on the basis of which a degree or award was conferred on an earlier "
              "occasion on this or any other candidate."); r.font.size = Pt(14)
para("")
sig = doc.add_table(rows=7, cols=2)
L = ["SIGNATURE", "[NAME OF HOD]  [TEAM TO FILL]", "HEAD OF THE DEPARTMENT", "Professor and Head",
     DEPT, "SSN College of Engineering", "Kalavakkam - 603 110"]
Rr = ["SIGNATURE", "Dr. RAJESH PANDA", "SUPERVISOR", "Professor", DEPT, "SSN College of Engineering", "Kalavakkam - 603 110"]
for i in range(7):
    for j, txt in enumerate((L[i], Rr[i])):
        c = sig.rows[i].cells[j]; c.text = ""
        rr = c.paragraphs[0].add_run(txt); rr.font.size = Pt(11)
        c.paragraphs[0].paragraph_format.line_spacing = 1.0; rr.bold = i in (0, 2) or i == 1
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
para("Submitted for project viva-voce examination held on ...............................", size=12)
ex = doc.add_table(rows=1, cols=2)
for c, txt in zip(ex.rows[0].cells, ("EXTERNAL EXAMINER", "INTERNAL EXAMINER")):
    c.text = ""; rr = c.paragraphs[0].add_run(txt); rr.bold = True; rr.font.size = Pt(12)
    c.paragraphs[0].paragraph_format.space_before = Pt(30)

# ================================================================== ABSTRACT
page_break()
para("ABSTRACT", "Front Heading")
notes([
    "Max 2 pages, TNR 14, double spacing (set the final text to 14 pt, double line spacing).",
    "Problem: machines, compressors, fans and high-bay lights in Indian MSME factories keep drawing power when no part is being cut and no operator is present.",
    "What exists: the Jetson Nano edge node (DeepStream, TensorRT FP16, ResNet10) that turns a camera feed into a filtered person count. IMPLEMENTED.",
    "What is new: machine ROIs + CT activity sensing + a four-state machine state machine with T1/T2 timers, ADVISORY vs AUTO modes, and zone rules for lights, fans, conveyor and compressor. MODELLED.",
    f"Key numbers (Monte-Carlo, {s5['days']:,} days): mean saving {f1(s5['mean_pct'])} % (P5 {f1(s5['p5_pct'])} %, P95 {f1(s5['p95_pct'])} %), "
    f"{f0(a5['kwh'])} kWh/yr, Rs {f0(a5['rs_total'])}/yr, {f1(a5['co2_t'])} t CO2/yr, full-shop payback {f1(s8['full_shop_payback_months'])} months.",
    f"Honest limits: maximum demand barely changes ({f1(s5['md_base_mean'])} to {f1(s5['md_ctrl_mean'])} kVA); savings are modelled, not measured.",
    "End with keywords: edge AI, Jetson Nano, idle energy, machine tools, occupancy, MSME, energy management.",
], words="350 to 450")

# ================================================================== ACKNOWLEDGEMENT
page_break()
para("ACKNOWLEDGEMENT", "Front Heading")
notes(["Max 1 page, double spacing. Thank: Chairman/President, Principal, HOD EEE, guide Dr. Rajesh Panda, review panel and the industry experts whose Review 3 feedback led to the manufacturing extension, lab staff, families.",
       "Student names typed in capitals at the bottom right, with signatures above."], words="150 to 200")

# ================================================================== TOC / LOT / LOF
page_break()
para("TABLE OF CONTENTS", "Front Heading")
para("In Word: right-click the field below and choose Update Field after the final edit. Reformat into the "
     "Annexure III table layout (CHAPTER NO. | TITLE | PAGE NO.) before printing.", "Writing Note")
field(_apply_pb(doc.add_paragraph()), 'TOC \\o "1-3" \\h \\z \\u')
page_break()
para("LIST OF TABLES", "Front Heading")
field(_apply_pb(doc.add_paragraph()), 'TOC \\h \\z \\t "Table Caption,1"')
page_break()
para("LIST OF FIGURES", "Front Heading")
field(_apply_pb(doc.add_paragraph()), 'TOC \\h \\z \\t "Figure Caption,1"')

# ================================================================== SYMBOLS / ABBREVIATIONS
page_break()
para("LIST OF SYMBOLS AND ABBREVIATIONS", "Front Heading")
SYM = [("a_k(t)", "Machine activity of machine k (1 = cutting), from CT current"),
       ("o_k(t)", "Operator presence in the ROI of machine k (camera, filtered)"),
       ("n_j(t)", "Person count in floor zone j"),
       ("P(t)", "Instantaneous active power, kW"), ("E", "Energy, kWh"), ("Δt", "Simulation time step, s"),
       ("T1, T2", "Standby and deep-standby timers, min"), ("MD", "Maximum demand, kVA (15-min block)"),
       ("CD", "Contract demand, kVA"), ("PF", "Power factor"), ("LF", "Load factor"),
       ("IER", "Idle-energy ratio (energy performance indicator)"), ("EF", "Grid CO2 emission factor, kg/kWh"),
       ("c_E, c_D", "Energy charge (Rs/kWh) and demand charge (Rs/kVA/month)")]
ABB = [("BEE", "Bureau of Energy Efficiency"), ("CEA", "Central Electricity Authority"), ("CNC", "Computer Numerical Control"),
       ("CT", "Current Transformer"), ("DPDP", "Digital Personal Data Protection (Act, 2023)"), ("EnMS", "Energy Management System"),
       ("EnPI", "Energy Performance Indicator"), ("FP16", "16-bit floating point"), ("HT", "High Tension (supply category)"),
       ("IPMVP", "International Performance Measurement and Verification Protocol"), ("M&V", "Measurement and Verification"),
       ("MQTT", "Message Queuing Telemetry Transport"), ("MSME", "Micro, Small and Medium Enterprises"),
       ("NILM", "Non-Intrusive Load Monitoring"), ("OPC UA", "Open Platform Communications Unified Architecture"),
       ("PAT", "Perform, Achieve and Trade"), ("PyDS", "Python bindings for DeepStream"), ("ROI", "Region of Interest"),
       ("TNERC", "Tamil Nadu Electricity Regulatory Commission"), ("VMC", "Vertical Machining Centre")]
CH["n"] = 0
t = doc.add_table(rows=0, cols=2); t.style = "Table Grid"
for a_, b_ in SYM + ABB:
    cells = t.add_row().cells
    for c, v in zip(cells, (a_, b_)):
        c.text = ""; c.paragraphs[0].style = st["Table Text"]; c.paragraphs[0].add_run(v).font.size = Pt(11)

# ================================================================== MAIN TEXT (arabic numbering)
sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
set_margins(sec2)
sec2.different_first_page_header_footer = False
page_numbering(sec2, "decimal", start=1, show=True)

# ------------------------------------------------------------------ CHAPTER 1
chapter(1, "Introduction")
h2("1.1 General")
notes([
    "Industry used about 42 % of India's electricity in FY 2023-24 (CEA General Review 2025) [CHECK Table 1.4].",
    "Machine tools: only 14.8 % of input energy went to actual cutting in a studied automotive line; 85.2 % to auxiliary and constant loads (Gutowski et al. 2005/2006, secondary citation, check primary).",
    "Fixed or readiness load keeps running when the machine waits for material, the operator is away, or during breaks.",
    "Our Phase I work (Reviews 1 to 3) built an edge node that turns a camera into an occupancy signal; experts asked us to apply it to factories and to loads beyond HVAC.",
], sample=("A machining centre does not stop drawing power when it stops cutting. Coolant pumps, hydraulics, chip "
           "conveyors and spindle cooling keep running while the operator fetches material or takes a break. "
           "Studies of production lines report that only a small share of the electricity reaches the cutting "
           "process itself. In a typical Indian machining shop this idle load is paid for at the full industrial "
           "tariff and adds to the plant's carbon footprint."), words=250)
table("Context numbers used in this report", ["Quantity", "Value", "Source"], [
    ["Industry share of India's electricity, FY 2023-24", "about 42 %", "CEA (2025) via ORF"],
    ["Machining share of line energy (automotive line)", "14.8 %", "Gutowski et al. (2005)"],
    ["Compressed air share of plant electricity", "about 10 % (30 % or more at some sites)", "US DOE (2003)"],
    ["TN HT-I industrial tariff from 1 July 2025", "Rs 7.50/kWh + Rs 608/kVA/month", "TNERC (2025)"],
    ["Grid emission factor FY 2024-25", "0.710 kg CO2/kWh", "CEA (2025) v21.0"],
], [6.5, 4.0, 3.0])
h2("1.2 Need for the study")
notes(["Machines are often left powered through breaks, material waits, breakdowns and even overnight.",
       "Existing switch-off policies use only a timer since the last part (Mouzon et al. 2007; Squeo et al. 2019); they do not know if an operator is standing at the machine.",
       "Most Indian factories already have CCTV. Adding an edge analytics layer reuses that sensor at low cost.",
       "HT bills charge both energy (kWh) and maximum demand (kVA), so both must be analysed."], words=250)
h2("1.3 Objectives of the study")
table("Objectives and status", ["No.", "Objective", "Status"], [
    ["1", "Detect people live on a Jetson Nano edge node", "IMPLEMENTED"],
    ["2", "Convert detections into a stable presence signal", "IMPLEMENTED"],
    ["3", "Extend to machine and zone ROIs with CT-based activity sensing", "MODELLED"],
    ["4", "Design a safe machine state machine with ADVISORY and AUTO modes", "MODELLED"],
    ["5", "Quantify kWh, Rs (energy and demand), kVA, load factor and CO2 for a reference MSME shop", "MODELLED"],
    ["6", "Test robustness, sensitivity and timer trade-offs", "MODELLED"],
    ["7", "Define the integration (PROFIenergy, Modbus, MQTT) and M&V path", "FUTURE"],
], [1.2, 9.3, 3.0])
h2("1.4 Scope and limitations")
notes(["In scope: 10-machine CNC shop, compressor, conveyor, lighting, extraction fans, 2 shifts; office room kept as a second case.",
       "Out of scope: furnaces, moulding barrels and any thermal process (advisory only); no automatic restart of machines.",
       "All savings are MODELLED; measured validation is FUTURE work. State this clearly."], words=150)
h2("1.5 Organisation of the report")
notes(["One or two lines per chapter (Chapters 2 to 8)."], words=150)

# ------------------------------------------------------------------ CHAPTER 2
chapter(2, "Literature Review and Research Gap")
h2("2.1 Energy use of machine tools in non-productive states")
notes(["Gutowski, Dahmus and Thiriez (2006): specific energy is not constant; process rate is the main driver.",
       "Kara and Li (2011): SEC = C0 + C1/MRR; the fixed term C1 is spread over output, so idle time inflates it.",
       "Li, Zein, Kara and Herrmann (2011): fixed (readiness) energy is under-studied; six machines assessed.",
       "Denkena et al. (2020) CIRP keynote: machine and process measures; retrofitting is an open question.",
       "Mori et al. (2011): DMG Mori cut energy by changing cutting conditions and synchronising spindle and feed acceleration.",
       "Heidenhain (2011): example machining centre 13 kW mean roughing; 5.1 kW just for coolant conditioning and pumping."], words=500)
h2("2.2 Switching idle machines to standby")
notes(["Mouzon, Yildirim and Twomey (2007): turn off under-used machines when idle time exceeds a break-even value.",
       "Squeo, Frigerio and Matta (2019): several sleep states per component on a 5-axis machining centre.",
       "Thermal warm-up limits: Fraunhofer IPK (up to 75 % of geometric errors are thermal); euspen studies on cooler standby.",
       "Link to our design: T1 (standby) and T2 (deep standby), whitelist, warm-up penalty charged in the model."], words=450)
h2("2.3 Vision-based occupancy and machine-state sensing")
notes(["Tien et al. (2021): Faster R-CNN detects occupancy (97.3 %) and equipment use (80.8 %) in an office.",
       "Hu et al. (2023), Choi et al. (2022), Calautit et al. (2024): camera-based counting for buildings (from Review 3).",
       "Kong et al. (2022): 17 to 24 % HVAC savings side by side; Lin et al. (2023): 6.1 % projected whole-building saving.",
       "Industrial worker localisation detects walking operators in about two-thirds of frames: occlusion is real, so filter + second sensor."], words=450)
h2("2.4 Current-based machine monitoring (NILM)")
notes(["Gebbe et al. (2019): NILM for manufacturing machines, 85 % or better for most loads.",
       "Suzuki, Kohmoto and Ogatsu (2017): one current sensor, several machines, factorial HMM.",
       "Machine-tool operating-state recognition from power data with deep learning (Sensors 2022): cutting, starting, standby."], words=300)
h2("2.5 Other idle loads in a factory")
notes(["Compressed air: about 10 % of plant electricity, leaks 20 to 30 % of output in poorly maintained plants, improvements save 20 to 50 % (DOE 2003).",
       "Lighting: occupancy sensors save about 24 % on average (Williams et al. 2012).",
       "Conveyors and extraction fans: no specific source found; values are labelled assumptions."], words=250)
h2("2.6 Research gap")
table("Summary of related work and the gap", ["Work", "Sensing", "Decision", "Gap for our problem"], [
    ["Mouzon et al. (2007)", "Schedule / time", "Turn off idle machines", "No presence sensing"],
    ["Squeo et al. (2019)", "Time since last part", "Multi-level sleep", "No presence sensing"],
    ["Tien et al. (2021)", "Camera (office)", "HVAC / plug loads", "Buildings only"],
    ["Kong et al. (2022); Lin et al. (2023)", "Occupancy sensors", "HVAC control", "Buildings only"],
    ["Gebbe et al. (2019); Suzuki et al. (2017)", "Current (NILM)", "Monitoring only", "No operator context, no action"],
    ["This work", "Camera ROI + CT current on an edge node", "Machine standby + zone loads, ADVISORY/AUTO", "Fills the gap (modelled)"],
], [3.8, 3.4, 3.3, 3.0])
notes(["One paragraph stating the gap: no reported system fuses camera operator presence and current-based machine state on an edge node to drive standby decisions for machines and shared loads with a safety whitelist."], words=150)

# ------------------------------------------------------------------ CHAPTER 3
chapter(3, "System Architecture")
h2("3.1 Overview")
figure(AS / "fig_architecture.png", "System architecture with implementation status")
notes(["Walk through the three rows of Figure 3.1. Stress: the implemented pipeline is kept and extended, not replaced.",
       "Only metadata leaves the node."], words=300)
h2("3.2 Zones and regions of interest")
figure(AS / "fig_shop_layout.png", "Reference machining shop with zones, machine ROIs and cameras")
notes(["Each machine has an operator ROI drawn in front of it (nvdsanalytics polygon).",
       "Zones 1 to 3 hold machines; Zone 4 is the aisle, stores and inspection area.",
       "Zone 3 holds precision machines, so it runs in ADVISORY mode."], words=250)
h2("3.3 Signal conditioning (temporal filter)")
para("The presence signal from the detector is passed through an asymmetric persistence filter, kept from Phase I:")
eq("o_f(t) = 1  if raw presence held for t_rise = 10 s;   o_f(t) = 0  if absence held for t_fall = 60 s")
eq("a_f(t) = 1  if I_k(t) > I_th;   a_f(t) = 0  only after I_k(t) < I_th for 30 s")
notes(["Explain why rise is short (serve the operator fast) and fall is long (do not sleep a machine when the operator bends down or is briefly hidden).",
       "Phase I result to quote: 2,633 to 9 state changes per day, 99.1 % time in correct state (office, model v1)."], words=200)
h2("3.4 Machine state machine")
figure(AS / "fig_state_machine.png", "Machine state machine with transition conditions")
mp = C["machine_power_kw"]
table("Machine states, conditions, power and action", ["State", "Condition", "Power (kW)", "Action"], [
    ["PROCESSING", "a = 1", f1(mp["processing"]), "None"],
    ["IDLE-ATTENDED", "a = 0, o = 1", f1(mp["idle"]), "None (set-up, measuring, tool change)"],
    ["IDLE-UNATTENDED", f"a = 0, o = 0 for more than T1 = {C['control']['T1_min']} min", f1(mp["standby"]) + " (standby)", "ADVISORY alert; AUTO standby if whitelisted"],
    ["DEEP STANDBY", f"unattended more than T2 = {C['control']['T2_min']} min and whitelisted", f2(mp["deep_standby"]), "AUTO deep standby; operator restarts with warm-up"],
], [3.2, 4.2, 2.3, 3.8], note="Power values are ASSUMED for a vertical machining centre (Chapter 5).")
h2("3.5 Multi-load actions")
table("Rules for shared loads", ["Load", "Baseline", "Rule with edge node", "Mode"], [
    ["Conveyor (2.2 kW)", "Runs whole shift", "Stop when no line machine processing for 2 min", "AUTO"],
    ["Compressor (22 kW)", "Runs whole shift", "Stop and isolate when whole shop idle for 5 min", "AUTO"],
    ["High-bay lighting (3.6 kW per zone)", "All on in shift", "Dim to 10 % when zone empty for 2 min", "AUTO"],
    ["Extraction fan (3.7 kW per zone)", "On in shift", "Off when zone empty and no machine processing for 5 min", "AUTO"],
], [3.6, 2.6, 5.6, 1.7])
h2("3.6 Advisory and automatic modes")
notes(["ADVISORY default: dashboard alert with machine, minutes unattended, kW and Rs per hour lost; supervisor decides.",
       "AUTO only on a whitelist; never furnaces, moulding barrels, heat treatment, or a machine with a cycle in progress.",
       "Node never restarts a machine; operator presses Resume (machinery safety principle)."], words=300)
h2("3.7 Privacy and worker acceptance")
notes(["Process on device, publish counts and states only, no face recognition, no image storage.",
       "DPDP Act 2023: purpose limitation and minimisation; core provisions due by May 2027 [CHECK].",
       "Signage and works-committee consent; use data for energy, not for appraisals."], words=250)

# ------------------------------------------------------------------ CHAPTER 4
chapter(4, "Implementation of the Edge Node")
h2("4.1 Hardware")
table("Edge node hardware (IMPLEMENTED)", ["Item", "Specification", "Cost (Rs)"], [
    ["NVIDIA Jetson Nano Developer Kit", "4 GB, 128-core Maxwell GPU", "13,000"],
    ["Camera", "Logitech C920 USB (existing CCTV in deployment)", "1,300"],
    ["Storage", "64 GB microSD", "700"], ["Power supply", "5 V / 4 A", "500"],
    ["Cooling", "Heatsink + fan", "600"], ["Networking and misc.", "Wi-Fi, cabling", "1,400"],
    ["Total", "", "17,500"],
], [4.5, 6.5, 2.5])
figure(AS / "prototype_bench.jpg", "Prototype bench set-up with Jetson Nano and live output", 12.5)
h2("4.2 Software pipeline")
table("DeepStream pipeline elements", ["Stage", "Element", "Function"], [
    ["Capture", "v4l2src / GStreamer", "Read camera frames"], ["Batching", "nvstreammux", "Form GPU batches"],
    ["Inference", "nvinfer (ResNet10, TensorRT FP16)", "Detect persons"], ["Metadata", "PyDS probe", "Read object metadata, count persons"],
    ["Filtering", "Python", "Rise/fall persistence filter"], ["Output", "live_state.json", "State and load for dashboard"],
], [3.0, 5.0, 5.5])
notes(["Describe each stage in your own words with the config file names you used. Insert short code excerpts in Appendix 3.",
       "Add the TensorRT engine build step and why FP16 suits the Nano."], words=600)
h2("4.3 Live detection and dashboard")
figure(AS / "live_detection.jpg", "Live person detection on the Jetson Nano", 7.0)
figure(AS / "dashboard.jpg", "Live energy dashboard (office mode)", 7.0)
notes(["Explain the dashboard fields. State that the kW and Rs values shown are modelled from state, not metered."], words=300)
h2("4.4 Extension for the factory (planned)")
notes(["nvdsanalytics ROI config per machine; INA219/SCT-013 + ADS1115 activity input; relay output; mode switch.",
       "Point to the bench demo plan (Appendix 4)."], words=300)
h2("4.5 Measurements to report")
team("[TEAM TO MEASURE AND FILL] FPS, end-to-end latency, Jetson input power (USB meter), precision and recall on 200 labelled frames.")

# ------------------------------------------------------------------ CHAPTER 5
chapter(5, "Electrical Energy Modelling")
h2("5.1 Machine power model")
para("Each machine k is in one state s_k(t) at every time step; its power is taken from the state table:")
eq("P_k(t) = P_state( s_k(t) )")
eq("P_shop(t) = Σ_k P_k(t) + P_comp(t) + P_conv(t) + Σ_j [ P_light,j(t) + P_fan,j(t) ]")
ol = C["other_loads_kw"]
table("Power assumptions (model v2)", ["Load", "Value", "Basis"], [
    ["CNC processing", f"{f1(mp['processing'])} kW", "ASSUMED, consistent with 13 kW roughing example (Heidenhain 2011)"],
    ["CNC idle", f"{f1(mp['idle'])} kW", "ASSUMED 40 % of processing; swept 0.25 to 0.55"],
    ["CNC standby / deep standby", f"{f1(mp['standby'])} / {f2(mp['deep_standby'])} kW", "ASSUMED"],
    ["Warm-up after deep standby", f"{f1(mp['warmup_kw'])} kW for {mp['warmup_min']} min", "ASSUMED"],
    ["Compressor", f"{f1(ol['compressor_full'])} kW, unload {int(100 * ol['compressor_unload_frac'])} %, leak {int(100 * ol['compressor_leak_frac'])} %", "Leak range from DOE (2003)"],
    ["Conveyor", f"{f1(ol['conveyor'])} kW", "ASSUMED"],
    ["Lighting per zone", f"{f1(ol['lighting_per_zone'])} kW", "ASSUMED 24 x 150 W LED"],
    ["Fan per zone", f"{f1(ol['fan_per_zone'])} kW", "ASSUMED"], ["Power factor", f2(ol["power_factor"]), "ASSUMED"],
], [3.8, 4.3, 5.4])
h2("5.2 Compressor model")
eq("P_comp = P_full [ f + (1 - f) α_u ],   f = min( 1, λ_leak + β N_proc )")
notes(["α_u: unloaded fraction; λ_leak: leak demand; β: air demand per processing machine; N_proc: machines processing."], words=150)
h2("5.3 Energy, demand and cost")
eq("E = Σ_t P(t) Δt")
eq("E_saved = E_base - E_ctrl")
eq("MD = max_b [ (1/n) Σ_(t in b) P(t) ] / PF")
eq("C = E c_E + max( MD, 0.9 CD ) c_D")
eq("LF = P_avg / P_peak")
eq("IER = E_non-processing / E_total")
eq("CO2 = E_saved × EF")
table("Tariff and emission inputs", ["Item", "Value", "Source"], [
    ["Energy charge c_E", f"Rs {C['tariff']['energy_rs_per_kwh']:.2f}/kWh", "TNERC T.O. No. 6 of 2025, HT-I"],
    ["Demand charge c_D", f"Rs {C['tariff']['demand_rs_per_kva_month']}/kVA/month", "TNERC T.O. No. 6 of 2025, HT-I"],
    ["Billing demand", "max(recorded, 90 % of CD)", "TNERC"],
    ["Contract demand CD", f"{C['tariff']['contract_demand_kva']} kVA", "ASSUMED"],
    ["Emission factor", f"{C['carbon']['ef_kg_per_kwh']} kg CO2/kWh", "CEA v21.0, FY 2024-25"],
    ["Working days", f"{C['meta']['days_per_year']} per year", "ASSUMED"],
], [4.0, 4.5, 5.0])
h2("5.4 Operations model of the reference shop")
op = C["operations"]
table("Shift events per machine (stochastic model)", ["Event", "Model", "Operator"], [
    ["Machining cycle", f"exponential, mean {op['cycle_proc_min']} min; load/unload {op['load_unload_min']} min", "present"],
    ["Start-of-shift set-up", f"{op['setup_start_min']} min", "present"],
    ["Tea breaks", f"{op['tea_min']} min at +2 h and +6 h", "absent"],
    ["Lunch", f"{op['lunch_min']} min at +4 h", "absent"],
    ["Material wait", f"Poisson {op['material_wait_rate']}/shift, lognormal median {op['material_wait_median_min']} min", f"absent with p = {op['material_wait_p_absent']}"],
    ["Tool change", f"Poisson {op['tool_change_rate']}/shift, mean {op['tool_change_min']} min", "present"],
    ["Breakdown", f"p = {op['breakdown_prob']}/shift, {op['breakdown_min'][0]} to {op['breakdown_min'][1]} min", f"absent with p = {op['breakdown_p_absent']}"],
    ["Left on overnight", f"p = {op['night_left_on_prob']} per machine", "absent"],
], [3.3, 7.0, 3.2])
notes(["Detector model: 10 % per-sample miss (as Phase I), 0.2 % false positive, occlusion bursts 2 per shift with mean 90 s.",
       f"Time step Δt = {C['meta']['dt_s']} s, fixed seed {C['meta']['seed']}, all inputs in assumptions.yaml (Appendix 1)."], words=250)

# ------------------------------------------------------------------ CHAPTER 6
chapter(6, "Simulation Results and Discussion")
para("All results in this chapter are MODELLED (model v2). Numbers are generated by the code in Appendix 2.", italic=True)
h2("6.1 S1: one machine over one shift")
figure(FIG / "S1_one_machine_shift.png", "Activity, operator presence and power of one machine over one shift")
notes([f"Machine M{R['S1']['machine'] + 1}: {f1(R['S1']['E_base_kwh'])} to {f1(R['S1']['E_ctrl_kwh'])} kWh in the shift ({f1(R['S1']['saving_pct'])} %).",
       "Point to the standby dips during tea break, lunch and material waits; idle-attended periods are left alone."], words=250)
h2("6.2 S2: whole shop cumulative energy")
figure(FIG / "S2_cumulative_energy.png", "Cumulative energy of the shop on the reference day")
notes([f"Reference day: {f0(rd['E_base_kwh'])} to {f0(rd['E_ctrl_kwh'])} kWh ({f1(rd['saving_pct'])} %).",
       f"Quote the Monte-Carlo mean ({f1(s5['mean_pct'])} %) as the headline; the reference day is one sample."], words=200)
h2("6.3 S3: savings by load type")
figure(FIG / "S3_breakdown_by_load.png", "Energy by load type, baseline and controlled")
table("Mean daily saving by load type (Monte-Carlo)", ["Load", "Saving (kWh/day)"],
      [[k, f1(v)] for k, v in s5["by_load_saving_kwh_day"].items()], [8.0, 5.5])
notes(["Machines give the largest absolute saving; lighting and fans the largest percentage. The same camera drives all of them, which answers the experts' second point."], words=250)
h2("6.4 S4: load-duration curve, load factor and maximum demand")
figure(FIG / "S4_load_duration.png", "Load-duration curve of the shop")
s4 = R["S4"]
table("Electrical indices (reference day)", ["Index", "Baseline", "Controlled"], [
    ["Average power (kW)", f1(s4["avg_base_kw"]), f1(s4["avg_ctrl_kw"])],
    ["Peak power (kW)", f1(s4["peak_base_kw"]), f1(s4["peak_ctrl_kw"])],
    ["Load factor", f2(s4["lf_base"]), f2(s4["lf_ctrl"])],
    ["Maximum demand, 15 min (kVA)", f1(s4["md_base_kva"]), f1(s4["md_ctrl_kva"])],
], [6.5, 3.5, 3.5])
notes(["Honest claim: energy falls; peak and MD hardly change because the peak occurs when all machines cut together. Load factor falls since average falls and peak stays.",
       "Demand saving is therefore small (Table 6.4); a demand-limiting feature is future work."], words=300)
h2("6.5 S5: Monte-Carlo robustness")
figure(FIG / "S5_monte_carlo.png", f"Distribution of daily saving over {s5['days']:,} simulated days")
table("Headline results (Monte-Carlo)", ["Quantity", "Value"], [
    ["Mean shop energy, baseline to controlled", f"{f0(s5['mean_E_base_kwh'])} to {f0(s5['mean_E_ctrl_kwh'])} kWh/day"],
    ["Mean saving (P5 / P95)", f"{f1(s5['mean_pct'])} % ({f1(s5['p5_pct'])} / {f1(s5['p95_pct'])} %)"],
    ["Days with positive saving", f"{f1(s5['positive_days_pct'])} %"],
    ["Energy avoided", f"{f0(a5['kwh'])} kWh/yr"],
    ["Cost saving, energy / demand / total", f"Rs {f0(a5['rs_energy'])} / Rs {f0(a5['rs_demand'])} / Rs {f0(a5['rs_total'])} per year"],
    ["CO2 avoided", f"{f1(a5['co2_t'])} t/yr"],
    ["Idle-energy ratio (EnPI)", f"{f1(100 * s5['ier_base_mean'])} % to {f1(100 * s5['ier_ctrl_mean'])} %"],
    ["Mean maximum demand", f"{f1(s5['md_base_mean'])} to {f1(s5['md_ctrl_mean'])} kVA"],
], [6.5, 7.0])
h2("6.6 S6: sensitivity analysis")
figure(FIG / "S6_tornado.png", "One-at-a-time sensitivity of the annual saving")
notes(["The idle-to-processing power ratio matters most, followed by the number of idle events and the tariff.",
       "These are the two numbers that must be measured on a real machine (CT clamp) before deployment.",
       "Advisory compliance matters little here because only 4 of 10 machines are advisory."], words=300)
h2("6.7 S7: timer study (false and nuisance standby)")
figure(FIG / "S7_timer_tradeoff.png", "Timer T1 versus saving and nuisance or false standby events")
table("Timer study results", ["T1 (min)", "Saving (%)", "Nuisance per machine-shift", "False standby per machine-shift"],
      [[r["T1_min"], f2(r["saving_pct"]), f2(r["nuisance_per_machine_shift"]), f"{r['false_standby_per_machine_shift']:.3f}"] for r in R["S7"]],
      [2.5, 3.0, 4.0, 4.0])
notes(["Key engineering result: nuisance standbys peak when T1 sits just under the 15-min tea break; T1 = 3 min gives more saving and fewer nuisance events than 5 to 10 min.",
       "Very short T1 (1 min) raises false standbys when an operator is briefly hidden.",
       "Recommendation: T1 = 3 min, plus a planned pause command at the start of scheduled breaks (PROFIenergy)."], words=350)
h2("6.8 S8: payback per node")
figure(FIG / "S8_payback.png", "Simple payback versus machines covered per edge node")
notes([f"Full shop, including actuation and integration: Rs {f0(s8['full_shop_cost_rs'])}, payback {f1(s8['full_shop_payback_months'])} months (CCTV reused); "
       f"Rs {f0(s8['full_shop_cost_new_cams_rs'])} and {f1(s8['full_shop_payback_new_cams_months'])} months with new cameras.",
       f"The node's own electricity is {f0(s8['node_kwh_yr'])} kWh/yr, {f2(s8['node_share_of_saving_pct'])} % of the saving.",
       "Payback is short because one node serves many machines and shared loads; prices are indicative."], words=250)
h2("6.9 S9: generality, office case")
figure(FIG / "S9_office_vs_shop.png", "Same edge layer applied to an office room and a machining shop")
notes([f"Office (model v1): {f1(s9['saving_pct'])} %, {f0(s9['annual_kwh'])} kWh/yr; payback corrected from {f1(s9['payback_gross_months'])} to {f1(s9['payback_net_months'])} months once the node's own load is subtracted.",
       "The factory saving in percent is lower because machines are busy most of the shift, but the absolute saving is far larger."], words=200)
h2("6.10 Discussion")
notes(["Compare with literature: building studies 6 to 24 %; our factory figure is lower in percent but large in kWh.",
       "Limitations: assumed powers, synthetic events, no measured data, single shop type.",
       "What would change the answer: measured idle power ratio and real idle-event logs."], words=500)

# ------------------------------------------------------------------ CHAPTER 7
chapter(7, "Economics, Standards and Deployment Roadmap")
h2("7.1 Cost of a deployment")
nd = C["node"]; sa = C["site_actuation"]
table("Indicative cost for the 10-machine shop (CCTV reused)", ["Item", "Qty", "Cost (Rs)"], [
    ["Jetson Nano + PSU, SD, enclosure", "1", f0(nd["jetson_rs"] + nd["psu_sd_enclosure_rs"])],
    ["Relay / Modbus I/O module", "1", f0(nd["relay_io_modbus_rs"])],
    ["CT clamps", str(C["shop"]["n_machines"]), f0(C["shop"]["n_machines"] * nd["ct_per_machine_rs"])],
    ["CT interface (ADC / Modbus meter)", "1", f0(nd["ct_interface_rs"])],
    ["Installation misc.", "1", f0(nd["install_misc_rs"])],
    ["Lighting zone dimming interface", "4", f0(4 * sa["lighting_zone_rs"])],
    ["Fan contactors", "4", f0(4 * sa["fan_contactor_rs"])],
    ["Conveyor interlock + compressor isolation valve", "1", f0(sa["conveyor_compressor_rs"])],
    ["Integration and commissioning", "1", f0(sa["integration_rs"])],
    ["Total", "", f0(s8["full_shop_cost_rs"])],
], [8.0, 1.5, 4.0], note="Indicative retail prices, October 2026 (ASSUMED).")
h2("7.2 Standards and control paths")
table("Standards and their role", ["Standard", "What it does", "Use in this work"], [
    ["ISO 14955-1:2017", "Design method for energy-efficient machine tools", "Reference for machine energy states"],
    ["ISO 14955-2", "Measurement of energy supplied to machine tools", "Future M&V of machine kW"],
    ["PROFIenergy (PI)", "PROFINET pause and standby commands", "AUTO path for PROFINET machines"],
    ["OPC UA (IEC 62541) / umati", "Vendor-neutral machine data model", "Second source of machine state"],
    ["Modbus TCP", "Register read/write for meters, VFDs, relays", "CT meter and relay I/O"],
    ["MQTT 5.0", "Lightweight publish/subscribe", "Node to dashboard / SCADA"],
    ["ISO 50001:2018", "Energy management system", "Where the node sits in an EnMS"],
    ["ISO 50006:2014", "Baselines and EnPIs", "Idle-energy ratio as EnPI"],
    ["ISO 50015:2014 / IPMVP", "Measurement and verification", "M&V plan (Option B)"],
], [3.5, 5.0, 5.0])
h2("7.3 Measurement and verification plan")
notes(["IPMVP Option B (retrofit isolation): CT on each machine and on compressor and lighting feeders.",
       "Baseline period 2 weeks with node in ADVISORY-only logging; reporting period 2 weeks AUTO.",
       "Normalise by parts produced (kWh/part) and by shift hours; report IER before and after."], words=400)
h2("7.4 Deployment roadmap")
notes(["Step 1 bench demo (Appendix 4); Step 2 one machine in a partner MSME (ADVISORY); Step 3 zone loads AUTO; Step 4 whitelist machines AUTO; Step 5 MQTT/SCADA integration."], words=300)

# ------------------------------------------------------------------ CHAPTER 8
chapter(8, "Conclusion and Future Work")
h2("8.1 Conclusions")
notes(["Restate each objective with its status and one number.",
       f"Headline: {f1(s5['mean_pct'])} % modelled energy saving, {f0(a5['kwh'])} kWh/yr, Rs {f0(a5['rs_total'])}/yr, {f1(a5['co2_t'])} t CO2/yr for a 10-machine shop.",
       "Honest: energy, not peak demand; modelled, not measured."], words=400)
h2("8.2 Mapping to Sustainable Development Goals")
table("SDG mapping", ["SDG", "Link"], [
    ["SDG 7 Affordable and clean energy", "Cuts avoidable electricity use in factories"],
    ["SDG 9 Industry, innovation and infrastructure", "Adds edge AI to existing CCTV in MSMEs"],
    ["SDG 12 Responsible consumption and production", "Lower energy per part produced"],
    ["SDG 13 Climate action", f"{f1(a5['co2_t'])} t CO2/yr avoided per shop (modelled)"],
], [6.0, 7.5])
h2("8.3 Future work")
notes(["Measure idle power ratio and idle events on real machines; replace assumptions.",
       "Bench demo with CT and relay; then a pilot in an MSME.",
       "Demand-limiting: stagger restarts after lunch to cut MD.",
       "PROFIenergy and OPC UA integration; detector retraining for factory PPE and occlusion."], words=300)

# ------------------------------------------------------------------ APPENDICES
page_break()
CH.update(n="A1", fig=0, tab=0, eq=0)
_apply_pb(doc.add_heading("APPENDIX 1  MODEL ASSUMPTIONS", level=1))
para("Full listing of sim_v2/assumptions.yaml (single spaced):", italic=True)
for line in (SIM / "assumptions.yaml").read_text().splitlines():
    p = doc.add_paragraph(style="Table Text")
    r = p.add_run(line); r.font.name = "Courier New"; r.font.size = Pt(8)
page_break()
_apply_pb(doc.add_heading("APPENDIX 2  SIMULATION CODE EXCERPT", level=1))
src = (SIM / "model.py").read_text().splitlines()
start = next(i for i, l in enumerate(src) if l.startswith("def simulate("))
for line in src[start:start + 70]:
    p = doc.add_paragraph(style="Table Text")
    r = p.add_run(line); r.font.name = "Courier New"; r.font.size = Pt(7.5)
page_break()
_apply_pb(doc.add_heading("APPENDIX 3  EDGE NODE CODE EXCERPTS", level=1))
team("[TEAM TO INSERT] DeepStream config (nvinfer, nvdsanalytics ROI), PyDS probe function, temporal filter, dashboard JSON writer. Keep to about 2 pages.")
page_break()
_apply_pb(doc.add_heading("APPENDIX 4  BENCH DEMONSTRATION PLAN", level=1))
for line in (ROOT / "05_DEMO_PLAN.md").read_text().splitlines():
    if line.startswith("```"):
        continue
    if line.startswith("# "):
        continue
    clean = line.replace("**", "").replace("`", "").replace(" — ", ": ").replace("—", "-").replace("–", "-")
    clean = clean.strip().lstrip("#").strip()
    if set(clean) <= set("|-: "):
        continue
    clean = clean.strip("|").replace(" | ", "  |  ")
    if clean:
        p = doc.add_paragraph(style="Table Text")
        p.add_run(clean).font.size = Pt(10)

# ------------------------------------------------------------------ REFERENCES
page_break()
_apply_pb(doc.add_heading("REFERENCES", level=1))
REFS = [
    "Calautit J.K. et al. (2024), Journal of Building Engineering [CHECK full citation from Review 3 source].",
    "Central Electricity Authority (2025), 'All India Electricity Statistics, General Review 2025', Ministry of Power, Government of India, New Delhi.",
    "Central Electricity Authority (2025), 'CO2 Baseline Database for the Indian Power Sector, User Guide Version 21.0', Ministry of Power, Government of India, New Delhi.",
    "Choi H. et al. (2022), Building and Environment, Vol. 223, 109496 [CHECK full author list and title].",
    "Denkena B., Abele E., Brecher C., Dittrich M.-A., Kara S. and Mori M. (2020), 'Energy efficient machine tools', CIRP Annals - Manufacturing Technology, Vol. 69, No. 2, pp. [CHECK].",
    "Gebbe C. et al. (2019), 'Nonintrusive load monitoring for machines used in manufacturing', arXiv:1912.01500 [CHECK full author list].",
    "Government of India (2023), 'The Digital Personal Data Protection Act, 2023', Act No. 22 of 2023, New Delhi.",
    "Gutowski T., Dahmus J. and Thiriez A. (2006), 'Electrical energy requirements for manufacturing processes', Proc. 13th CIRP Int. Conf. on Life Cycle Engineering, Leuven, pp. 623-628.",
    "Gutowski T., Murphy C., Allen D., Bauer D., Bras B., Piwonka T., Sheng P., Sutherland J., Thurston D. and Wolff E. (2005), 'Environmentally benign manufacturing: observations from Japan, Europe and the United States', Journal of Cleaner Production, Vol. 13, No. 1, pp. 1-17.",
    "HEIDENHAIN (2011), 'Aspects of energy efficiency in machine tools', Technical Information, Dr. Johannes Heidenhain GmbH, Traunreut.",
    "Hu S. et al. (2023), IEEE Internet of Things Journal, Vol. 10, No. 1, pp. 597-608 [CHECK title].",
    "ISO (2014), 'ISO 50006:2014 Energy management systems - Measuring energy performance using energy baselines and energy performance indicators', International Organization for Standardization, Geneva.",
    "ISO (2014), 'ISO 50015:2014 Energy management systems - Measurement and verification of energy performance of organizations', ISO, Geneva.",
    "ISO (2017), 'ISO 14955-1:2017 Machine tools - Environmental evaluation of machine tools - Part 1: Design methodology for energy-efficient machine tools', ISO, Geneva.",
    "ISO (2018), 'ISO 50001:2018 Energy management systems - Requirements with guidance for use', ISO, Geneva.",
    "Kara S. and Li W. (2011), 'Unit process energy consumption models for material removal processes', CIRP Annals - Manufacturing Technology, Vol. 60, No. 1, pp. 37-40.",
    "Kong M., Dong B., Zhang R. and O'Neill Z. (2022), 'HVAC energy savings, thermal comfort and air quality for occupant-centric control through a side-by-side experimental study', Applied Energy, Vol. 306, 117987.",
    "Li W., Zein A., Kara S. and Herrmann C. (2011), 'An investigation into fixed energy consumption of machine tools', Proc. 18th CIRP Int. Conf. on Life Cycle Engineering, Braunschweig, pp. 268-273.",
    "Lin G., Casillas A., Sheng M. and Granderson J. (2023), 'Performance evaluation of an occupancy-based HVAC control system in an office building', Energies, Vol. 16, No. 20, 7088.",
    "Mori M., Fujishima M., Inamasu Y. and Oda Y. (2011), 'A study on energy efficiency improvement for machine tools', CIRP Annals - Manufacturing Technology, Vol. 60, No. 1, pp. 145-148.",
    "Mouzon G., Yildirim M.B. and Twomey J. (2007), 'Operational methods for minimization of energy consumption of manufacturing equipment', International Journal of Production Research, Vol. 45, No. 18-19, pp. 4247-4271.",
    "NVIDIA (2021), 'DeepStream SDK 6.0.1 Developer Guide', NVIDIA Corporation, Santa Clara.",
    "OASIS (2019), 'MQTT Version 5.0', OASIS Standard, 7 March 2019.",
    "PROFIBUS and PROFINET International (2010), 'PROFIenergy - Technical specification for PROFINET', PI, Karlsruhe [CHECK version].",
    "Squeo M., Frigerio N. and Matta A. (2019), 'Multiple sleeping states for energy saving in CNC machining centers', Procedia CIRP, Vol. 80, pp. 144-149.",
    "Suzuki R., Kohmoto S. and Ogatsu T. (2017), 'Non-intrusive condition monitoring for manufacturing systems', Proc. 25th European Signal Processing Conf. (EUSIPCO), Kos, pp. [CHECK].",
    "Tamil Nadu Electricity Regulatory Commission (2025), 'Tariff Order No. 6 of 2025', TNERC, Chennai, 30 June 2025.",
    "Tien P.W., Wei S., Calautit J.K., Darkwa J. and Wood C. (2021), 'A computer vision-based occupancy and equipment usage detection approach for reducing building energy demand', Energies, Vol. 14, No. 1, 156.",
    "U.S. Department of Energy (2003), 'Improving compressed air system performance: a sourcebook for industry', DOE Industrial Technologies Program and Compressed Air Challenge, Washington DC.",
    "Williams A., Atkinson B., Garbesi K., Page E. and Rubinstein F. (2012), 'Lighting controls in commercial buildings', LEUKOS, Vol. 8, No. 3, pp. 161-180 [CHECK].",
]
for i, ref in enumerate(sorted(REFS, key=lambda s: s.lower()), 1):
    p = para(f"{i}.  {ref}", "Ref")
    p.paragraph_format.left_indent = Cm(0.8)
    p.paragraph_format.first_line_indent = Cm(-0.8)

out = ROOT / "Final_Report_Draft.docx"
doc.save(out)

# guard: no em or en dashes in the report body
import zipfile
xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf8")
bad = [ch for ch in ("—", "–") if ch in xml]
print("saved", out, "| figures", len(FIGLIST), "| tables", len(TABLIST), "| dash check", "FAIL " + str(bad) if bad else "ok")
