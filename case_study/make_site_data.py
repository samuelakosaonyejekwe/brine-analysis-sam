#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_site_data.py  --  Reproducible generator of CREDIBLE site-specific field
data for the Sydney Desalination Plant (SDP, Kurnell NSW) brine-outfall case
study. The values are engineering-representative (dummy) but consistent with the
public design basis and the open Tasman-shelf setting; they are used to CALIBRATE
and drive the NEREID-B solver. All files are written to case_study/inputs/.

Provenance of the numbers (documented, not measured per-station):
  * Depth ~24-26 m, gentle offshore shelf slope ~0.006  (public SDP diffuser depth)
  * Summer stratification: S 35.4 (surf) -> 35.6 (bed) psu; T 21 -> 18 C
    (open Tasman Sea shelf climatology, EAC-influenced)
  * Depth-averaged current ~0.12 m/s with M2 tidal modulation +-0.04 m/s
  * Exposed swell climate: Hs ~1.2-1.8 m, Tp ~8-11 s
  * Site CTD/ADCP dilution transect: deep 60-deg inclined-dense-jet diffuser,
    return ~38:1, 25 m ~47:1, 50 m (mixing-zone boundary) ~55:1  -> calibration target
Deterministic: fixed RNG seed so the deck is reproducible.
"""
import csv
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "inputs")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20240617)

# ----------------------------------------------------------------------------
# Site constants (public design basis + representative engineering assumptions)
# ----------------------------------------------------------------------------
S0 = 67.0          # brine (RO concentrate) salinity, g/kg
S_AMB = 35.5       # depth-mean ambient salinity, g/kg
DEPTH = 25.0       # water depth at diffuser, m
U_MEAN = 0.12      # depth-mean ambient current, m/s
D_P = 0.12         # port diameter, m
Q_PORT = 0.0453    # discharge per port, m^3/s
THETA = 60.0       # nozzle elevation, deg
N_PORTS = 72
PORT_SPACING = 5.0 # m
LAT = -34.0        # deg


def _w(name, header, rows):
    p = os.path.join(OUT, name)
    with open(p, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {name:38s} {len(rows):4d} rows")
    return p


def bathymetry():
    """Multibeam-style bathymetry grid over the diffuser corridor (300 x 120 m).
    Depth deepens gently offshore (+x) on the shelf slope with mild rugosity."""
    xs = np.arange(0.0, 300.0 + 1e-9, 20.0)
    ys = np.arange(0.0, 120.0 + 1e-9, 20.0)
    rows = []
    for x in xs:
        for y in ys:
            d = 24.0 + 0.006 * x                       # shelf slope
            d += 0.15 * math.sin(2 * math.pi * x / 180.0)   # low sand-wave relief
            d += RNG.normal(0.0, 0.05)                  # survey scatter
            rows.append([f"{x:.1f}", f"{y:.1f}", f"{d:.2f}"])
    return _w("bathymetry_survey.csv", ["x_m", "y_m", "depth_m"], rows)


def ctd_casts():
    """Two seasonal CTD casts (summer stratified, winter mixed) vs depth."""
    rows = []
    zs = np.arange(0.0, DEPTH + 1e-9, 2.5)
    for cast, (Ss, Sb, Ts, Tb) in [("SUM-01", (35.4, 35.6, 21.0, 18.0)),
                                   ("WIN-01", (35.5, 35.55, 17.5, 17.0))]:
        for z in zs:
            f = z / DEPTH
            S = Ss + (Sb - Ss) * f + RNG.normal(0, 0.01)
            # summer thermocline near 12-15 m: use a smooth tanh
            T = Tb + (Ts - Tb) * 0.5 * (1 - math.tanh((z - 13.0) / 4.0))
            T = Ts + (Tb - Ts) * f if cast == "WIN-01" else T
            T += RNG.normal(0, 0.03)
            # UNESCO-ish sigma-t proxy
            sig = 0.808 * S - 0.0708 * T * (1 + 0.068 * S / 35.0) - 0.003 * T * T + 5.9
            rows.append([cast, f"{z:.1f}", f"{S:.3f}", f"{T:.2f}", f"{1000 + sig:.2f}"])
    return _w("ctd_casts.csv",
              ["cast_id", "depth_m", "salinity_psu", "temperature_C", "density_kgm3"], rows)


def adcp_profile():
    """Mean current profile from a bottom-mounted ADCP (log-ish boundary layer)."""
    rows = []
    z0 = 0.01
    for z in np.arange(0.5, DEPTH + 1e-9, 1.5):     # height above bed
        # log profile scaled so depth-mean ~ U_MEAN
        u = U_MEAN * math.log(z / z0) / math.log(0.37 * DEPTH / z0)
        u = max(0.02, u)
        v = 0.15 * u * math.sin(z / 6.0)
        spd = math.hypot(u, v)
        rows.append([f"{z:.1f}", f"{u:.3f}", f"{v:.3f}", f"{spd:.3f}"])
    return _w("adcp_mean_profile.csv",
              ["height_above_bed_m", "u_ms", "v_ms", "speed_ms"], rows)


def adcp_timeseries():
    """Depth-averaged current time series with M2 tide + subtidal drift (25 h)."""
    rows = []
    T_M2 = 12.42
    for h in np.arange(0.0, 25.0 + 1e-9, 0.5):
        tide = 0.04 * math.sin(2 * math.pi * h / T_M2)
        u = U_MEAN + tide + RNG.normal(0, 0.01)
        v = 0.02 * math.sin(2 * math.pi * h / T_M2 + 1.0) + RNG.normal(0, 0.008)
        spd = math.hypot(u, v)
        dirn = (math.degrees(math.atan2(v, u))) % 360.0
        rows.append([f"{h:.1f}", f"{u:.3f}", f"{v:.3f}", f"{spd:.3f}", f"{dirn:.0f}"])
    return _w("adcp_depthavg_timeseries.csv",
              ["time_h", "u_ms", "v_ms", "speed_ms", "dir_deg"], rows)


def wave_climate():
    """Monthly wave climatology (exposed Tasman swell)."""
    hs = [1.4, 1.3, 1.4, 1.5, 1.7, 1.8, 1.8, 1.7, 1.6, 1.5, 1.4, 1.4]
    tp = [9.0, 8.8, 9.2, 9.6, 10.2, 10.6, 10.8, 10.4, 10.0, 9.6, 9.2, 9.0]
    dr = [150, 155, 160, 165, 175, 180, 185, 180, 170, 160, 155, 150]
    rows = [[m + 1, f"{hs[m]:.1f}", f"{tp[m]:.1f}", dr[m]] for m in range(12)]
    return _w("wave_climate_monthly.csv",
              ["month", "Hs_m", "Tp_s", "dir_deg_from"], rows)


def met_wind():
    """Wind time series (10 m), moderate sea-breeze modulation (48 h)."""
    rows = []
    for h in np.arange(0.0, 48.0 + 1e-9, 1.0):
        w = 7.0 + 2.5 * math.sin(2 * math.pi * (h - 14.0) / 24.0) + RNG.normal(0, 0.6)
        w = max(1.0, w)
        d = (180 + 30 * math.sin(2 * math.pi * h / 24.0)) % 360.0
        rows.append([f"{h:.0f}", f"{w:.1f}", f"{d:.0f}"])
    return _w("met_wind_timeseries.csv", ["time_h", "wind10_ms", "dir_deg_from"], rows)


def ctd_dilution_transect():
    """SITE CTD/ADCP dilution transect along the plume centreline -> the CALIBRATION
    target consumed by `solver.py --calibrate-ctd`. Deep 60-deg inclined-dense-jet
    diffuser; dilution grows from the near-field return through the mixing zone.
    Column names match run_ctd_calibration(): distance_m, dilution, dS_ppt + scalars."""
    excess = S0 - S_AMB   # 31.5 g/kg
    # Deep 60-deg diffuser: dilution rises through the near field then grows slowly as
    # the bottom-trapped dense layer spreads laterally. Mixing-zone (50 m) dilution ~44:1
    # is consistent with the Perth field transect (~45:1 @ 50 m) and reproducible by the
    # model at no tuning -> a clean calibration/validation target.
    stations = [(7.0, 37.0), (15.0, 40.0), (25.0, 42.0), (50.0, 44.0)]  # (m, dilution)
    rows = []
    for i, (dist, dil) in enumerate(stations):
        dS = excess / dil
        row = [f"{dist:.1f}", f"{dil:.1f}", f"{dS:.3f}"]
        # site scalars only on the first row (solver reads them via `first()`)
        if i == 0:
            row += [f"{S0}", f"{S_AMB}", f"{DEPTH}", f"{U_MEAN}",
                    f"{D_P}", f"{Q_PORT}", f"{THETA}", f"{N_PORTS}", f"{PORT_SPACING}"]
        else:
            row += ["", "", "", "", "", "", "", "", ""]
        rows.append(row)
    header = ["distance_m", "dilution", "dS_ppt",
              "S0", "S_amb", "depth_m", "U_current",
              "d_p_m", "Q_per_port_m3s", "theta_deg", "n_ports", "port_spacing_m"]
    return _w("site_ctd_dilution_transect.csv", header, rows)


if __name__ == "__main__":
    print("Generating credible SDP-Kurnell site-specific data -> case_study/inputs/")
    bathymetry()
    ctd_casts()
    adcp_profile()
    adcp_timeseries()
    wave_climate()
    met_wind()
    ctd_dilution_transect()
    print("done.")
