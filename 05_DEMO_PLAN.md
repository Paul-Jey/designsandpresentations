# 05 — LIVE DEMO PLAN (viva) — OPTIONAL if time is short

Goal: show, live on the existing Jetson, the full chain **operator leaves → timer → IDLE-UNATTENDED → action → kWh and ₹ update**.
Fallback if hardware fails: replay a recorded `live_state.json` log through the same dashboard (keep a screen recording too).

## 1. Bench set-up

```
 [C920 camera] ──USB──► [Jetson Nano] ── GPIO / USB ──► [Relay module] ──► 230 V or 12 V "machine"
                              ▲                                              │
                              └── ADS1115 (I²C) ◄── burden + SCT-013 CT ◄─────┘   (current = activity)
 Desk = "workstation ROI"; small fan / drill / DC motor = "machine"
```

Two options for the "machine" (pick one; Option A is safer in a viva hall):

| Option | Machine | Sensing | Switching | Safety |
|---|---|---|---|---|
| **A (recommended)** | 12 V DC motor or 12 V fan from a 12 V 2 A adapter | INA219 current sensor (I²C) | 5 V relay on 12 V side | No mains on the bench |
| B | 230 V table fan (≈ 50 W) on a plug board | SCT-013-030 CT + ADS1115 | 5 V relay with opto + mains-rated enclosure, or a smart plug with power reading and local API | Mains: enclosed, fused, checked by lab staff |

## 2. Parts and cost (indicative, Oct 2026)

| Part | Qty | ₹ (approx.) |
|---|---|---|
| Jetson Nano + C920 (already owned) | 1 | 0 |
| 12 V DC fan or motor + 12 V 2 A adapter | 1 | 450 |
| INA219 current/power sensor breakout | 1 | 250 |
| 1-channel 5 V relay module (opto-isolated) | 1 | 120 |
| Jumper wires, terminal block, small board | 1 set | 200 |
| *(Option B only)* SCT-013-030 CT | 1 | 650 |
| *(Option B only)* ADS1115 16-bit ADC | 1 | 300 |
| *(Option B only)* enclosure, fuse, plug board | 1 | 600 |
| **Total Option A** | | **≈ ₹1,020** |
| **Total Option B** | | **≈ ₹2,570** |

## 3. What the team must code (small)

1. **ROI presence** — in the existing PyDS probe, count persons whose bbox centre lies inside a desk ROI polygon (or enable `nvdsanalytics` ROI filtering). Output `o(t)`.
2. **Activity** — read INA219 at 2 Hz; `a(t) = I > I_th` (I_th ≈ 30 % of running current).
3. **State machine** — port the v2 rules: rise hold 10 s, fall hold 60 s, **T1 = 30 s in demo** (scaled down from 3 min so the panel can see it), T2 = 90 s demo.
4. **Action** — in AUTO mode toggle the relay GPIO to cut the "machine"; in ADVISORY mode only show a red banner "Machine 1 unattended — standby recommended".
5. **Energy counters** — integrate measured P (from INA219: V × I) for controlled; integrate "machine left on" power for baseline; show kWh, ₹ (× 7.50) and CO₂ (× 0.710) live.
6. **Dashboard** — add a machine card: state chip (PROCESSING / IDLE-ATTENDED / IDLE-UNATTENDED / STANDBY), timer countdown, mode switch (ADVISORY/AUTO).

Rule kept in demo: **the node never restarts the machine**; the operator presses a "Resume" button.

## 4. Demo script (≈ 90 s inside the 10-minute talk)

1. Operator sits at desk, fan running → PROCESSING.
2. Operator stops the fan with a switch but stays → IDLE-ATTENDED (no action).
3. Operator walks away → countdown 30 s → IDLE-UNATTENDED → relay opens (AUTO) → power drops on dashboard; kWh/₹ "avoided" counter starts rising.
4. Operator returns → presses Resume → PROCESSING.
5. Switch mode to ADVISORY → repeat step 3 → only an alert appears (precision-machine behaviour).

## 5. What to measure during the demo week (fills FUTURE items honestly)

- Detector precision/recall on 200 labelled desk frames (person in ROI vs not).
- Jetson FPS and end-to-end latency (frame → state change).
- Jetson input power with a USB power meter (replace the 12.5 W rated figure).
- False-standby count over a 1-hour session with normal desk movement.

Label all of these MEASURED (bench) in the report; savings remain MODELLED.
