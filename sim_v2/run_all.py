"""Run S1-S9 for model v2, write figures (300 dpi PNG) and results.json.

Usage: python3 run_all.py            (full run, about 3-5 min)
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import model as m

HERE = Path(__file__).parent
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)

# ---- style (Review 3 look: SSN blue titles, white background, recessive grid)
BLUE = "#2F4F8F"
BASE = "#B03A3A"      # baseline (red, dashed) as in Review 3
CTRL = "#2E7D32"      # controlled (green) as in Review 3
INK = "#222222"
MUTED = "#6B7280"
CAT = ["#2F4F8F", "#2A9D8F", "#C9852B", "#7B5EA7", "#B5485A"]  # validated categorical order
plt.rcParams.update({
    "font.family": ["Liberation Sans", "DejaVu Sans"], "font.size": 10, "axes.edgecolor": "#9AA3AF",
    "axes.grid": True, "grid.color": "#E5E7EB", "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": "white",
    "axes.facecolor": "white", "axes.titleweight": "bold", "axes.titlecolor": BLUE,
    "axes.titlesize": 12, "axes.titlelocation": "left", "legend.frameon": False,
    "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
})


def footnote(fig, text):
    fig.text(0.99, -0.035, f"MODELLED · model v2 · {text}", ha="right", va="bottom",
             fontsize=7, color=MUTED, style="italic")


def save(fig, name):
    fig.savefig(FIG / name, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def hours_axis(ax, dt, T, lo=0, hi=24, step=2):
    ax.set_xlim(lo, hi)
    ax.set_xticks(range(lo, hi + 1, step))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(lo, hi + 1, step)])


cfg = m.load_cfg()
R = {}

# =============================================================== reference day
ref = m.simulate(cfg, 1, keep_series=True)
dt = ref["dt"]
T = ref["Pb"].shape[1]
t_h = np.arange(T) * dt / 3600
Eb, Ec = float(ref["E_base"][0]), float(ref["E_ctrl"][0])
R["reference_day"] = dict(
    E_base_kwh=Eb, E_ctrl_kwh=Ec, saving_kwh=Eb - Ec, saving_pct=100 * (Eb - Ec) / Eb,
    by_load_base={k: float(v[0]) for k, v in ref["E_b"].items()},
    by_load_ctrl={k: float(v[0]) for k, v in ref["E_c"].items()},
    md_base_kva=float(ref["md_base"][0]), md_ctrl_kva=float(ref["md_ctrl"][0]),
    peak_base_kw=float(ref["peak_base"][0]), peak_ctrl_kw=float(ref["peak_ctrl"][0]),
    avg_base_kw=float(ref["avg_base"][0]), avg_ctrl_kw=float(ref["avg_ctrl"][0]),
    ier_base=float(ref["ier_base"][0]), ier_ctrl=float(ref["ier_ctrl"][0]),
    standby_events=int(ref["n_standby"][0]), nuisance_events=int(ref["n_nuisance"][0]),
    false_standby_events=int(ref["n_false"][0]), warmup_kwh=float(ref["warm_kwh"][0]),
)

# =============================================================== S1 one machine, one shift
k = 0  # whitelisted general-purpose machine
s0, s1 = 6, 14
sl = slice(int(s0 * 3600 / dt), int(s1 * 3600 / dt))
th = t_h[sl]
fig, axs = plt.subplots(3, 1, figsize=(9, 6.2), sharex=True,
                        gridspec_kw=dict(height_ratios=[1, 1, 2.2], hspace=0.12))
axs[0].step(th, ref["A"][0, k, sl], where="post", color=INK, lw=1.2)
axs[0].set_ylabel("Machine\nactive a(t)")
axs[0].set_yticks([0, 1]); axs[0].set_yticklabels(["idle", "cutting"])
axs[1].step(th, ref["O"][0, k, sl], where="post", color=MUTED, lw=1.0, label="true")
axs[1].step(th, ref["Of"][0, k, sl], where="post", color=BLUE, lw=1.6, label="camera (filtered)")
axs[1].set_ylabel("Operator\npresent o(t)")
axs[1].set_yticks([0, 1]); axs[1].set_yticklabels(["absent", "present"])
axs[1].legend(loc="lower right", ncol=2, fontsize=8)
axs[2].step(th, ref["Pm_base"][0, k, sl], where="post", color=BASE, ls="--", lw=1.6, label="Baseline (machine left on)")
axs[2].step(th, ref["Pm_ctrl"][0, k, sl], where="post", color=CTRL, lw=1.8, label="Edge-AI controlled")
axs[2].set_ylabel("P(t) (kW)")
axs[2].set_ylim(0, 8.5)
axs[2].legend(loc="upper right", ncol=2, fontsize=8)
for y, lab in [(7.5, "PROCESSING 7.5"), (3.0, "IDLE 3.0"), (1.2, "STANDBY 1.2")]:
    axs[2].axhline(y, color="#D1D5DB", lw=0.8, zorder=0)
    axs[2].text(14.02, y, lab, fontsize=7, color=MUTED, va="center")
hours_axis(axs[2], dt, T, 6, 14, 1)
axs[2].set_xlabel("Time of day (h)")
axs[0].set_title("S1 · One CNC machine, first shift: activity and operator presence drive power")
e_b1 = ref["Pm_base"][0, k, sl].sum() * dt / 3600
e_c1 = ref["Pm_ctrl"][0, k, sl].sum() * dt / 3600
R["S1"] = dict(machine=k, shift="06:00-14:00", E_base_kwh=float(e_b1), E_ctrl_kwh=float(e_c1),
               saving_pct=float(100 * (e_b1 - e_c1) / e_b1))
footnote(fig, f"machine M{k + 1} (AUTO whitelist) · reference day seed {cfg['meta']['seed']}")
save(fig, "S1_one_machine_shift.png")

# =============================================================== S2 cumulative energy
cb = np.cumsum(ref["Pb"][0]) * dt / 3600
cc = np.cumsum(ref["Pc"][0]) * dt / 3600
fig, ax = plt.subplots(figsize=(8.5, 4.8))
ax.plot(t_h, cb, color=BASE, ls="--", lw=2, label="Baseline  E_base(t)")
ax.plot(t_h, cc, color=CTRL, lw=2, label="Edge-AI controlled  E_ctrl(t)")
ax.fill_between(t_h, cc, cb, color=CTRL, alpha=0.08, lw=0)
ax.annotate(f"{Eb:,.0f} kWh", (24, cb[-1]), xytext=(6, 4), textcoords="offset points", color=BASE, fontweight="bold")
ax.annotate(f"{Ec:,.0f} kWh", (24, cc[-1]), xytext=(6, -12), textcoords="offset points", color=CTRL, fontweight="bold")
ax.text(16.5, (cb[-1] + cc[-1]) / 2 - 250,
        f"ΔE = {Eb - Ec:,.0f} kWh/day\n({100 * (Eb - Ec) / Eb:.1f} % reduction)", fontsize=10, color=INK)
hours_axis(ax, dt, T, 0, 24, 2)
ax.set_xlabel("Time of day (h)"); ax.set_ylabel("Cumulative energy  E(t) = Σ P·Δt  (kWh)")
ax.set_title("S2 · Whole shop cumulative energy, reference day")
ax.legend(loc="upper left")
footnote(fig, "10 CNC + compressor + conveyor + lighting + fans · 2 shifts")
save(fig, "S2_cumulative_energy.png")

# =============================================================== S3 breakdown by load
fig, ax = plt.subplots(figsize=(8.5, 4.8))
labels = ["Baseline", "Edge-AI controlled"]
bottoms = np.zeros(2)
for i, L in enumerate(m.LOADS):
    vals = np.array([R["reference_day"]["by_load_base"][L], R["reference_day"]["by_load_ctrl"][L]])
    ax.barh(labels, vals, left=bottoms, color=CAT[i], edgecolor="white", linewidth=2, height=0.55, label=L)
    for j in range(2):
        if vals[j] > 90:
            ax.text(bottoms[j] + vals[j] / 2, j, f"{vals[j]:,.0f}", ha="center", va="center",
                    color="white", fontsize=8, fontweight="bold")
    bottoms += vals
for j in range(2):
    ax.text(bottoms[j] + 15, j, f"{bottoms[j]:,.0f} kWh", va="center", color=INK, fontweight="bold")
ax.set_xlabel("Energy per day (kWh)")
ax.set_xlim(0, bottoms.max() * 1.15)
ax.invert_yaxis()
ax.grid(axis="y", visible=False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=5, fontsize=8)
ax.set_title("S3 · Energy by load type, reference day")
footnote(fig, "segment labels in kWh/day")
save(fig, "S3_breakdown_by_load.png")
R["S3"] = {L: dict(base=R["reference_day"]["by_load_base"][L], ctrl=R["reference_day"]["by_load_ctrl"][L],
                   saving_pct=100 * (1 - R["reference_day"]["by_load_ctrl"][L] / R["reference_day"]["by_load_base"][L]))
           for L in m.LOADS}

# =============================================================== S4 load-duration + LF + MD
pb = np.sort(ref["Pb"][0])[::-1]
pc = np.sort(ref["Pc"][0])[::-1]
x = np.linspace(0, 100, len(pb))
lf_b = pb.mean() / pb.max()
lf_c = pc.mean() / pc.max()
fig, ax = plt.subplots(figsize=(8.5, 4.8))
ax.plot(x, pb, color=BASE, ls="--", lw=2, label=f"Baseline  (LF {lf_b:.2f}, MD {ref['md_base'][0]:.0f} kVA)")
ax.plot(x, pc, color=CTRL, lw=2, label=f"Edge-AI controlled  (LF {lf_c:.2f}, MD {ref['md_ctrl'][0]:.0f} kVA)")
ax.axhline(pb.mean(), color=BASE, lw=0.8, ls=":")
ax.axhline(pc.mean(), color=CTRL, lw=0.8, ls=":")
ax.text(101, pb.mean(), f"P_avg {pb.mean():.0f} kW", color=BASE, fontsize=8, va="bottom")
ax.text(101, pc.mean(), f"P_avg {pc.mean():.0f} kW", color=CTRL, fontsize=8, va="top")
ax.set_xlim(0, 100); ax.set_ylim(0, None)
ax.set_xlabel("Percentage of the day (%)"); ax.set_ylabel("Shop power (kW)")
ax.set_title("S4 · Load-duration curve: energy falls, peak and maximum demand barely move")
ax.legend(loc="upper right")
footnote(fig, "24 h reference day · LF = P_avg / P_peak · MD = max 15-min kVA at PF 0.90")
save(fig, "S4_load_duration.png")
R["S4"] = dict(lf_base=float(lf_b), lf_ctrl=float(lf_c), peak_base_kw=float(pb.max()), peak_ctrl_kw=float(pc.max()),
               avg_base_kw=float(pb.mean()), avg_ctrl_kw=float(pc.mean()),
               md_base_kva=float(ref["md_base"][0]), md_ctrl_kva=float(ref["md_ctrl"][0]))

# =============================================================== S5 Monte-Carlo
N = cfg["meta"]["mc_days"]
mc = m.simulate_batched(cfg, N)
sav = 100 * (1 - mc["E_ctrl"] / mc["E_base"])
p5, p50, p95 = np.percentile(sav, [5, 50, 95])
ann = m.annual(cfg, mc)
R["S5"] = dict(days=N, mean_pct=float(sav.mean()), p5_pct=float(p5), p50_pct=float(p50), p95_pct=float(p95),
               positive_days_pct=float(100 * (sav > 0).mean()),
               mean_E_base_kwh=float(mc["E_base"].mean()), mean_E_ctrl_kwh=float(mc["E_ctrl"].mean()),
               annual=dict((kk, float(v)) for kk, v in ann.items()),
               ier_base_mean=float(mc["ier_base"].mean()), ier_ctrl_mean=float(mc["ier_ctrl"].mean()),
               md_base_mean=float(mc["md_base"].mean()), md_ctrl_mean=float(mc["md_ctrl"].mean()),
               lf_base_mean=float((mc["avg_base"] / mc["peak_base"]).mean()),
               lf_ctrl_mean=float((mc["avg_ctrl"] / mc["peak_ctrl"]).mean()),
               by_load_saving_kwh_day={L: float((mc["E_b"][L] - mc["E_c"][L]).mean()) for L in m.LOADS},
               nuisance_per_machine_shift=float(mc["n_nuisance"].mean() / mc["machine_shifts"]),
               false_standby_per_machine_shift=float(mc["n_false"].mean() / mc["machine_shifts"]))
fig, ax = plt.subplots(figsize=(8.5, 4.8))
ax.hist(sav, bins=30, color="#3D85A6", edgecolor="white", linewidth=1)
for v, lab, c, ls in [(p5, f"P5 {p5:.1f} %", MUTED, "--"), (sav.mean(), f"mean {sav.mean():.1f} %", BLUE, "--"),
                      (p95, f"P95 {p95:.1f} %", MUTED, "--"), (R["reference_day"]["saving_pct"],
                      f"reference day {R['reference_day']['saving_pct']:.1f} %", BASE, "-")]:
    ax.axvline(v, color=c, ls=ls, lw=1.6)
    ax.text(v, ax.get_ylim()[1] * 0.97, " " + lab, color=c, fontsize=8, va="top", rotation=90, ha="right")
ax.set_xlabel("Daily energy saving (%)"); ax.set_ylabel("Number of simulated days")
ax.set_title(f"S5 · Monte-Carlo: {N:,} stochastic days")
footnote(fig, f"random waits, tool changes, breakdowns, absences, occlusion · seed {cfg['meta']['seed']}")
save(fig, "S5_monte_carlo.png")

# =============================================================== S6 tornado (annual ₹, energy + demand)
NS = 150


def annual_rs(c, seed=7):
    r = m.simulate_batched(c, NS, seed=seed)
    return m.annual(c, r)["rs_total"]


base_rs = annual_rs(cfg)
op = cfg["operations"]
cases = [
    ("Idle events ×0.5 / ×1.5", dict(operations__material_wait_rate=op["material_wait_rate"] * 0.5,
                                     operations__breakdown_prob=op["breakdown_prob"] * 0.5,
                                     operations__night_left_on_prob=op["night_left_on_prob"] * 0.5),
                                dict(operations__material_wait_rate=op["material_wait_rate"] * 1.5,
                                     operations__breakdown_prob=op["breakdown_prob"] * 1.5,
                                     operations__night_left_on_prob=min(1, op["night_left_on_prob"] * 1.5))),
    ("Idle power ratio 0.25 / 0.55", dict(machine_power_kw__idle=7.5 * 0.25), dict(machine_power_kw__idle=7.5 * 0.55)),
    ("Tariff ₹6.50 / ₹8.50 per kWh", dict(tariff__energy_rs_per_kwh=6.5), dict(tariff__energy_rs_per_kwh=8.5)),
    ("Shifts per day 3 / 1", dict(shop__shifts=[[6, 14], [14, 22], [22, 30]]), dict(shop__shifts=[[6, 14]])),
    ("Standby timer T1 15 / 2 min", dict(control__T1_min=15), dict(control__T1_min=2)),
    ("Advisory compliance 0.3 / 0.9", dict(control__advisory_compliance=0.3), dict(control__advisory_compliance=0.9)),
]
tor = []
for name, lo, hi in cases:
    a = annual_rs(m.with_overrides(cfg, **lo))
    b = annual_rs(m.with_overrides(cfg, **hi))
    tor.append((name, a, b))
    print("S6", name, round(a), round(b))
tor.sort(key=lambda r: abs(r[2] - r[1]))
fig, ax = plt.subplots(figsize=(8.5, 4.8))
for i, (name, a, b) in enumerate(tor):
    lo_, hi_ = min(a, b), max(a, b)
    ax.barh(i, lo_ - base_rs, left=base_rs, color="#C26A6A", height=0.55, edgecolor="white")
    ax.barh(i, hi_ - base_rs, left=base_rs, color="#5A9A5E", height=0.55, edgecolor="white")
    ax.text(lo_, i, f"₹{lo_ / 1e5:.2f} L ", ha="right", va="center", fontsize=8)
    ax.text(hi_, i, f" ₹{hi_ / 1e5:.2f} L", ha="left", va="center", fontsize=8)
ax.axvline(base_rs, color=INK, lw=1)
ax.set_yticks(range(len(tor))); ax.set_yticklabels([r[0] for r in tor])
ax.set_xlabel("Annual saving, energy + demand (₹ lakh/yr)")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f"{v / 1e5:.1f}"))
ax.grid(axis="y", visible=False)
lo_all = min(min(a, b) for _, a, b in tor); hi_all = max(max(a, b) for _, a, b in tor)
ax.set_xlim(lo_all - 0.25 * (hi_all - lo_all), hi_all + 0.25 * (hi_all - lo_all))
ax.text(base_rs, len(tor) - 0.45, f"reference ₹{base_rs / 1e5:.2f} lakh/yr", ha="center", fontsize=8, fontweight="bold")
ax.set_ylim(-0.6, len(tor) - 0.2)
ax.set_title("S6 · Sensitivity: which assumption matters most? (one at a time)")
footnote(fig, f"{NS} days per case, common random numbers · labels: low / high input")
save(fig, "S6_tornado.png")
R["S6"] = dict(reference_rs=float(base_rs), cases=[dict(name=n, low_input_rs=float(a), high_input_rs=float(b)) for n, a, b in tor])

# =============================================================== S7 timer study
T1s = [1, 2, 3, 5, 8, 10, 15, 20, 30]
s7 = []
for t1 in T1s:
    c = m.with_overrides(cfg, control__T1_min=t1, control__T2_min=max(30, t1 + 10))
    r = m.simulate_batched(c, NS, seed=7)
    savp = float((100 * (1 - r["E_ctrl"] / r["E_base"])).mean())
    nuis = float(r["n_nuisance"].mean() / r["machine_shifts"])
    false = float(r["n_false"].mean() / r["machine_shifts"])
    s7.append(dict(T1_min=t1, saving_pct=savp, nuisance_per_machine_shift=nuis, false_standby_per_machine_shift=false))
    print("S7", t1, savp, nuis, false)
R["S7"] = s7
fig, axs = plt.subplots(1, 2, figsize=(10, 4.4))
axs[0].plot(T1s, [s["saving_pct"] for s in s7], "-o", color=CTRL, lw=2, ms=6)
axs[0].set_xlabel("Standby timer T1 (min)"); axs[0].set_ylabel("Mean daily energy saving (%)")
axs[0].set_title("Saving falls as T1 grows")
axs[1].plot(T1s, [s["nuisance_per_machine_shift"] for s in s7], "-o", color=BASE, lw=2, ms=6,
            label="nuisance standby (person returns ≤ 5 min)")
axs[1].plot(T1s, [s["false_standby_per_machine_shift"] for s in s7], "-s", color=BLUE, lw=2, ms=6,
            label="false standby (operator present, not seen)")
axs[1].set_xlabel("Standby timer T1 (min)"); axs[1].set_ylabel("Events per machine-shift")
axs[1].set_title("Nuisance peaks when T1 sits just under a break")
axs[1].axvspan(10, 15, color="#F3E8E8", zorder=0)
axs[1].text(12.5, axs[1].get_ylim()[1] * 0.55, "15-min\ntea break\nzone", ha="center", fontsize=7, color=MUTED)
axs[1].legend(fontsize=8)
for a_ in axs:
    a_.axvline(cfg["control"]["T1_min"], color=MUTED, ls=":", lw=1)
fig.suptitle("S7 · Timer study: false/nuisance shutdowns vs savings trade-off", x=0.01, ha="left",
             color=BLUE, fontweight="bold", fontsize=12)
fig.tight_layout(rect=(0, 0.03, 1, 0.95))
footnote(fig, f"{NS} days per point · dotted line = chosen T1 = {cfg['control']['T1_min']} min")
save(fig, "S7_timer_tradeoff.png")

# =============================================================== S8 payback per node
node_kwh, node_rs = m.node_energy_rs(cfg)
M = cfg["shop"]["n_machines"]
rs_per_machine = ann["rs_total"] / M  # shop saving spread evenly over machines covered
ns = [1, 2, 3, 4, 6, 8, 10]
s8 = []
for reuse in (True, False):
    for n in ns:
        cost = m.node_cost(cfg, n, reuse_cctv=reuse)
        net = n * rs_per_machine - node_rs
        s8.append(dict(machines=n, reuse_cctv=reuse, cost_rs=float(cost), net_rs_yr=float(net),
                       payback_months=float(12 * cost / net)))
R["S8"] = dict(node_kwh_yr=float(node_kwh), node_rs_yr=float(node_rs), rs_per_machine_yr=float(rs_per_machine),
               rows=s8, full_shop_cost_rs=float(m.site_cost(cfg, True)),
               full_shop_payback_months=float(12 * m.site_cost(cfg, True) / (ann["rs_total"] - node_rs)),
               full_shop_cost_new_cams_rs=float(m.site_cost(cfg, False)),
               full_shop_payback_new_cams_months=float(12 * m.site_cost(cfg, False) / (ann["rs_total"] - node_rs)),
               node_share_of_saving_pct=float(100 * node_kwh / ann["kwh"]))
fig, ax = plt.subplots(figsize=(8.5, 4.8))
for reuse, col, lab in [(True, CTRL, "existing CCTV reused"), (False, BLUE, "new IP cameras (₹3,000 each)")]:
    rows = [r for r in s8 if r["reuse_cctv"] == reuse]
    ax.plot([r["machines"] for r in rows], [r["payback_months"] for r in rows], "-o", color=col, lw=2, ms=6, label=lab)
    for r in rows:
        if r["machines"] in (1, 4, 10):
            ax.annotate(f"{r['payback_months']:.1f}", (r["machines"], r["payback_months"]), xytext=(4, 6),
                        textcoords="offset points", fontsize=8, color=col)
ax.set_xlabel("Machines covered by one edge node"); ax.set_ylabel("Simple payback (months)")
ax.set_ylim(0, None)
ax.set_title("S8 · Payback per node, net of the node's own electricity")
ax.text(0.98, 0.62, f"Full shop incl. actuation + integration:\n₹{m.site_cost(cfg):,.0f} → "
        f"{12 * m.site_cost(cfg) / (ann['rs_total'] - node_rs):.1f} months",
        transform=ax.transAxes, ha="right", fontsize=8, color=INK,
        bbox=dict(boxstyle="round,pad=0.4", fc="#EEF2F8", ec="#C7D2E5"))
ax.legend()
footnote(fig, f"saving ₹{rs_per_machine:,.0f}/machine/yr (shop average) · node {cfg['node']['node_power_w']} W × 8,760 h")
save(fig, "S8_payback.png")

# =============================================================== S9 office case (v1, kept)
ov = cfg["office_v1"]
e_base = ov["baseline_kw"] * ov["baseline_h"]
e_ctrl = sum(ov["powers_kw"][s] * ov["hours"][s] for s in ov["powers_kw"])
e_sav = e_base - e_ctrl
node_day = ov["node_w"] * 24 / 1000
gross_rs = e_sav * ov["days"] * ov["tariff"]
net_rs = (e_sav - node_day) * ov["days"] * ov["tariff"]
R["S9"] = dict(E_base=e_base, E_ctrl=e_ctrl, saving_kwh=e_sav, saving_pct=100 * e_sav / e_base,
               annual_kwh=e_sav * ov["days"], gross_rs=gross_rs, net_rs=net_rs,
               payback_gross_months=12 * ov["node_cost"] / gross_rs, payback_net_months=12 * ov["node_cost"] / net_rs,
               net_retained_pct=100 * (e_sav - node_day) / e_sav)
fig, ax = plt.subplots(figsize=(8.5, 4.4))
cats = ["Office room\n(v1, 1 room)", "Machining shop\n(v2, 10 CNC + utilities)"]
pct = [R["S9"]["saving_pct"], R["S5"]["mean_pct"]]
bars = ax.bar(cats, pct, color=[CAT[1], CAT[0]], width=0.5, edgecolor="white")
for b_, v, sub in zip(bars, pct, [f"{e_sav:.1f} kWh/day", f"{R['S5']['mean_E_base_kwh'] - R['S5']['mean_E_ctrl_kwh']:,.0f} kWh/day"]):
    ax.text(b_.get_x() + b_.get_width() / 2, v + 0.4, f"{v:.1f} %\n{sub}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Modelled energy saving (%)")
ax.set_ylim(0, max(pct) * 1.35)
ax.grid(axis="x", visible=False)
ax.set_title("S9 · Same edge layer, two applications")
footnote(fig, "office = Review 3 reference day · shop = Monte-Carlo mean")
save(fig, "S9_office_vs_shop.png")

with open(HERE / "results.json", "w") as f:
    json.dump(R, f, indent=2, default=float)
print("done")
