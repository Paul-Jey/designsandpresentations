"""Build Final_Report.docx in SSN format (Annexure I-A cover, Annexure II-B bonafide).

Prose lives in report/text/*.txt. Markup:
  # n Title            chapter            ## x.y TITLE    division       ### x.y.z Title   sub-division
  @fig key / @tab key / @eq key          place a registered figure, table or equation
  - item               bullet line
  <<fig:key>>          reference to a figure/table/equation number (resolved in a first pass)
  {name}               number filled from sim_v2/results.json (see N below)
"""
import json
import re
import zipfile
from pathlib import Path

import yaml
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

HERE = Path(__file__).parent
ROOT = HERE.parent
TXT = HERE / "text"
SIM = ROOT / "sim_v2"
FIG = SIM / "figures"
AS = HERE / "assets"
R = json.load(open(SIM / "results.json"))
C = yaml.safe_load(open(SIM / "assumptions.yaml"))
s5, a5, s8, s9, rd, s4 = R["S5"], R["S5"]["annual"], R["S8"], R["S9"], R["reference_day"], R["S4"]
f0 = lambda x: f"{x:,.0f}"
f1 = lambda x: f"{x:,.1f}"
f2 = lambda x: f"{x:,.2f}"

TITLE = "AI DATA ANALYTICS LAYER FOR SURVEILLANCE SYSTEMS USING EDGE AI FOR ENERGY MANAGEMENT SYSTEMS"
TEAM = [("PAUL JEY SANJITH J", "3122233001069"), ("OVIYAN P S", "3122233001067"), ("THIRSNA S", "3122233001309")]
DEPT = "Department of Electrical and Electronics Engineering"

# ------------------------------------------------------------------ numbers used in the prose
s6 = {c["name"]: c for c in R["S6"]["cases"]}
s7 = {r["T1_min"]: r for r in R["S7"]}
rows8 = {(r["machines"], r["reuse_cctv"]): r for r in s8["rows"]}
sv = s5["by_load_saving_kwh_day"]
N = dict(
    mean_pct=f1(s5["mean_pct"]), p5=f1(s5["p5_pct"]), p50=f1(s5["p50_pct"]), p95=f1(s5["p95_pct"]),
    pos_days=f1(s5["positive_days_pct"]), Eb_day=f0(s5["mean_E_base_kwh"]), Ec_day=f0(s5["mean_E_ctrl_kwh"]),
    save_day=f0(a5["e_save_day"]), kwh_yr=f0(a5["kwh"]), rs_energy=f0(a5["rs_energy"]), rs_demand=f0(a5["rs_demand"]),
    rs_total=f0(a5["rs_total"]), rs_lakh=f2(a5["rs_total"] / 1e5), co2=f1(a5["co2_t"]),
    ier_b=f1(100 * s5["ier_base_mean"]), ier_c=f1(100 * s5["ier_ctrl_mean"]),
    mc_md_b=f1(s5["md_base_mean"]), mc_md_c=f1(s5["md_ctrl_mean"]),
    nuis=f2(s5["nuisance_per_machine_shift"]), days_yr=str(C["meta"]["days_per_year"]),
    ref_Eb=f0(rd["E_base_kwh"]), ref_Ec=f0(rd["E_ctrl_kwh"]), ref_pct=f1(rd["saving_pct"]),
    s1_b=f1(R["S1"]["E_base_kwh"]), s1_c=f1(R["S1"]["E_ctrl_kwh"]), s1_pct=f1(R["S1"]["saving_pct"]),
    sv_cnc=f1(sv["CNC machines"]), sv_comp=f1(sv["Compressor"]), sv_conv=f1(sv["Conveyor"]),
    sv_light=f1(sv["Lighting"]), sv_fan=f1(sv["Ventilation fans"]),
    avg_b=f1(s4["avg_base_kw"]), avg_c=f1(s4["avg_ctrl_kw"]), peak_b=f1(s4["peak_base_kw"]), peak_c=f1(s4["peak_ctrl_kw"]),
    lf_b=f2(s4["lf_base"]), lf_c=f2(s4["lf_ctrl"]), md_b=f1(s4["md_base_kva"]), md_c=f1(s4["md_ctrl_kva"]),
    s6_idle_lo=f0(s6["Idle power ratio 0.25 / 0.55"]["low_input_rs"]), s6_idle_hi=f0(s6["Idle power ratio 0.25 / 0.55"]["high_input_rs"]),
    s6_ev_lo=f0(s6["Idle events ×0.5 / ×1.5"]["low_input_rs"]), s6_ev_hi=f0(s6["Idle events ×0.5 / ×1.5"]["high_input_rs"]),
    s6_sh3=f0(s6["Shifts per day 3 / 1"]["low_input_rs"]), s6_sh1=f0(s6["Shifts per day 3 / 1"]["high_input_rs"]),
    t1_1_s=f2(s7[1]["saving_pct"]), t1_1_f=f2(s7[1]["false_standby_per_machine_shift"]),
    t1_3_s=f2(s7[3]["saving_pct"]), t1_3_n=f2(s7[3]["nuisance_per_machine_shift"]), t1_3_f=f"{s7[3]['false_standby_per_machine_shift']:.3f}",
    t1_5_s=f2(s7[5]["saving_pct"]), t1_5_n=f2(s7[5]["nuisance_per_machine_shift"]),
    t1_10_n=f2(s7[10]["nuisance_per_machine_shift"]), t1_30_s=f2(s7[30]["saving_pct"]),
    rs_per_machine=f0(s8["rs_per_machine_yr"]), pb_1=f1(rows8[(1, True)]["payback_months"]),
    pb_4=f1(rows8[(4, True)]["payback_months"]), pb_10=f1(rows8[(10, True)]["payback_months"]),
    cost_full=f0(s8["full_shop_cost_rs"]), pb_full=f1(s8["full_shop_payback_months"]),
    cost_new=f0(s8["full_shop_cost_new_cams_rs"]), pb_new=f1(s8["full_shop_payback_new_cams_months"]),
    node_kwh=f0(s8["node_kwh_yr"]), node_share=f2(s8["node_share_of_saving_pct"]),
    off_b=f1(s9["E_base"]), off_c=f1(s9["E_ctrl"]), off_pct=f1(s9["saving_pct"]), off_kwh=f0(s9["annual_kwh"]),
    off_gross=f0(s9["gross_rs"]), off_net=f0(s9["net_rs"]), off_pb_n=f1(s9["payback_net_months"]),
    bill_lakh=f1(s5["mean_E_base_kwh"] * C["meta"]["days_per_year"] * C["tariff"]["energy_rs_per_kwh"] / 1e5),
)

# ------------------------------------------------------------------ registries
mp, ol, op, nd, sa = C["machine_power_kw"], C["other_loads_kw"], C["operations"], C["node"], C["site_actuation"]
FIGS = {
    "arch": (AS / "fig_architecture.png", "System architecture with implementation status", 13.5),
    "layout": (AS / "fig_shop_layout.png", "Reference machining shop with zones, machine regions of interest and cameras", 13.5),
    "sm": (AS / "fig_state_machine.png", "Machine state machine with transition conditions", 13.5),
    "bench": (AS / "prototype_bench.jpg", "Prototype bench set-up with the Jetson Nano edge node", 12.0),
    "live": (AS / "live_detection.jpg", "Live person detection on the Jetson Nano", 6.5),
    "dash": (AS / "dashboard.jpg", "Live energy dashboard in the office configuration", 6.5),
    "s1": (FIG / "S1_one_machine_shift.png", "Activity, operator presence and power of machine M1 over the first shift", 13.5),
    "s2": (FIG / "S2_cumulative_energy.png", "Cumulative energy of the shop on the reference day", 13.0),
    "s3": (FIG / "S3_breakdown_by_load.png", "Energy by load type on the reference day, baseline and controlled", 13.0),
    "s4": (FIG / "S4_load_duration.png", "Load-duration curve of the shop on the reference day", 13.0),
    "s5": (FIG / "S5_monte_carlo.png", "Distribution of the daily energy saving over 1,000 simulated days", 13.0),
    "s6": (FIG / "S6_tornado.png", "One-at-a-time sensitivity of the annual saving", 13.5),
    "s7": (FIG / "S7_timer_tradeoff.png", "Effect of the standby timer T1 on saving and on nuisance and false standbys", 13.5),
    "s8": (FIG / "S8_payback.png", "Simple payback against the number of machines covered by one node", 13.0),
    "s9": (FIG / "S9_office_vs_shop.png", "Saving of the same edge layer in an office room and in a machining shop", 12.0),
}
TABS = {
    "context": ("Key figures for the Indian manufacturing context", ["Quantity", "Value", "Source"], [
        ["Industry share of electricity consumption, 2023-24", "about 42 %", "CEA (2025a)"],
        ["Share of line energy used for machining (automotive line)", "14.8 %", "Gutowski et al (2005)"],
        ["Compressed air share of plant electricity", "about 10 %, over 30 % at some sites", "US DOE (2003)"],
        ["Tamil Nadu HT-I tariff from July 2025", "Rs 7.50/kWh and Rs 608/kVA/month", "TNERC (2025)"],
        ["Grid emission factor, 2024-25", "0.710 kg CO2/kWh", "CEA (2025b)"],
    ], [6.6, 4.2, 2.7], None),
    "objectives": ("Objectives of the project and their status", ["No.", "Objective", "Status"], [
        ["1", "Detect people in real time on a Jetson Nano edge node", "IMPLEMENTED"],
        ["2", "Convert detections into a stable presence signal", "IMPLEMENTED"],
        ["3", "Extend sensing to machine and zone regions with current-based activity", "MODELLED"],
        ["4", "Design a safe machine state machine with advisory and automatic modes", "MODELLED"],
        ["5", "Quantify energy, cost (energy and demand), demand, load factor and CO2 for a reference shop", "MODELLED"],
        ["6", "Test robustness, sensitivity and the choice of standby timer", "MODELLED"],
        ["7", "Define the integration and measurement path", "FUTURE"],
    ], [1.2, 9.3, 3.0], None),
    "gap": ("Summary of related work", ["Work", "Sensing", "Decision", "Limitation for this problem"], [
        ["Mouzon et al (2007)", "Schedule and time", "Switch off idle machines", "No knowledge of operator presence"],
        ["Squeo et al (2019)", "Time since last part", "Multi-level sleep states", "No knowledge of operator presence"],
        ["Tien et al (2021); Choi et al (2022)", "Camera", "Building HVAC and ventilation", "Applied to buildings only"],
        ["Kong et al (2022); Lin et al (2023)", "Occupancy sensors", "HVAC control", "Applied to buildings only"],
        ["Gebbe (2019); Suzuki et al (2017)", "Current (NILM)", "Monitoring only", "No operator context, no control"],
        ["This work", "Camera regions and machine current on an edge node", "Machine standby and shared loads, advisory or automatic", "Modelled; field validation planned"],
    ], [3.6, 3.4, 3.4, 3.1], None),
    "inputs": ("Sensing inputs for machine k and zone j", ["Signal", "Meaning", "Source", "Status"], [
        ["o_k(t)", "Operator present in the region of machine k", "Camera, per-region person count", "Detector IMPLEMENTED, regions MODELLED"],
        ["a_k(t)", "Machine k cutting", "CT clamp current above threshold", "MODELLED"],
        ["n_j(t)", "Persons in floor zone j", "Camera, per-zone person count", "Count IMPLEMENTED, zones MODELLED"],
    ], [1.8, 4.2, 4.0, 3.5], None),
    "states": ("Machine states, conditions, power and action", ["State", "Condition", "Power (kW)", "Action"], [
        ["PROCESSING", "a = 1", f1(mp["processing"]), "None"],
        ["IDLE-ATTENDED", "a = 0 and o = 1", f1(mp["idle"]), "None"],
        ["IDLE-UNATTENDED", f"a = 0 and o = 0 for more than T1 = {C['control']['T1_min']} min", f1(mp["standby"]) + " in standby", "Advisory alert, or automatic standby if whitelisted"],
        ["DEEP STANDBY", f"Unattended for more than T2 = {C['control']['T2_min']} min, whitelisted only", f2(mp["deep_standby"]), "Automatic deep standby; restart by operator with warm-up"],
    ], [3.3, 4.3, 2.2, 3.7], None),
    "loads": ("Control rules for shared loads", ["Load", "Baseline", "Rule with the edge node", "Mode"], [
        [f"Conveyor ({f1(ol['conveyor'])} kW)", "Runs all shift", "Stop when no line machine has cut for 2 min", "Automatic"],
        [f"Compressor ({f0(ol['compressor_full'])} kW)", "Runs all shift", "Stop and isolate when the whole shop has been idle for 5 min", "Automatic"],
        [f"High-bay lighting ({f1(ol['lighting_per_zone'])} kW per zone)", "On all shift", "Dim to 10 % when the zone has been empty for 2 min", "Automatic"],
        [f"Extraction fan ({f1(ol['fan_per_zone'])} kW per zone)", "On all shift", "Off when the zone is empty and no machine in it has cut for 5 min", "Automatic"],
    ], [3.6, 2.4, 5.8, 1.7], None),
    "hw": ("Edge node hardware", ["Item", "Specification", "Cost (Rs)"], [
        ["NVIDIA Jetson Nano Developer Kit", "4 GB, quad-core ARM A57, 128-core Maxwell GPU", "13,000"],
        ["Camera", "Logitech C920 USB (existing CCTV in a factory)", "1,300"],
        ["Storage", "64 GB microSD card", "700"],
        ["Power supply", "5 V, 4 A barrel jack", "500"],
        ["Cooling", "Heatsink with fan", "600"],
        ["Networking and miscellaneous", "Wi-Fi module, cables", "1,400"],
        ["Total", "", "17,500"],
    ], [4.6, 6.4, 2.5], None),
    "pipe": ("DeepStream pipeline elements", ["Stage", "Element", "Function"], [
        ["Capture", "v4l2src (rtspsrc for CCTV)", "Read camera frames"],
        ["Batching", "nvstreammux", "Form batches in GPU memory"],
        ["Inference", "nvinfer with ResNet10, TensorRT FP16", "Detect persons"],
        ["Regions", "nvdsanalytics (factory extension)", "Count persons per region of interest"],
        ["Metadata", "PyDS probe", "Read detections, apply filter"],
        ["Output", "live_state.json", "Publish state once a second"],
    ], [2.6, 5.4, 5.5], None),
    "power": ("Power assumptions for model v2", ["Load", "Value", "Basis"], [
        ["Machine, cutting", f"{f1(mp['processing'])} kW", "Assumed; below the 13 kW roughing example of Heidenhain (2011)"],
        ["Machine, idle", f"{f1(mp['idle'])} kW", "Assumed, 40 % of cutting; varied 25 to 55 %"],
        ["Machine, standby / deep standby", f"{f1(mp['standby'])} / {f2(mp['deep_standby'])} kW", "Assumed"],
        ["Warm-up after deep standby", f"{f1(mp['warmup_kw'])} kW for {mp['warmup_min']} min", "Assumed"],
        ["Compressor", f"{f0(ol['compressor_full'])} kW, unloaded {int(100 * ol['compressor_unload_frac'])} %, leak {int(100 * ol['compressor_leak_frac'])} %", "Leak within US DOE (2003) range"],
        ["Conveyor", f"{f1(ol['conveyor'])} kW", "Assumed"],
        ["Lighting per zone", f"{f1(ol['lighting_per_zone'])} kW", "Assumed, 24 LED fittings of 150 W"],
        ["Fan per zone", f"{f1(ol['fan_per_zone'])} kW", "Assumed"],
        ["Power factor", f2(ol["power_factor"]), "Assumed"],
    ], [4.0, 4.0, 5.5], None),
    "ops": ("Events in each machine shift", ["Event", "Model", "Operator"], [
        ["Machining cycle", f"Exponential, mean {op['cycle_proc_min']} min, with {op['load_unload_min']} min loading gaps", "Present"],
        ["Set-up at shift start", f"{op['setup_start_min']} min", "Present"],
        ["Tea breaks", f"{op['tea_min']} min at 2 h and 6 h into the shift", "Absent"],
        ["Meal break", f"{op['lunch_min']} min at 4 h into the shift", "Absent"],
        ["Material wait", f"Poisson, {op['material_wait_rate']} per shift; lognormal, median {op['material_wait_median_min']} min", f"Absent with probability {op['material_wait_p_absent']}"],
        ["Tool change", f"Poisson, {op['tool_change_rate']} per shift; mean {op['tool_change_min']} min", "Present"],
        ["Breakdown", f"Probability {op['breakdown_prob']} per shift; {op['breakdown_min'][0]} to {op['breakdown_min'][1]} min", f"Absent with probability {op['breakdown_p_absent']}"],
        ["Short absence", f"Poisson, {op['short_absence_rate']} per shift; mean {op['short_absence_min']} min", "Absent"],
        ["Left on overnight (baseline)", f"Probability {op['night_left_on_prob']} per machine", "Absent"],
    ], [3.4, 6.8, 3.3], None),
    "tariff": ("Tariff and emission inputs", ["Item", "Value", "Source"], [
        ["Energy charge c_E", f"Rs {C['tariff']['energy_rs_per_kwh']:.2f} per kWh", "TNERC (2025), HT-I"],
        ["Demand charge c_D", f"Rs {C['tariff']['demand_rs_per_kva_month']} per kVA per month", "TNERC (2025), HT-I"],
        ["Billing demand", "Higher of recorded MD and 90 % of CD", "TNERC (2025)"],
        ["Contract demand CD", f"{C['tariff']['contract_demand_kva']} kVA", "Assumed"],
        ["Emission factor EF", f"{C['carbon']['ef_kg_per_kwh']:.3f} kg CO2 per kWh", "CEA (2025b), 2024-25"],
        ["Working days", f"{C['meta']['days_per_year']} per year", "Assumed"],
    ], [4.0, 4.8, 4.7], None),
    "byload": ("Mean daily saving by load type over 1,000 days", ["Load", "Saving (kWh per day)"],
               [[k, f1(v)] for k, v in sv.items()] + [["Total", f0(a5["e_save_day"])]], [8.0, 5.5], None),
    "indices": ("Electrical indices on the reference day", ["Index", "Baseline", "Controlled"], [
        ["Average power (kW)", N["avg_b"], N["avg_c"]], ["Peak power (kW)", N["peak_b"], N["peak_c"]],
        ["Load factor", N["lf_b"], N["lf_c"]], ["Maximum demand, 15 min (kVA)", N["md_b"], N["md_c"]],
    ], [6.5, 3.5, 3.5], None),
    "headline": ("Headline results over 1,000 simulated days", ["Quantity", "Value"], [
        ["Mean shop energy, baseline to controlled", f"{N['Eb_day']} to {N['Ec_day']} kWh per day"],
        ["Mean saving (5th to 95th percentile)", f"{N['mean_pct']} % ({N['p5']} to {N['p95']} %)"],
        ["Days with a positive saving", f"{N['pos_days']} %"],
        ["Energy avoided", f"{N['kwh_yr']} kWh per year"],
        ["Cost saving: energy, demand, total", f"Rs {N['rs_energy']}, Rs {N['rs_demand']}, Rs {N['rs_total']} per year"],
        ["CO2 avoided", f"{N['co2']} t per year"],
        ["Idle-energy ratio", f"{N['ier_b']} % to {N['ier_c']} %"],
        ["Mean maximum demand", f"{N['mc_md_b']} to {N['mc_md_c']} kVA"],
        ["Nuisance standbys", f"{N['nuis']} per machine-shift"],
    ], [6.5, 7.0], None),
    "sens": ("Sensitivity of the annual saving (150 days per case)", ["Input (low / high)", "Saving at low input (Rs/yr)", "Saving at high input (Rs/yr)"],
             [[c["name"].replace("₹", "Rs ").replace("×", "x"), f0(c["low_input_rs"]), f0(c["high_input_rs"])] for c in reversed(R["S6"]["cases"])],
             [6.0, 3.75, 3.75], f"Reference case over the same 150 days: Rs {f0(R['S6']['reference_rs'])} per year."),
    "timer": ("Effect of the standby timer T1 (150 days per value)", ["T1 (min)", "Saving (%)", "Nuisance per machine-shift", "False standby per machine-shift"],
              [[r["T1_min"], f2(r["saving_pct"]), f2(r["nuisance_per_machine_shift"]), f"{r['false_standby_per_machine_shift']:.3f}"] for r in R["S7"]],
              [2.4, 2.9, 4.1, 4.1], None),
    "cost": ("Indicative cost of the installation for the reference shop", ["Item", "Quantity", "Cost (Rs)"], [
        ["Jetson Nano with power supply, storage and enclosure", "1", f0(nd["jetson_rs"] + nd["psu_sd_enclosure_rs"])],
        ["Relay or Modbus input and output module", "1", f0(nd["relay_io_modbus_rs"])],
        ["CT clamps", str(C["shop"]["n_machines"]), f0(C["shop"]["n_machines"] * nd["ct_per_machine_rs"])],
        ["CT interface (ADC or Modbus meter)", "1", f0(nd["ct_interface_rs"])],
        ["Installation sundries", "1", f0(nd["install_misc_rs"])],
        ["Lighting zone dimming interfaces", "4", f0(4 * sa["lighting_zone_rs"])],
        ["Fan contactors", "4", f0(4 * sa["fan_contactor_rs"])],
        ["Conveyor interlock and compressor isolation valve", "1", f0(sa["conveyor_compressor_rs"])],
        ["Wiring, integration and commissioning", "1", f0(sa["integration_rs"])],
        ["Total, with existing CCTV", "", f0(s8["full_shop_cost_rs"])],
    ], [8.2, 1.8, 3.5], "Indicative retail prices, October 2026."),
    "std": ("Standards and protocols relevant to deployment", ["Standard", "Purpose", "Role in this work"], [
        ["ISO 14955-1:2017", "Design method for energy-efficient machine tools", "Reference for machine energy states"],
        ["PROFIenergy (PROFINET)", "Standard pause and standby commands", "Automatic control of PROFINET machines"],
        ["OPC UA / umati", "Vendor-neutral machine data", "Machine state from the controller"],
        ["Modbus TCP", "Register access to meters, relays and drives", "CT meters and switching of shared loads"],
        ["MQTT 5.0", "Publish and subscribe telemetry", "Node to dashboard and plant systems"],
        ["ISO 50001:2018", "Energy management system", "Framework for the node in a plant"],
        ["ISO 50006:2014", "Baselines and performance indicators", "Idle-energy ratio as an indicator"],
        ["ISO 50015:2014, IPMVP", "Measurement and verification", "Proving the savings (Option B)"],
    ], [3.6, 5.0, 4.9], None),
    "sdg": ("Mapping to Sustainable Development Goals", ["Goal", "Contribution"], [
        ["SDG 7: Affordable and clean energy", "Reduces avoidable electricity use in factories"],
        ["SDG 9: Industry, innovation and infrastructure", "Adds edge AI to existing camera infrastructure in MSMEs"],
        ["SDG 12: Responsible consumption and production", "Lowers the energy used per part produced"],
        ["SDG 13: Climate action", f"Avoids about {N['co2']} t CO2 per year for one shop (modelled)"],
    ], [6.0, 7.5], None),
}
EQS = {
    "presence": "o_f : 0 → 1 after t_rise of presence;   1 → 0 after t_fall of absence",
    "activity": "a_f : 0 → 1 when I_k > I_th;   1 → 0 after 30 s with I_k < I_th",
    "mpower": "P_k(t) = P_state( s_k(t) )",
    "shop": "P_shop = Σ_k P_k + P_comp + P_conv + Σ_j ( P_light,j + P_fan,j )",
    "comp": "P_comp = P_full [ f + (1 - f) α_u ],  f = min(1, λ_leak + β N_proc)",
    "energy": "E = Σ_t P(t) Δt",
    "saved": "E_saved = E_base - E_ctrl",
    "md": "MD = max_b [ (1/n) Σ_(t in b) P(t) ] / PF",
    "bill": "C_month = E c_E + max( MD, 0.9 CD ) c_D",
    "lf": "LF = P_avg / P_peak",
    "ier": "IER = E_idle / E_total",
    "co2": "CO2 = E_saved × EF",
    "payback": "Payback = 12 C_inst / ( S_yr - E_node c_E )  months",
}

# ------------------------------------------------------------------ document and styles
doc = Document()
st = doc.styles
normal = st["Normal"]
normal.font.name = "Times New Roman"
normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.font.size = Pt(13)
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def fix_heading(name, size, align):
    h = st[name]
    rpr = h.element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(k)) is not None:
            del rf.attrib[qn(k)]
    for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(k), "Times New Roman")
    h.font.size = Pt(size); h.font.bold = True; h.font.italic = False
    h.font.color.rgb = RGBColor(0, 0, 0)
    pf = h.paragraph_format
    pf.alignment = align; pf.space_before = Pt(12); pf.space_after = Pt(10); pf.line_spacing = 1.5
    pf.keep_with_next = True


fix_heading("Heading 1", 14, WD_ALIGN_PARAGRAPH.CENTER)
fix_heading("Heading 2", 13, WD_ALIGN_PARAGRAPH.LEFT)
fix_heading("Heading 3", 13, WD_ALIGN_PARAGRAPH.LEFT)


def add_style(name, size=13, bold=False, italic=False, align=None, spacing=1.5):
    s = st.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    s.base_style = st["Normal"]
    s.font.name = "Times New Roman"; s.font.size = Pt(size); s.font.bold = bold; s.font.italic = italic
    if align is not None:
        s.paragraph_format.alignment = align
    s.paragraph_format.line_spacing = spacing
    return s


add_style("Chapter Label", 14, True, align=WD_ALIGN_PARAGRAPH.CENTER).paragraph_format.space_before = Mm(15)
add_style("Figure Caption", 12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0).paragraph_format.space_after = Pt(14)
tc = add_style("Table Caption", 12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0)
tc.paragraph_format.space_before = Pt(10); tc.paragraph_format.keep_with_next = True
add_style("Ref", 12, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0).paragraph_format.space_after = Pt(1)
add_style("Equation", 12, align=WD_ALIGN_PARAGRAPH.LEFT)
add_style("Front Heading", 14, True, align=WD_ALIGN_PARAGRAPH.CENTER).paragraph_format.space_after = Pt(18)
add_style("Table Text", 11, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0).paragraph_format.space_after = Pt(0)
add_style("Code", 8, align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0).paragraph_format.space_after = Pt(0)
st["Code"].font.name = "Courier New"
bl = add_style("Bullet", 13)
bl.paragraph_format.left_indent = Cm(1.6); bl.paragraph_format.first_line_indent = Cm(-0.6)
body = add_style("Body", 13)
body.paragraph_format.first_line_indent = Cm(2.0)

PB = {"next": False}


def page_break():
    PB["next"] = True


def _pb(p):
    if PB["next"]:
        p.paragraph_format.page_break_before = True
        PB["next"] = False
    return p


def para(text="", style="Body", bold=False, italic=False, size=None, align=None, after=None, spacing=None):
    p = _pb(doc.add_paragraph(style=style))
    if text:
        r = p.add_run(text); r.bold, r.italic = bold or style in ("Chapter Label", "Front Heading"), italic
        if size:
            r.font.size = Pt(size)
    if align is not None:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if spacing is not None:
        p.paragraph_format.line_spacing = spacing
    return p


def field(par, instr):
    r = par.add_run()
    for tag, attr in (("w:fldChar", "begin"), ("w:instrText", None), ("w:fldChar", "separate")):
        el = OxmlElement(tag)
        if attr:
            el.set(qn("w:fldCharType"), attr)
        else:
            el.set(qn("xml:space"), "preserve"); el.text = instr
        r._r.append(el)
    t = OxmlElement("w:t"); t.text = " "; r._r.append(t)
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end"); r._r.append(e)


def update_fields_on_open():
    s = doc.settings.element
    u = OxmlElement("w:updateFields"); u.set(qn("w:val"), "true"); s.append(u)


def set_margins(sec):
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin, sec.bottom_margin = Mm(35), Mm(35)
    sec.left_margin, sec.right_margin = Mm(40), Mm(35)
    sec.header_distance = Mm(20)


def page_numbering(sec, fmt, start=None, show=True):
    sp = sec._sectPr
    pg = sp.find(qn("w:pgNumType"))
    if pg is None:
        pg = OxmlElement("w:pgNumType"); sp.append(pg)
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    sec.header.is_linked_to_previous = False
    hp = sec.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if show:
        field(hp, "PAGE")
        for r in hp.runs:
            r.font.name = "Times New Roman"; r.font.size = Pt(12)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)


# ------------------------------------------------------------------ figure / table / equation numbering
NUM = {}


def prepass(files):
    for chap, path in files:
        cnt = {"fig": 0, "tab": 0, "eq": 0}
        for line in path.read_text().splitlines():
            m = re.match(r"@(fig|tab|eq) (\w+)", line.strip())
            if m:
                kind, key = m.groups()
                cnt[kind] += 1
                NUM[f"{kind}:{key}"] = f"{chap}.{cnt[kind]}"


def resolve(text):
    def rep(m):
        kind, key = m.group(1), m.group(2)
        n = NUM[f"{kind}:{key}"]
        return {"fig": f"Figure {n}", "tab": f"Table {n}", "eq": f"Equation ({n})"}[kind]
    text = re.sub(r"<<(fig|tab|eq):(\w+)>>", rep, text)
    return text.format(**N)


def figure(key):
    path, cap, w = FIGS[key]
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(6)
    p.add_run().add_picture(str(path), width=Cm(w))
    para(f"Figure {NUM['fig:' + key]} {cap}", "Figure Caption", bold=True)


def table(key):
    cap, header, rows, widths, note = TABS[key]
    para(f"Table {NUM['tab:' + key]} {cap}", "Table Caption", bold=True)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        c.paragraphs[0].style = st["Table Text"]
        r = c.paragraphs[0].add_run(str(h)); r.bold = True
        shade(c, "D9E2F3")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; cells[i].paragraphs[0].style = st["Table Text"]
            r = cells[i].paragraphs[0].add_run(str(v))
            if str(row[0]).startswith("Total"):
                r.bold = True
    if widths:
        t.autofit = False
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
            for row in t.rows:
                row.cells[i].width = Cm(w)
    keep_table_together(t)
    if note:
        para(note, "Table Text", italic=True, size=10)
    doc.add_paragraph(style="Table Text")



def keep_table_together(t):
    """Keep a table on one page: rows never split and each row stays with the next."""
    n = len(t.rows)
    for ri, row in enumerate(t.rows):
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        if ri < n - 1:
            for c in row.cells:
                for p in c.paragraphs:
                    p.paragraph_format.keep_with_next = True


def equation(key):
    p = doc.add_paragraph(style="Equation")
    p.paragraph_format.tab_stops.add_tab_stop(Cm(0.6))
    p.paragraph_format.tab_stops.add_tab_stop(Cm(13.5), alignment=2)
    p.add_run("\t" + EQS[key] + "\t" + f"({NUM['eq:' + key]})")


def render(path):
    lines = path.read_text().splitlines()
    buf = []

    def flush():
        if buf:
            para(resolve(" ".join(buf)), "Body")
            buf.clear()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush(); continue
        if line.startswith("# "):
            flush()
            n, title = line[2:].split(" ", 1)
            if n != "1":
                page_break()
            para(f"CHAPTER {n}", "Chapter Label")
            h = _pb(doc.add_heading(title.upper(), level=1))
            h.paragraph_format.space_after = Pt(30)
        elif line.startswith("### "):
            flush(); doc.add_heading(line[4:], level=3)
        elif line.startswith("## "):
            flush()
            num, title = line[3:].split(" ", 1)
            h = doc.add_heading(f"{num}\t{title}", level=2)
            h.paragraph_format.tab_stops.add_tab_stop(Cm(2.0))
        elif line.startswith("@fig "):
            flush(); figure(line.split()[1])
        elif line.startswith("@tab "):
            flush(); table(line.split()[1])
        elif line.startswith("@eq "):
            flush(); equation(line.split()[1])
        elif line.startswith("- "):
            flush(); para("•\t" + resolve(line[2:]), "Bullet").paragraph_format.tab_stops.add_tab_stop(Cm(1.6))
        else:
            buf.append(line)
    flush()


CHAPTERS = [(i, TXT / f"ch{i}.txt") for i in range(1, 9)]
prepass(CHAPTERS)

# ================================================================== TITLE PAGE (Annexure I-A)
sec = doc.sections[0]
set_margins(sec)
page_numbering(sec, "lowerRoman", start=1, show=True)
sec.different_first_page_header_footer = True


def tp(text, size, bold=True, italic=False, after=6, spacing=1.15, wide=False):
    p = para(text, "Normal", bold=bold, italic=italic, size=size, align=WD_ALIGN_PARAGRAPH.CENTER, after=after, spacing=spacing)
    if wide:
        p.paragraph_format.left_indent = Mm(-6); p.paragraph_format.right_indent = Mm(-6)
    return p


tp(TITLE, 18, after=18, spacing=1.5)
tp("PHASE I REPORT", 14, after=18)
tp("Submitted by", 14, italic=True, after=4)
for n_, r_ in TEAM:
    p = doc.add_paragraph(style="Normal"); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(f"{n_}   ({r_})"); r.bold = True; r.font.size = Pt(16)
tp("", 8, after=6)
tp("in partial fulfillment for the award of the degree of", 14, bold=True, italic=True, after=12)
tp("BACHELOR OF ENGINEERING", 16, after=0)
tp("IN", 14, after=0)
tp("ELECTRICAL AND ELECTRONICS ENGINEERING", 16, after=8, wide=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run().add_picture(str(AS / "ssn_logo.png"), width=Cm(3.2))
tp("DEPARTMENT OF", 16, after=0)
tp("ELECTRICAL AND ELECTRONICS ENGINEERING", 16, after=0, wide=True)
tp("SRI SIVASUBRAMANIYA NADAR", 16, after=0)
tp("COLLEGE OF ENGINEERING", 16, after=0)
tp("(An Autonomous Institution, Affiliated to Anna University)", 12, after=18)
tp("NOVEMBER 2026", 14, after=0)

# ================================================================== BONAFIDE (Annexure II-B)
page_break()
tp("Sri Sivasubramaniya Nadar College of Engineering", 16, after=0)
tp("(An Autonomous Institution, Affiliated to Anna University)", 12, after=18)
tp("BONAFIDE CERTIFICATE", 16, after=18)
p = _pb(doc.add_paragraph(style="Normal"))
p.paragraph_format.line_spacing = 2.0
p.paragraph_format.first_line_indent = Cm(1.27)


def _r(t, b=False):
    r = p.add_run(t); r.bold = b; r.font.size = Pt(14)


_r("Certified that this project titled “"); _r(TITLE, True); _r("” is the bonafide work of “")
for i, (n_, r_) in enumerate(TEAM):
    _r(n_.title(), True); _r(f" ({r_})" + (", " if i < 1 else (" and " if i == 1 else "")))
_r("”, who carried out the project work under my supervision.")
p = doc.add_paragraph(style="Normal")
p.paragraph_format.line_spacing = 2.0; p.paragraph_format.first_line_indent = Cm(1.27)
r = p.add_run("Certified further that to the best of my knowledge the work reported herein does not form part of any "
              "other thesis or dissertation on the basis of which a degree or award was conferred on an earlier "
              "occasion on this or any other candidate."); r.font.size = Pt(14)
p_gap = doc.add_paragraph(style="Table Text"); p_gap.paragraph_format.space_after = Pt(16)
sig = doc.add_table(rows=7, cols=2)
L = ["SIGNATURE", "Dr. V. RAJINI", "HEAD OF THE DEPARTMENT", "Professor and Head", DEPT, "SSN College of Engineering", "Kalavakkam - 603 110"]
Rr = ["SIGNATURE", "Dr. RAJESH PANDA", "SUPERVISOR", "Assistant Professor", DEPT, "SSN College of Engineering", "Kalavakkam - 603 110"]
for i in range(7):
    for j, txt in enumerate((L[i], Rr[i])):
        c = sig.rows[i].cells[j]; c.text = ""
        rr = c.paragraphs[0].add_run(txt); rr.font.size = Pt(12); rr.bold = i in (0, 1, 2)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
        c.width = Cm(7.0)
        c.paragraphs[0].paragraph_format.space_after = Pt(0)
        c.paragraphs[0].paragraph_format.line_spacing = 1.0
para("Submitted for project viva-voce examination held on ...............................", "Normal", size=12)
p = para("", "Normal", align=WD_ALIGN_PARAGRAPH.LEFT)
p.paragraph_format.space_before = Pt(18)
p.paragraph_format.tab_stops.add_tab_stop(Cm(8.0))
for txt in ("EXTERNAL EXAMINER", "\tINTERNAL EXAMINER"):
    rr = p.add_run(txt); rr.bold = True; rr.font.size = Pt(12)

# ================================================================== ABSTRACT (TNR 14, double spacing)
page_break()
para("ABSTRACT", "Front Heading")
for block in (TXT / "abstract.txt").read_text().strip().split("\n\n"):
    p = para(resolve(block.strip()), "Body", size=14, spacing=2.0)
    if block.startswith("Keywords"):
        p.paragraph_format.first_line_indent = Cm(0)

# ================================================================== ACKNOWLEDGEMENT
page_break()
para("ACKNOWLEDGEMENT", "Front Heading")
for block in (TXT / "ack.txt").read_text().strip().split("\n\n"):
    para(block.strip(), "Body", spacing=2.0)
for n_, _ in TEAM:
    p = para(n_, "Normal", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, after=0, spacing=1.0)
    p.paragraph_format.space_before = Pt(12)

# ================================================================== TOC / LOT / LOF (static tables, Annexure III layout)
PAGEMAP_FILE = HERE / "pagemap.json"
PAGEMAP = json.load(open(PAGEMAP_FILE)) if PAGEMAP_FILE.exists() else {}
APPENDICES = ["APPENDIX 1  MODEL ASSUMPTIONS", "APPENDIX 2  EDGE NODE PROBE AND FILTER", "APPENDIX 3  BENCH DEMONSTRATION"]
FRONT = ["ABSTRACT", "LIST OF TABLES", "LIST OF FIGURES", "LIST OF SYMBOLS AND ABBREVIATIONS"]


def toc_entries():
    """(kind, chapter_no, title, search_key) in document order."""
    out = [("front", "", h, "front:" + h) for h in FRONT]
    for n, path in CHAPTERS:
        for line in path.read_text().splitlines():
            if line.startswith("# "):
                title = line[2:].split(" ", 1)[1].upper()
                out.append(("chap", str(n), title, f"chap:{n}"))
            elif line.startswith("## "):
                out.append(("sec", "", line[3:], "head:" + line[3:]))
    for a in APPENDICES:
        out.append(("chap", "", a.replace("  ", " "), "head:" + a))
    out.append(("chap", "", "REFERENCES", "head:REFERENCES"))
    return out


def caption_entries(kind):
    reg = FIGS if kind == "fig" else TABS
    rows = []
    for k, num in NUM.items():
        kk, key = k.split(":")
        if kk == kind:
            cap = reg[key][1] if kind == "fig" else reg[key][0]
            label = ("Figure " if kind == "fig" else "Table ") + num
            rows.append((num, cap, f"{kind}:{label} {cap}"))
    if kind == "tab":
        rows.append(("A 3.1", "Parts for the bench demonstration", "tab:Table A 3.1 Parts for the bench demonstration"))
    return rows


def static_table(header, rows, widths, bold_rows=()):
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""
        c.paragraphs[0].style = st["Table Text"]
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(12)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]; p.style = st["Table Text"]
            p.paragraph_format.space_before = Pt(0); p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.5
            if i != 1:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(v); r.font.size = Pt(12); r.bold = ri in bold_rows
    for i, w in enumerate(widths):
        t.columns[i].width = Cm(w)
        for row in t.rows:
            row.cells[i].width = Cm(w)
    return t


page_break()
para("TABLE OF CONTENTS", "Front Heading")
rows, bold = [], []
for kind, chap, title, key in toc_entries():
    pg = PAGEMAP.get(key, "")
    if kind == "sec":
        num, rest = title.split(" ", 1)
        rows.append(["", f"      {num}   {rest}", pg])
    else:
        bold.append(len(rows)); rows.append([chap, title, pg])
static_table(["CHAPTER NO.", "TITLE", "PAGE NO."], rows, [2.8, 8.7, 2.0], bold)

page_break()
para("LIST OF TABLES", "Front Heading")
static_table(["TABLE NO.", "TITLE", "PAGE NO."],
             [[n, cap, PAGEMAP.get(k, "")] for n, cap, k in caption_entries("tab")], [2.4, 9.1, 2.0])
page_break()
para("LIST OF FIGURES", "Front Heading")
static_table(["FIGURE NO.", "TITLE", "PAGE NO."],
             [[n, cap, PAGEMAP.get(k, "")] for n, cap, k in caption_entries("fig")], [2.4, 9.1, 2.0])
json.dump({"toc": toc_entries(), "tab": caption_entries("tab"), "fig": caption_entries("fig")},
          open(HERE / "toc_entries.json", "w"), indent=0)

# ================================================================== SYMBOLS AND ABBREVIATIONS
page_break()
para("LIST OF SYMBOLS AND ABBREVIATIONS", "Front Heading")
SYM = [("a_k(t)", "Activity of machine k (1 when cutting), from CT current"),
       ("o_k(t)", "Operator presence in the region of machine k, after filtering"),
       ("n_j(t)", "Person count in floor zone j"), ("P(t)", "Active power, kW"), ("E", "Energy, kWh"),
       ("Δt", "Simulation time step, s"), ("T1, T2", "Standby and deep standby timers, min"),
       ("MD", "Maximum demand over a 15-minute interval, kVA"), ("CD", "Contract demand, kVA"),
       ("PF", "Power factor"), ("LF", "Load factor"), ("IER", "Idle-energy ratio"),
       ("EF", "Grid emission factor, kg CO2 per kWh"), ("c_E, c_D", "Energy charge (Rs/kWh) and demand charge (Rs/kVA/month)"),
       ("α_u, λ_leak, β", "Compressor unloaded fraction, leak demand and demand per cutting machine")]
ABB = [("BEE", "Bureau of Energy Efficiency"), ("CEA", "Central Electricity Authority"), ("CNC", "Computer Numerical Control"),
       ("CT", "Current Transformer"), ("DPDP", "Digital Personal Data Protection"), ("FP16", "16-bit floating point"),
       ("HT", "High Tension"), ("HVAC", "Heating, Ventilation and Air Conditioning"),
       ("IPMVP", "International Performance Measurement and Verification Protocol"), ("MQTT", "Message Queuing Telemetry Transport"),
       ("MSME", "Micro, Small and Medium Enterprises"), ("NILM", "Non-Intrusive Load Monitoring"),
       ("OPC UA", "Open Platform Communications Unified Architecture"), ("PAT", "Perform, Achieve and Trade"),
       ("PyDS", "Python bindings for DeepStream"), ("ROI", "Region of Interest"),
       ("TNERC", "Tamil Nadu Electricity Regulatory Commission"), ("VMC", "Vertical Machining Centre")]
static_table(["SYMBOL", "DESCRIPTION"], [[a_, b_] for a_, b_ in SYM], [3.5, 10.0])
para("", "Table Text")
static_table(["ABBREVIATION", "EXPANSION"], [[a_, b_] for a_, b_ in ABB], [3.5, 10.0])

# ================================================================== CHAPTERS
sec2 = doc.add_section(WD_SECTION.NEW_PAGE)
set_margins(sec2)
page_numbering(sec2, "decimal", start=1, show=True)
sec2.different_first_page_header_footer = False
for _, path in CHAPTERS:
    render(path)

# ================================================================== APPENDICES
page_break()
_pb(doc.add_heading("APPENDIX 1  MODEL ASSUMPTIONS", level=1))
para("The complete input file of model v2 is reproduced below. Every value used in Chapters 5 and 6 is read from this file.", "Body")
for line in (SIM / "assumptions.yaml").read_text().splitlines():
    if line.strip().startswith("office_v1"):
        break
    if not line.strip() or line.strip().startswith("#"):
        continue
    para(line.split("  #")[0].rstrip() if "#" in line else line, "Code")
page_break()
_pb(doc.add_heading("APPENDIX 2  EDGE NODE PROBE AND FILTER", level=1))
para("The listing below shows the PyDS probe function attached to the DeepStream pipeline, the per-region counting and the asymmetric presence filter of Section 3.5.", "Body")
for line in (TXT / "appendix3_probe.py").read_text().splitlines():
    para(line, "Code")
page_break()
_pb(doc.add_heading("APPENDIX 3  BENCH DEMONSTRATION", level=1))
para("The bench demonstration shows the complete chain from operator absence to switching on the existing edge node, using a small fan as the machine. The parts are listed in Table A 3.1.", "Body")
para("Table A 3.1 Parts for the bench demonstration", "Table Caption", bold=True)
tA = doc.add_table(rows=1, cols=3); tA.style = "Table Grid"
for c, h in zip(tA.rows[0].cells, ("Part", "Quantity", "Approximate cost (Rs)")):
    c.text = ""; c.paragraphs[0].style = st["Table Text"]; c.paragraphs[0].add_run(h).bold = True; shade(c, "D9E2F3")
for row in [("Jetson Nano and C920 camera (existing)", "1", "0"), ("12 V DC fan with 12 V, 2 A adapter", "1", "450"),
            ("INA219 current and power sensor", "1", "250"), ("Opto-isolated 5 V relay module", "1", "120"),
            ("Jumper wires, terminal block and board", "1 set", "200"), ("Total", "", "1,020")]:
    cells = tA.add_row().cells
    for c, v in zip(cells, row):
        c.text = ""; c.paragraphs[0].style = st["Table Text"]; rr = c.paragraphs[0].add_run(v); rr.bold = row[0] == "Total"
keep_table_together(tA)
doc.add_paragraph(style="Table Text")
for txt in [
    "The software changes are small. The probe counts persons inside a region drawn around the desk, the INA219 is read twice a second over I2C and the fan is taken as running when its current exceeds about 30 % of its running value. The state machine of Chapter 3 runs with the standby timer shortened to 30 s, and a GPIO pin drives the relay. The dashboard gains a machine card with the state, the countdown and live counters of energy and rupees avoided.",
    "The demonstration runs in five steps. With the operator seated and the fan running, the state is PROCESSING; with the fan stopped and the operator present, it is IDLE-ATTENDED and nothing happens. When the operator leaves, the countdown runs, the relay opens and the avoided energy counter starts to rise. The fan restarts only when the returning operator presses the resume button. In advisory mode the same sequence produces only an alert.",
]:
    para(txt, "Body")

# ================================================================== REFERENCES
page_break()
_pb(doc.add_heading("REFERENCES", level=1))
REFS = [
    "Central Electricity Authority (2025a), 'All India Electricity Statistics: General Review 2025', Ministry of Power, Government of India, New Delhi.",
    "Central Electricity Authority (2025b), 'CO2 Baseline Database for the Indian Power Sector, User Guide Version 21.0', Ministry of Power, Government of India, New Delhi.",
    "Choi H., Lee J., Yi Y., Na H., Kang K. and Kim T. (2022), 'Deep vision-based occupancy counting: experimental performance evaluation and implementation of ventilation control', Building and Environment, Vol. 223, Paper No.109496.",
    "Denkena B., Abele E., Brecher C., Dittrich M.-A., Kara S. and Mori M. (2020), 'Energy efficient machine tools', CIRP Annals - Manufacturing Technology, Vol. 69, No.2, DOI 10.1016/j.cirp.2020.05.008.",
    "Gebbe C. (2019), 'Nonintrusive load monitoring for machines used in manufacturing', arXiv preprint arXiv:1912.01500, Fraunhofer IGCV, Augsburg.",
    "Government of India (2023), 'The Digital Personal Data Protection Act, 2023', Act No. 22 of 2023, Ministry of Law and Justice, New Delhi.",
    "Gutowski T., Dahmus J. and Thiriez A. (2006), 'Electrical energy requirements for manufacturing processes', Proc. 13th CIRP International Conference on Life Cycle Engineering, Leuven, pp.623-628.",
    "Gutowski T., Murphy C., Allen D., Bauer D., Bras B., Piwonka T., Sheng P., Sutherland J., Thurston D. and Wolff E. (2005), 'Environmentally benign manufacturing: observations from Japan, Europe and the United States', Journal of Cleaner Production, Vol. 13, No.1, pp.1-17.",
    "HEIDENHAIN (2011), 'Aspects of energy efficiency in machine tools', Technical Information, Dr. Johannes Heidenhain GmbH, Traunreut.",
    "ISO (2014a), 'ISO 50006:2014 Energy management systems: Measuring energy performance using energy baselines and energy performance indicators', International Organization for Standardization, Geneva.",
    "ISO (2014b), 'ISO 50015:2014 Energy management systems: Measurement and verification of energy performance of organizations', International Organization for Standardization, Geneva.",
    "ISO (2017), 'ISO 14955-1:2017 Machine tools: Environmental evaluation of machine tools, Part 1: Design methodology for energy-efficient machine tools', International Organization for Standardization, Geneva.",
    "ISO (2018), 'ISO 50001:2018 Energy management systems: Requirements with guidance for use', International Organization for Standardization, Geneva.",
    "Kara S. and Li W. (2011), 'Unit process energy consumption models for material removal processes', CIRP Annals - Manufacturing Technology, Vol. 60, No.1, pp.37-40.",
    "Kong M., Dong B., Zhang R. and O'Neill Z. (2022), 'HVAC energy savings, thermal comfort and air quality for occupant-centric control through a side-by-side experimental study', Applied Energy, Vol. 306, Paper No.117987.",
    "Li W., Zein A., Kara S. and Herrmann C. (2011), 'An investigation into fixed energy consumption of machine tools', Proc. 18th CIRP International Conference on Life Cycle Engineering, Braunschweig, pp.268-273.",
    "Lin G., Casillas A., Sheng M. and Granderson J. (2023), 'Performance evaluation of an occupancy-based HVAC control system in an office building', Energies, Vol. 16, No.20, Paper No.7088.",
    "Mori M., Fujishima M., Inamasu Y. and Oda Y. (2011), 'A study on energy efficiency improvement for machine tools', CIRP Annals - Manufacturing Technology, Vol. 60, No.1, pp.145-148.",
    "Mouzon G., Yildirim M.B. and Twomey J. (2007), 'Operational methods for minimization of energy consumption of manufacturing equipment', International Journal of Production Research, Vol. 45, No.18-19, pp.4247-4271.",
    "NVIDIA Corporation (2021), 'DeepStream SDK 6.0.1 Developer Guide', NVIDIA, Santa Clara.",
    "OASIS (2019), 'MQTT Version 5.0', OASIS Standard, 7 March 2019.",
    "PROFIBUS and PROFINET International (2024), 'PROFIenergy: energy management for PROFINET devices', Technology description, PI, Karlsruhe.",
    "Squeo M., Frigerio N. and Matta A. (2019), 'Multiple sleeping states for energy saving in CNC machining centers', Procedia CIRP, Vol. 80, pp.144-149.",
    "Suzuki R., Kohmoto S. and Ogatsu T. (2017), 'Non-intrusive condition monitoring for manufacturing systems', Proc. 25th European Signal Processing Conference (EUSIPCO), Kos.",
    "Tamil Nadu Electricity Regulatory Commission (2025), 'Tariff Order No.6 of 2025', TNERC, Chennai, 30 June 2025.",
    "Tien P.W., Wei S., Calautit J.K., Darkwa J. and Wood C. (2021), 'A computer vision-based occupancy and equipment usage detection approach for reducing building energy demand', Energies, Vol. 14, No.1, Paper No.156.",
    "U.S. Department of Energy (2003), 'Improving compressed air system performance: a sourcebook for industry', Industrial Technologies Program and Compressed Air Challenge, Washington DC.",
    "Williams A., Atkinson B., Garbesi K., Page E. and Rubinstein F. (2012), 'Lighting controls in commercial buildings', LEUKOS, Vol. 8, No.3, pp.161-180.",
    "Zhang Y., Calautit J.K., Tien P.W., Wu Y. and Wei S. (2024), 'Deep learning models for vision-based occupancy detection in high occupancy buildings', Journal of Building Engineering, Vol. 98, Paper No.111355.",
]
for i, ref in enumerate(sorted(REFS, key=str.lower), 1):
    p = para(f"{i}.\t{ref}", "Ref")
    p.paragraph_format.left_indent = Cm(0.9); p.paragraph_format.first_line_indent = Cm(-0.9)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(0.9))

out = ROOT / "Final_Report.docx"
doc.save(out)

xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf8")
bad = [c for c in ("—", "–", "[TEAM", "[CHECK", "{", "<<") if c in re.sub(r"<[^>]+>", "", xml)]
print("saved", out.name, "| figures", sum(k.startswith("fig") for k in NUM), "| tables", sum(k.startswith("tab") for k in NUM),
      "| equations", sum(k.startswith("eq") for k in NUM), "| leftover check", bad or "clean")
