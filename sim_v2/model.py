"""sim_v2 model: Edge-AI idle-energy control of a reference MSME machining shop.

MODELLED, model v2. All inputs come from assumptions.yaml.
Time step dt (default 10 s); arrays are vectorised over simulated days.
"""
import copy
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).parent

# machine controlled states
PROC, IDLE_ATT, IDLE_UNATT, STANDBY, DEEP, OFF = range(6)
LOADS = ["CNC machines", "Compressor", "Conveyor", "Lighting", "Ventilation fans"]


def load_cfg(path=HERE / "assumptions.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def _steps(cfg, minutes):
    return int(round(minutes * 60 / cfg["meta"]["dt_s"]))


def _hour_idx(cfg, h):
    return int(round(h * 3600 / cfg["meta"]["dt_s"]))


# ---------------------------------------------------------------- day generation
def gen_machine_day(rng, cfg, left_on):
    """True machine activity a, true operator presence o, and powered flag (baseline)."""
    op = cfg["operations"]
    T = _hour_idx(cfg, 24)
    a = np.zeros(T, np.int8)
    o = np.zeros(T, np.int8)
    on = np.zeros(T, np.int8)
    st = lambda m: _steps(cfg, m)

    def put(arr, i0, n, v):
        i0 = max(i0, 0)
        arr[i0:min(i0 + n, T)] = v

    for s0h, s1h in cfg["shop"]["shifts"]:
        s0, s1 = _hour_idx(cfg, s0h), _hour_idx(cfg, s1h)
        if s1 > T:  # night shift wraps past midnight
            segs = [(s0, T), (0, s1 - T)]
        else:
            segs = [(s0, s1)]
        for x0, x1 in segs:
            on[x0:x1] = 1
            o[x0:x1] = 1
        L = s1 - s0
        idx = lambda k: (s0 + k) % T  # position inside shift, wrapped

        # machining cycles with load/unload gaps
        k = 0
        shift_a = np.zeros(L, np.int8)
        while k < L:
            c = max(st(2), int(rng.exponential(st(op["cycle_proc_min"]))))
            shift_a[k:k + c] = 1
            k += c + st(op["load_unload_min"])
        shift_o = np.ones(L, np.int8)

        def ev(k0, n, a_val, o_val):
            k0 = max(0, k0)
            shift_a[k0:k0 + n] = a_val
            if o_val is not None:
                shift_o[k0:k0 + n] = o_val

        # random events (order: frequent -> rare; breaks override at the end)
        for _ in range(rng.poisson(op["short_absence_rate"])):
            k0 = int(rng.integers(0, L))
            shift_o[k0:k0 + max(1, int(rng.exponential(st(op["short_absence_min"]))))] = 0
        for _ in range(rng.poisson(op["tool_change_rate"])):
            ev(int(rng.integers(0, L)), max(1, int(rng.exponential(st(op["tool_change_min"])))), 0, 1)
        for _ in range(rng.poisson(op["material_wait_rate"])):
            d = rng.lognormal(np.log(op["material_wait_median_min"]), op["material_wait_sigma"])
            ev(int(rng.integers(0, L)), st(d), 0, 0 if rng.random() < op["material_wait_p_absent"] else 1)
        if rng.random() < op["breakdown_prob"]:
            d = rng.uniform(*op["breakdown_min"])
            ev(int(rng.integers(0, L)), st(d), 0, 0 if rng.random() < op["breakdown_p_absent"] else 1)
        # fixed shift structure
        ev(0, st(op["setup_start_min"]), 0, 1)
        for bh in op["tea_breaks_h"]:
            ev(st(bh * 60 + rng.uniform(-5, 5)), st(op["tea_min"]), 0, 0)
        ev(st(op["lunch_h"] * 60 + rng.uniform(-5, 5)), st(op["lunch_min"]), 0, 0)
        cm = op["changeover_min"]
        ev(L - st(cm), st(5), 0, 1)
        ev(L - st(cm - 5), st(cm - 5), 0, 0)
        pos = (s0 + np.arange(L)) % T
        a[pos] = shift_a
        o[pos] = shift_o

    if left_on:
        on[:] = np.where(on == 0, 1, on)  # left powered and idle outside shifts
    return a, o, on


def gen_aisle(rng, cfg, shift_mask):
    op = cfg["operations"]
    T = len(shift_mask)
    z = np.zeros(T, np.int8)
    k, busy = 0, False
    while k < T:
        m = op["aisle_busy_mean_min"] if busy else op["aisle_empty_mean_min"]
        n = max(1, int(rng.exponential(_steps(cfg, m))))
        if busy:
            z[k:k + n] = 1
        k += n
        busy = not busy
    return z * shift_mask


def gen_days(cfg, n_days, seed):
    rng = np.random.default_rng(seed)
    M = cfg["shop"]["n_machines"]
    T = _hour_idx(cfg, 24)
    A = np.zeros((n_days, M, T), np.int8)
    O = np.zeros((n_days, M, T), np.int8)
    ON = np.zeros((n_days, M, T), np.int8)
    shift_mask = np.zeros(T, np.int8)
    for s0h, s1h in cfg["shop"]["shifts"]:
        s0, s1 = _hour_idx(cfg, s0h), _hour_idx(cfg, s1h)
        shift_mask[s0:min(s1, T)] = 1
        if s1 > T:
            shift_mask[:s1 - T] = 1
    Z4 = np.zeros((n_days, T), np.int8)
    for d in range(n_days):
        for m in range(M):
            left_on = rng.random() < cfg["operations"]["night_left_on_prob"]
            A[d, m], O[d, m], ON[d, m] = gen_machine_day(rng, cfg, left_on)
        Z4[d] = gen_aisle(rng, cfg, shift_mask)
    return dict(A=A, O=O, ON=ON, Z4=Z4, shift=shift_mask, rng=rng)


# ---------------------------------------------------------------- detection + filter
def detect_and_filter(cfg, O, rng):
    """Camera presence with misses, false positives and occlusion bursts, then rise/fall hold."""
    det = cfg["detection"]
    dt = cfg["meta"]["dt_s"]
    seen = O.copy()
    # occlusion bursts while present
    shape = O.shape
    T = shape[-1]
    n_shifts = len(cfg["shop"]["shifts"])
    lam = det["occlusion_rate"] * n_shifts
    flat = seen.reshape(-1, T)
    for r in range(flat.shape[0]):
        for _ in range(rng.poisson(lam)):
            k0 = int(rng.integers(0, T))
            n = max(1, int(rng.exponential(det["occlusion_mean_s"] / dt)))
            flat[r, k0:k0 + n] = 0
    seen = flat.reshape(shape)
    miss = rng.random(shape) < det["miss_prob"]
    fp = rng.random(shape) < det["false_pos_prob"]
    raw = np.where(seen == 1, ~miss, fp).astype(np.int8)
    return hold_filter(raw, det["rise_hold_s"] // dt + 1, det["fall_hold_s"] // dt)


def hold_filter(raw, rise, fall):
    """Asymmetric persistence filter along last axis (v1 temporal filter)."""
    out = np.zeros_like(raw)
    state = np.zeros(raw.shape[:-1], np.int8)
    cnt = np.zeros(raw.shape[:-1], np.int32)
    for t in range(raw.shape[-1]):
        x = raw[..., t]
        diff = x != state
        cnt = np.where(diff, cnt + 1, 0)
        need = np.where(state == 0, rise, fall)
        flip = diff & (cnt >= need)
        state = np.where(flip, x, state).astype(np.int8)
        cnt = np.where(flip, 0, cnt)
        out[..., t] = state
    return out


def off_hold(x, n):
    """CT activity: on immediately, off only after n steps low."""
    out = np.zeros_like(x)
    last = np.full(x.shape[:-1], -10 ** 9)
    for t in range(x.shape[-1]):
        last = np.where(x[..., t] == 1, t, last)
        out[..., t] = (t - last) <= n
    return out


def recent(x, n):
    """1 if x was 1 at any step in the last n steps (inclusive)."""
    return off_hold(x, n)


# ---------------------------------------------------------------- simulation
def simulate(cfg, n_days=1, seed=None, keep_series=False, data=None):
    seed = cfg["meta"]["seed"] if seed is None else seed
    if data is None:
        data = gen_days(cfg, n_days, seed)
    A, O, ON, Z4, shift, rng = data["A"], data["O"], data["ON"], data["Z4"], data["shift"], data["rng"]
    D, M, T = A.shape
    dt = cfg["meta"]["dt_s"]
    h = dt / 3600.0
    mp, ol, ctl = cfg["machine_power_kw"], cfg["other_loads_kw"], cfg["control"]
    st = lambda m: _steps(cfg, m)

    Of = detect_and_filter(cfg, O, rng)
    Af = off_hold(A, max(1, cfg["detection"]["ct_off_hold_s"] // dt))

    white = np.zeros(M, bool)
    white[cfg["shop"]["whitelist_auto"]] = True
    T1, T2 = st(ctl["T1_min"]), st(ctl["T2_min"])
    adv_delay = st(ctl["advisory_delay_min"])
    nuis_win = st(ctl["nuisance_window_min"])

    # ---- baseline machine power
    Pm_base = np.where(ON == 1, np.where(A == 1, mp["processing"], mp["idle"]), 0.0)

    # ---- controlled machine state machine
    Pm_ctrl = np.zeros((D, M, T), np.float32)
    state_ctrl = np.zeros((D, M, T), np.int8) if keep_series else None
    timer = np.zeros((D, M), np.int32)
    in_deep = np.zeros((D, M), bool)
    sb_entry = np.full((D, M), -1, np.int64)
    comply = np.zeros((D, M), bool)
    warm_kwh = np.zeros(D)
    n_standby = np.zeros(D)
    n_nuisance = np.zeros(D)
    n_false = np.zeros(D)  # standby entered while operator truly present
    for t in range(T):
        on, af, of = ON[:, :, t] == 1, Af[:, :, t] == 1, Of[:, :, t] == 1
        active = af | of
        unatt = on & ~active
        newly = unatt & (timer == 0)
        comply = np.where(newly, rng.random((D, M)) < ctl["advisory_compliance"], comply)
        timer = np.where(unatt, timer + 1, 0)
        # leaving standby/deep
        was_sb = sb_entry >= 0
        leaving = was_sb & active
        n_nuisance += (leaving & ((t - sb_entry) <= nuis_win)).sum(1)
        warm_kwh += (leaving & in_deep).sum(1) * mp["warmup_kw"] * mp["warmup_min"] / 60.0
        sb_entry = np.where(leaving | ~on, -1, sb_entry)
        in_deep = np.where(leaving | ~on, False, in_deep)

        in_shift = shift[t] == 1
        sb_white = unatt & white[None, :] & (timer > T1)
        sb_adv = unatt & ~white[None, :] & comply & (timer > T1 + adv_delay) & in_shift
        sb = sb_white | sb_adv
        deep = unatt & white[None, :] & (timer > T2)
        entering = sb & (sb_entry < 0)
        n_standby += entering.sum(1)
        # false standby: operator truly present for the last 30 s but not seen by the camera
        n_false += (entering & (O[:, :, max(0, t - 3):t + 1].min(2) == 1)).sum(1)
        sb_entry = np.where(entering, t, sb_entry)
        in_deep = in_deep | deep

        # physical power follows the true machine activity; the node only changes idle draw
        P = np.where(A[:, :, t] == 1, mp["processing"], mp["idle"])
        P = np.where(sb, mp["standby"], P)
        P = np.where(deep, mp["deep_standby"], P)
        P = np.where(on, P, 0.0)
        Pm_ctrl[:, :, t] = P
        if keep_series:
            s = np.where(af, PROC, np.where(of, IDLE_ATT, IDLE_UNATT))
            s = np.where(sb, STANDBY, s)
            s = np.where(deep, DEEP, s)
            state_ctrl[:, :, t] = np.where(on, s, OFF)

    # ---- shared loads
    shiftb = shift[None, :].astype(bool)
    zones = cfg["shop"]["zones"]
    Zt = np.zeros((D, len(zones), T), np.int8)  # true zone occupancy
    Zf = np.zeros((D, len(zones), T), np.int8)  # filtered (camera)
    Zact = np.zeros((D, len(zones), T), np.int8)
    for j, ms in enumerate(zones):
        if ms:
            Zt[:, j] = O[:, ms].max(1)
            Zf[:, j] = Of[:, ms].max(1)
            Zact[:, j] = Af[:, ms].max(1)
        else:
            Zt[:, j] = Z4
    z4raw = np.where(Z4 == 1, rng.random(Z4.shape) > cfg["detection"]["miss_prob"],
                     rng.random(Z4.shape) < cfg["detection"]["false_pos_prob"]).astype(np.int8)
    Zf[:, 3] = hold_filter(z4raw, 1, max(1, cfg["detection"]["fall_hold_s"] // dt))

    # conveyor
    line = cfg["shop"]["conveyor_line"]
    conv_b = np.where(shiftb, ol["conveyor"], 0.0) * np.ones((D, 1))
    conv_on = recent(Af[:, line].max(1), st(ctl["conveyor_hold_min"])) & shiftb
    conv_c = np.where(conv_on, ol["conveyor"], 0.0)

    # compressor: load/unload with leak load
    def comp_power(active_count, run):
        f = np.clip(ol["compressor_leak_frac"] + active_count * ol["compressor_demand_per_proc_machine"], 0, 1)
        P = ol["compressor_full"] * (f + (1 - f) * ol["compressor_unload_frac"])
        return np.where(run, P, 0.0)

    comp_b = comp_power(A.sum(1), np.broadcast_to(shiftb, (D, T)))
    shop_active = recent(Af.max(1), st(ctl["compressor_hold_min"]))
    comp_c = comp_power(Af.sum(1), shop_active & shiftb)

    # lighting and fans per zone
    light_b = np.zeros((D, T))
    light_c = np.zeros((D, T))
    fan_b = np.zeros((D, T))
    fan_c = np.zeros((D, T))
    for j in range(len(zones)):
        occ_l = recent(Zf[:, j], st(ctl["light_hold_min"]))
        light_b += np.where(shiftb, ol["lighting_per_zone"], 0.0)
        light_c += np.where(shiftb, np.where(occ_l, 1.0, ol["lighting_dim_frac"]) * ol["lighting_per_zone"], 0.0)
        need_fan = recent(np.maximum(Zf[:, j], Zact[:, j]), st(ctl["fan_hold_min"]))
        fan_b += np.where(shiftb, ol["fan_per_zone"], 0.0)
        fan_c += np.where(shiftb & need_fan, ol["fan_per_zone"], 0.0)

    base = {"CNC machines": Pm_base.sum(1), "Compressor": comp_b, "Conveyor": conv_b,
            "Lighting": light_b, "Ventilation fans": fan_b}
    ctrl = {"CNC machines": Pm_ctrl.sum(1), "Compressor": comp_c, "Conveyor": conv_c,
            "Lighting": light_c, "Ventilation fans": fan_c}
    Pb = sum(base.values())
    Pc = sum(ctrl.values())

    E_b = {k: v.sum(1) * h for k, v in base.items()}
    E_c = {k: v.sum(1) * h for k, v in ctrl.items()}
    E_c["CNC machines"] = E_c["CNC machines"] + warm_kwh

    blk = st(15)
    nb = T // blk
    pf = ol["power_factor"]
    md_b = Pb[:, :nb * blk].reshape(D, nb, blk).mean(2).max(1) / pf
    md_c = Pc[:, :nb * blk].reshape(D, nb, blk).mean(2).max(1) / pf

    # idle-energy ratio (non-processing machine energy / total shop energy)
    proc_b = (np.where((ON == 1) & (A == 1), mp["processing"], 0).sum((1, 2))) * h
    proc_c = proc_b

    res = dict(
        E_base=sum(E_b.values()), E_ctrl=sum(E_c.values()), E_b=E_b, E_c=E_c,
        md_base=md_b, md_ctrl=md_c, peak_base=Pb.max(1), peak_ctrl=Pc.max(1),
        avg_base=Pb.mean(1), avg_ctrl=Pc.mean(1),
        ier_base=(E_b["CNC machines"] - proc_b) / sum(E_b.values()),
        ier_ctrl=(E_c["CNC machines"] - proc_c) / sum(E_c.values()),
        n_standby=n_standby, n_nuisance=n_nuisance, n_false=n_false, warm_kwh=warm_kwh,
        machine_shifts=M * len(cfg["shop"]["shifts"]),
    )
    if keep_series:
        res.update(Pb=Pb, Pc=Pc, base=base, ctrl=ctrl, A=A, O=O, Of=Of, Af=Af,
                   Pm_base=Pm_base, Pm_ctrl=Pm_ctrl, state=state_ctrl, dt=dt)
    return res


# ---------------------------------------------------------------- economics
def annual(cfg, res):
    """Annual kWh, energy ₹, demand ₹, CO2 from a set of simulated days (means / monthly max)."""
    tf = cfg["tariff"]
    dpy = cfg["meta"]["days_per_year"]
    e_save_day = float(np.mean(res["E_base"] - res["E_ctrl"]))
    kwh = e_save_day * dpy
    rs_energy = kwh * tf["energy_rs_per_kwh"]
    dpm = tf["days_per_month"]
    floor = tf["billing_floor_frac"] * tf["contract_demand_kva"]

    def monthly_bill(md):
        n = max(1, len(md) // dpm)
        months = [md[i * dpm:(i + 1) * dpm].max() for i in range(n)] if len(md) >= dpm else [md.max()]
        return np.mean([max(m, floor) for m in months]) * tf["demand_rs_per_kva_month"]

    rs_demand = (monthly_bill(res["md_base"]) - monthly_bill(res["md_ctrl"])) * 12
    co2_t = kwh * cfg["carbon"]["ef_kg_per_kwh"] / 1000
    return dict(kwh=kwh, rs_energy=rs_energy, rs_demand=rs_demand, rs_total=rs_energy + rs_demand,
                co2_t=co2_t, e_save_day=e_save_day)


def node_cost(cfg, n_machines, reuse_cctv=True):
    nd = cfg["node"]
    cams = int(np.ceil(n_machines / nd["machines_per_camera"]))
    return (nd["jetson_rs"] + nd["psu_sd_enclosure_rs"] + nd["relay_io_modbus_rs"] + nd["ct_interface_rs"]
            + nd["install_misc_rs"] + n_machines * nd["ct_per_machine_rs"]
            + (0 if reuse_cctv else cams * nd["camera_rs"]))


def site_cost(cfg, reuse_cctv=True):
    """Full-shop cost: node + CTs + actuation for shared loads + integration labour."""
    sa = cfg["site_actuation"]
    nz = len(cfg["shop"]["zones"])
    return (node_cost(cfg, cfg["shop"]["n_machines"], reuse_cctv) + nz * sa["lighting_zone_rs"]
            + nz * sa["fan_contactor_rs"] + sa["conveyor_compressor_rs"] + sa["integration_rs"])


def node_energy_rs(cfg):
    nd = cfg["node"]
    kwh = nd["node_power_w"] / 1000 * nd["node_hours_per_year"]
    return kwh, kwh * cfg["tariff"]["energy_rs_per_kwh"]


def with_overrides(cfg, **kw):
    c = copy.deepcopy(cfg)
    for path, v in kw.items():
        node = c
        keys = path.split("__")
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] = v
    return c


def simulate_batched(cfg, n_days, seed=None, batch=100):
    """Monte-Carlo over many days in batches; returns concatenated per-day metrics."""
    seed = cfg["meta"]["seed"] if seed is None else seed
    out = None
    for b in range(int(np.ceil(n_days / batch))):
        nd = min(batch, n_days - b * batch)
        r = simulate(cfg, nd, seed=seed + 1000 + b)
        flat = {k: v for k, v in r.items() if isinstance(v, np.ndarray)}
        flat["E_b"] = r["E_b"]
        flat["E_c"] = r["E_c"]
        if out is None:
            out = flat
            out["machine_shifts"] = r["machine_shifts"]
        else:
            for k, v in flat.items():
                if isinstance(v, dict):
                    for kk in v:
                        out[k][kk] = np.concatenate([out[k][kk], v[kk]])
                else:
                    out[k] = np.concatenate([out[k], v])
    return out
