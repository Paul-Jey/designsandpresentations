# 01 — PROJECT CONTEXT (read this first)

## 1. Who and what
- **College:** Sri Sivasubramaniya Nadar (SSN) College of Engineering, Dept. of EEE (Autonomous, Anna University).
- **Course:** UEE2718 – Project Phase 1. Batch **B2**.
- **Team:** Paul Jey Sanjith J (3122233001069), Oviyan P S (3122233001067), Thirsna S (3122233001309).
- **Guide:** Dr. Rajesh Panda, Professor / EEE, SSNCE.
- **Current title:** "AI Data Analytics Layer for Surveillance Systems Using Edge AI for Energy Management Systems". Subtitle: "Edge-AI occupancy intelligence for building energy management".
- **Status:** Review 3 done. Industry experts were satisfied. Next: **final project report (thesis)** + **final viva-voce**.

## 2. What exists today (Review 3 state)
### Implemented (real hardware, live)
- Jetson Nano 4 GB + Logitech C920 + DeepStream 6.0.1 + TensorRT FP16 + NVIDIA ResNet10 person detector.
- Pipeline: Camera → V4L2 → GStreamer → nvstreammux → nvinfer → object metadata (PyDS) → person count n(t) → temporal filter → `live_state.json` → live dashboard.
- Only metadata leaves the device (privacy). Node cost ₹17,500.

### Modelled (Python simulation, "model v1")
- 4-state machine on occupancy: Unoccupied (n=0, 27 °C, lights off, 0.30 kW), Economy (1–2, 25 °C, 1.20 kW), Comfort (3–5, 24 °C, 1.70 kW), High Demand (≥6, 23.5 °C, 2.00 kW). Rise hold 10 s, fall hold 30 s.
- Equations: P(t)=P_HVAC+P_Light; E=ΣP·Δt; E_saved=E_base−E_ctrl; Cost=E_saved×Tariff; CO₂=E_saved×EF.
- Reference day: 17.0 → 13.8 kWh/day, 3.2 kWh saved (18.8 %). 1,168 kWh/yr, ₹9,344/yr (₹8/kWh assumed), 0.83 t CO₂/yr (CEA EF 0.710 kg/kWh, FY24-25). Net of node load (12.5 W × 24 h) 90.6 % retained.
- Temporal filter study: 2,633 → 9 state changes/day, 99.1 % time in correct state (10 % simulated miss).
- Monte-Carlo 1,000 days: mean 24.4 %, P5–P95 10–40 %, positive on 99.9 % days.
- Sensitivity: occupancy pattern dominates; tariff, HVAC size, days only scale.
- Payback: 22.5 months (1 room), ~11 months (2 rooms/node).
- Load-duration: energy down, peak up (2.00 kW). Honest claim: energy, not peak.

### Future (not built)
- CT / smart meter validation, MQTT 5.0, BACnet (ASHRAE 135), ONVIF/RTSP for CCTV, BAS/BMS. Measure precision/recall, FPS, latency, node power.

## 3. What the experts asked for (THE PIVOT)
1. **Apply it to manufacturing industries, not only offices.** Factories consume large electricity, and **machines left idle** waste a lot.
2. **Use the AI for more than HVAC.** The same camera intelligence can drive other energy decisions (machines, lighting, compressed air, conveyors, exhaust, etc.).
3. Incorporate their corrections to improve report quality.

## 4. Hard requirements from the department
- Report: **60 pages ±10 %** (Chapter 1 first page → last page of References).
- Front page month/year: **NOVEMBER 2026**.
- Follow SSN template (COE website / LMS). Guidelines PDF is attached separately.
- **Turnitin similarity ≤ 30 %** and **AI-detection ≤ 10 %**. Thesis must be signed by supervisor.
- Final PPT: **max 15 slides**, covers milestones of all three phases. Viva = 10 min talk + 5 min Q&A + **live demo**.

## 5. Panel preferences (known from earlier reviews)
- The panel likes **simulated results, clear graphs and equations** more than hardware alone.
- They respect honesty labels: IMPLEMENTED / MODELLED / FUTURE. Keep this labelling.
- EEE department: frame everything in electrical terms (kW, kWh, load factor, power factor, demand, tariff, CO₂).
