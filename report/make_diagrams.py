"""Diagrams for the report (architecture, state machine, shop layout). 300 dpi PNG."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)
BLUE = "#2F4F8F"
GREEN = "#2E7D32"
GREY = "#6B7280"
INK = "#222222"
plt.rcParams.update({"font.family": ["Liberation Sans", "DejaVu Sans"], "font.size": 9})


def box(ax, x, y, w, h, text, status="impl", fs=8.5, bold=False):
    style = {"impl": dict(fc="#E8F3E9", ec=GREEN, ls="-"),
             "model": dict(fc="#EEF2F8", ec=BLUE, ls="--"),
             "future": dict(fc="#F1F2F4", ec=GREY, ls=":"),
             "dark": dict(fc=BLUE, ec=BLUE, ls="-")}[status]
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.08",
                       fc=style["fc"], ec=style["ec"], ls=style["ls"], lw=1.4)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color="white" if status == "dark" else INK, fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, x0, y0, x1, y1, color=INK):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=10, color=color, lw=1.1))


# ---------------------------------------------------------------- Fig 3.1 architecture
fig, ax = plt.subplots(figsize=(10, 6.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 6.4); ax.axis("off")
rows = [
    (5.3, "IMPLEMENTED · EDGE NODE", GREEN, "impl",
     ["Camera\n(C920 / CCTV)", "V4L2 +\nGStreamer", "nvstreammux", "nvinfer\nResNet10\nTensorRT FP16", "Person\nmetadata\n(PyDS)", "Temporal\nfilter"]),
    (3.6, "MODELLED · MANUFACTURING DECISION LAYER (model v2)", BLUE, "model",
     ["Machine and\nzone ROIs", "CT clamp\nactivity a(t)", "Machine state\nmachine", "Zone rules\n(light, fan,\nconveyor, air)", "ADVISORY /\nAUTO mode", "kW, kWh, ₹,\nkVA, CO₂"]),
    (1.9, "FUTURE · INTEGRATION AND MEASUREMENT", GREY, "future",
     ["MQTT 5.0\ntelemetry", "Modbus TCP /\nrelays / VFD", "PROFIenergy\npause", "OPC UA /\numati", "CT / smart\nmeter M&V", "ISO 50001\nEnPI"]),
]
w, h, gap = 1.42, 1.0, 0.2
for y, label, col, st, items in rows:
    ax.text(0.05, (y - 0.3) if st == "future" else (y + h + 0.12), label, color=col, fontweight="bold", fontsize=9)
    for i, t in enumerate(items):
        x = 0.05 + i * (w + gap)
        box(ax, x, y, w, h, t, st)
        if i:
            arrow(ax, x - gap + 0.02, y + h / 2, x - 0.02, y + h / 2)
arrow(ax, 0.05 + 5 * (w + gap) + w / 2, 5.3, 0.05 + 2 * (w + gap) + w / 2, 3.6 + h, BLUE)
for i in range(6):
    x = 0.05 + i * (w + gap) + w / 2
    arrow(ax, x, 3.6, x, 1.9 + h, GREY)
box(ax, 0.6, 0.15, 8.8, 0.8, "Privacy by design: video never leaves the node; only counts, states and kW are published", "dark", 9, True)
fig.savefig(OUT / "fig_architecture.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- Fig 3.2 machine state machine
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.set_xlim(0, 10); ax.set_ylim(0, 4.6); ax.axis("off")
S = [("PROCESSING\na = 1\n7.5 kW", 0.2, "#2F4F8F"), ("IDLE-ATTENDED\na = 0, o = 1\n3.0 kW", 2.7, "#2A9D8F"),
     ("IDLE-UNATTENDED\na = 0, o = 0\n> T1 → STANDBY\n1.2 kW", 5.2, "#C9852B"), ("DEEP STANDBY\n> T2, whitelist\n0.35 kW", 7.7, "#6B7280")]
for t, x, c in S:
    p = FancyBboxPatch((x, 1.9), 2.1, 1.3, boxstyle="round,pad=0.02,rounding_size=0.12", fc=c, ec=c)
    ax.add_patch(p)
    ax.text(x + 1.05, 2.55, t, ha="center", va="center", color="white", fontweight="bold", fontsize=9)
lab = ["cutting stops", "operator leaves\n(fall hold 60 s)", "unattended > T2\n(AUTO only)"]
back = ["cycle start", "operator returns\n(rise hold 10 s)", "operator restarts\n(+ warm-up)"]
for i in range(3):
    x0 = S[i][1] + 2.1; x1 = S[i + 1][1]
    arrow(ax, x0 + 0.02, 2.95, x1 - 0.02, 2.95)
    arrow(ax, x1 - 0.02, 2.15, x0 + 0.02, 2.15)
    ax.text((x0 + x1) / 2, 3.35, lab[i], ha="center", fontsize=7.5, color=INK)
    ax.text((x0 + x1) / 2, 1.45, back[i], ha="center", fontsize=7.5, color=INK, va="top")
ax.text(5, 4.25, "Machine state machine per machine k (inputs: o = operator in ROI, a = CT activity)",
        ha="center", color=BLUE, fontweight="bold", fontsize=10)
ax.text(5, 0.35, "Safety rule: the node may request standby but never starts a machine. Precision machines: ADVISORY only, never DEEP STANDBY.",
        ha="center", fontsize=8, color=GREY, style="italic")
fig.savefig(OUT / "fig_state_machine.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- Fig 3.3 shop layout with zones
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_xlim(0, 20); ax.set_ylim(0, 10); ax.set_aspect("equal"); ax.axis("off")
zones = [(0.3, 5.3, 6.2, 4.3, "Zone 1  (M1-M3)  AUTO"), (6.8, 5.3, 6.2, 4.3, "Zone 2  (M4-M6)  AUTO"),
         (13.05, 5.3, 6.65, 4.3, "Zone 3  (M7-M10)  ADVISORY"), (0.3, 0.3, 19.4, 4.6, "")]
for x, y, w_, h_, t in zones[:3]:
    ax.add_patch(FancyBboxPatch((x, y), w_, h_, boxstyle="round,pad=0.02", fc="#F6F8FB", ec=BLUE, ls="--"))
    ax.text(x + 0.2, y + h_ - 0.45, t, color=BLUE, fontweight="bold", fontsize=8)
mx = [(1.0, 1), (3.0, 2), (5.0, 3), (7.5, 4), (9.5, 5), (11.5, 6), (13.8, 7), (15.3, 8), (16.8, 9), (18.3, 10)]
for x, n in mx:
    c = "#2F4F8F" if n <= 6 else "#7B5EA7"
    ax.add_patch(FancyBboxPatch((x - 0.6, 7.2), 1.2, 1.2, boxstyle="round,pad=0.02", fc=c, ec=c))
    ax.text(x, 7.8, f"M{n}", color="white", ha="center", va="center", fontweight="bold", fontsize=8)
    ax.add_patch(plt.Rectangle((x - 0.6, 5.7), 1.2, 1.2, fc="none", ec=GREEN, lw=1.2))
    ax.text(x, 6.3, "ROI", color=GREEN, ha="center", va="center", fontsize=6.5)
ax.add_patch(plt.Rectangle((0.6, 4.3), 9.0, 0.5, fc="#C9852B", ec="none", alpha=0.8))
ax.text(5.1, 4.55, "Conveyor line (M1-M5)", ha="center", va="center", fontsize=7.5, color="white", fontweight="bold")
ax.add_patch(FancyBboxPatch((0.3, 0.3), 19.4, 3.6, boxstyle="round,pad=0.02", fc="#FBFBF7", ec=GREY, ls=":"))
ax.text(0.5, 3.4, "Zone 4  Aisle / stores / inspection", color=GREY, fontweight="bold", fontsize=8)
ax.add_patch(FancyBboxPatch((15.5, 0.7), 3.6, 1.6, boxstyle="round,pad=0.02", fc="#2A9D8F", ec="#2A9D8F"))
ax.text(17.3, 1.5, "Compressor\n22 kW", color="white", ha="center", va="center", fontsize=8, fontweight="bold")
for cx in (3, 10, 17):
    ax.plot([cx], [9.8], marker="v", color=INK, ms=9)
ax.text(9, 2.4, "▼ = camera (existing CCTV, 4 machines per camera assumed)", ha="center", fontsize=8, color=INK)
ax.text(9, 1.5, "High-bay lighting: 3.6 kW per zone · extraction fan: 3.7 kW per zone", ha="center", fontsize=8, color=INK)
fig.savefig(OUT / "fig_shop_layout.png", dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("diagrams done")
