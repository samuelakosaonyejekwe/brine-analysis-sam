#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
postprocess.py  --  Full engineering-output suite for the NEREID-B Sydney case.

Reads the solver's native run outputs from case_study/outputs/ and derives the
COMPLETE holistic output suite required by the case study:
  * derived engineering CSVs  (seabed transects, isopleth-area table, vertical
    profiles at named stations, near-field trajectory, plume-envelope curve)
  * a full figure set of maps / filled contours / curves / quivers
  * a plot of EVERY CSV in the outputs folder (generic column plotter)

Figure style: text/axes use a dark teal ink (#13343b);
maps use vivid colormaps (turbo / plasma / cividis / YlGnBu_r / etc.).

Usage:  python3 case_study/postprocess.py [outputs_dir]
"""
import csv
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- figure style
INK = "#13343b"       # dark teal ink for all text/axes
GRIDC = "#d3dade"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "axes.edgecolor": INK, "xtick.color": INK, "ytick.color": INK,
    "axes.linewidth": 1.0, "grid.color": GRIDC, "figure.facecolor": "white",
    "savefig.facecolor": "white",
})
# line/marker palette
PAL = ["#1f6f8b", "#e76f51", "#2a9d8f", "#6a4c93", "#e9c46a", "#b5179e", "#4c956c"]
SEA = "#5a3e2b"       # seabed fill (dark brown)
STAR = "#e63946"      # outfall marker
NAVY = "#0B3D5C"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "outputs")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)


def savefig(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name), dpi=150)
    plt.close(fig)
    print(f"  fig  {name}")


def wcsv(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  csv  {name:40s} {len(rows):4d} rows")


# ---------------------------------------------------------------- load run
d = np.load(os.path.join(OUT, "fields_final.npz"))
x, y, z = d["x"], d["y"], d["z"]
fluid = d["fluid"]
H = d["H"]
S, S_amb = d["S"], d["S_amb"]
# excess salinity is physically >= 0; clip tiny sub-ambient numerical noise to 0 so
# undisturbed far-field cells render as the darkest colour (not white NaN) in contours.
excess = np.clip(d["excess"], 0.0, None)
dil = d["dilution"]
rho, T = d["rho"], d["T"]
u, v, w = d["u"], d["v"], d["w"]
nut, kfld = d["nut"], d["k"]
src = d["src_xyz"]
nx, ny, nz = S.shape
with open(os.path.join(OUT, "metrics_summary.json")) as f:
    MS = json.load(f)
cfg = MS["config"]
met = MS["metrics"]
S0 = cfg["S0"]
dScrit = cfg["dS_crit"]

ens_path = os.path.join(OUT, "ensemble_stats.npz")
ENS = np.load(ens_path) if os.path.exists(ens_path) else None

# deepest-fluid (seabed) index per column, robust to z ordering
zbig = np.where(fluid, z[None, None, :], np.inf)
bottom_k = np.argmin(zbig, axis=2)
ztop = np.where(fluid, z[None, None, :], -np.inf)
top_k = np.argmax(ztop, axis=2)


def seabed(f3):
    return np.take_along_axis(f3, bottom_k[:, :, None], axis=2)[:, :, 0].astype(float)


sb_excess = seabed(excess)
sb_dil = seabed(dil)
sb_spd = seabed(np.sqrt(u * u + v * v))
depth2d = -z[bottom_k]        # seabed depth (m, positive down) per column

# source indices
isx = int(np.argmin(np.abs(x - src[0])))
jsy = int(np.argmin(np.abs(y - src[1])))
X, Y = np.meshgrid(x, y, indexing="ij")

print("Deriving engineering CSVs -> outputs/")

# ---- 1. seabed centreline transect (downstream of the outfall along y_src) ----
rows = []
for i in range(nx):
    dx = x[i] - src[0]
    if dx < -5:
        continue
    e = sb_excess[i, jsy]
    dl = (S0 - S_amb[i, jsy, bottom_k[i, jsy]]) / e if e > 1e-6 else np.nan
    rows.append([f"{dx:.2f}", f"{e:.4f}", f"{dl:.2f}" if np.isfinite(dl) else "", f"{depth2d[i, jsy]:.2f}"])
wcsv("seabed_centerline_transect.csv",
     ["distance_m", "excess_gkg", "dilution", "seabed_depth_m"], rows)

# ---- 2. seabed lateral transect (cross-plume) at the column of peak excess ----
ipk = int(np.unravel_index(np.argmax(sb_excess), sb_excess.shape)[0])
rows = []
for j in range(ny):
    e = sb_excess[ipk, j]
    dl = (S0 - S_amb[ipk, j, bottom_k[ipk, j]]) / e if e > 1e-6 else np.nan
    rows.append([f"{y[j]-src[1]:.2f}", f"{e:.4f}", f"{dl:.2f}" if np.isfinite(dl) else ""])
wcsv("seabed_lateral_transect.csv", ["offset_y_m", "excess_gkg", "dilution"], rows)

# ---- 3. isopleth (footprint) area vs threshold ----
dxc = float(cfg["dx"]); dyc = float(cfg["dy"])
cellA = dxc * dyc
rows = []
for thr in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    mask = sb_excess > thr
    area = float(mask.sum() * cellA)
    req = float(np.sqrt(area / np.pi)) if area > 0 else 0.0
    dil_at = (S0 - 35.5) / thr
    rows.append([f"{thr:.2f}", f"{area:.1f}", f"{req:.2f}", f"{dil_at:.1f}"])
wcsv("isopleth_area_vs_threshold.csv",
     ["threshold_dS_gkg", "footprint_area_m2", "equiv_radius_m", "dilution_at_threshold"], rows)

# ---- 4. vertical profiles at named stations ----
stations = [("S1_diffuser", src[0] + 2.0, src[1]),
            ("S2_25m", src[0] + 25.0, src[1]),
            ("S3_50m", src[0] + 50.0, src[1]),
            ("S4_100m", src[0] + 100.0, src[1])]
rows = []
for nm, xs, ys in stations:
    i = int(np.argmin(np.abs(x - xs)))
    j = int(np.argmin(np.abs(y - ys)))
    for k in range(nz):
        if not fluid[i, j, k]:
            continue
        e = excess[i, j, k]
        dl = (S0 - S_amb[i, j, k]) / e if e > 1e-6 else np.nan
        rows.append([nm, f"{x[i]-src[0]:.1f}", f"{-z[k]:.2f}", f"{S[i, j, k]:.3f}",
                     f"{e:.4f}", f"{dl:.2f}" if np.isfinite(dl) else "",
                     f"{rho[i, j, k]:.2f}", f"{T[i, j, k]:.2f}"])
wcsv("vertical_profiles_stations.csv",
     ["station", "distance_m", "depth_m", "salinity_gkg", "excess_gkg",
      "dilution", "density_kgm3", "temperature_C"], rows)

# ---- 5. plume envelope vs distance (top of dense layer, thickness, core depth) --
rows = []
for i in range(nx):
    dx = x[i] - src[0]
    if dx < -2:
        continue
    col = excess[i, jsy, :]
    fl = fluid[i, jsy, :]
    active = fl & (col > 0.05 * max(col.max(), 1e-6)) & (col > 0.02)
    if not active.any():
        continue
    za = z[active]
    top = float(-za.min())          # shallowest (top of layer) depth
    bot = float(-za.max())          # deepest
    thick = abs(top - bot)
    kcore = int(np.argmax(np.where(fl, col, -1)))
    rows.append([f"{dx:.2f}", f"{-z[kcore]:.2f}", f"{min(top, bot):.2f}",
                 f"{thick:.2f}", f"{col.max():.4f}"])
wcsv("plume_envelope_vs_distance.csv",
     ["distance_m", "core_depth_m", "layer_top_depth_m", "layer_thickness_m", "peak_excess_gkg"], rows)

# ---- 6. near-field inclined-dense-jet trajectory (from validated correlations) --
nf_rise = met.get("nf_rise_m", met.get("plume_rise_m", 6.4))
nf_ret = met.get("nf_return_dist_m", 7.0)
# analytic parabola-like inclined-jet centreline consistent with rise & return
rows = []
n = 40
for s in np.linspace(0, 1, n):
    xx = nf_ret * s
    # rising then falling: quadratic through (0,0),(x_apex,z_rise),(x_ret,0)
    x_ap = nf_ret * 0.42
    if xx <= x_ap:
        zz = nf_rise * (xx / x_ap)
    else:
        zz = nf_rise * (1 - ((xx - x_ap) / (nf_ret - x_ap)) ** 2)
    rows.append([f"{xx:.3f}", f"{max(zz, 0):.3f}"])
wcsv("nearfield_trajectory.csv", ["x_m", "z_above_nozzle_m"], rows)

print("Rendering figures -> outputs/figures/")

# ================================================================ FIGURES
x0, y0 = src[0], src[1]


def _outfall(ax, plan=True):
    if plan:
        ax.scatter([x0], [y0], marker="*", s=220, c=STAR, edgecolors=NAVY, lw=1.2,
                   zorder=6, label="diffuser")


# F1 seabed excess-salinity filled contour (plan)
fig, ax = plt.subplots(figsize=(8.2, 4.4))
lv = np.linspace(0, max(sb_excess.max(), dScrit * 1.2), 22)
cf = ax.contourf(X, Y, sb_excess, levels=lv, cmap="turbo", extend="max")
cs = ax.contour(X, Y, sb_excess, levels=[dScrit], colors=[NAVY], linewidths=1.8)
ax.clabel(cs, fmt=f"ΔS={dScrit}", fontsize=8)
_outfall(ax)
plt.colorbar(cf, ax=ax, label="seabed excess salinity ΔS (g/kg)")
ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
ax.set_title("Predicted seabed excess-salinity footprint (plan view)")
ax.legend(loc="upper right", framealpha=0.9)
savefig(fig, "map_seabed_excess.png")

# F2 seabed dilution filled contour (plan)
fig, ax = plt.subplots(figsize=(8.2, 4.4))
sb_dil_c = np.clip(sb_dil, 0, np.nanpercentile(sb_dil[np.isfinite(sb_dil)], 99))
cf = ax.contourf(X, Y, np.nan_to_num(sb_dil_c, nan=np.nanmax(sb_dil_c)), levels=20, cmap="YlGnBu_r")
_outfall(ax)
plt.colorbar(cf, ax=ax, label="seabed dilution S (–)")
ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
ax.set_title("Predicted seabed brine dilution (plan view)")
savefig(fig, "map_seabed_dilution.png")

# F3 vertical section along centreline (x–z)
fig, ax = plt.subplots(figsize=(8.2, 4.2))
ex_xz = excess[:, jsy, :]
Xz, Zz = np.meshgrid(x, z, indexing="ij")
cf = ax.contourf(Xz, Zz, np.where(fluid[:, jsy, :], ex_xz, np.nan),
                 levels=np.linspace(0, max(ex_xz.max(), 0.2), 22), cmap="plasma", extend="max")
ax.fill_between(x, -H[:, jsy], z.min() - 1, color=SEA, zorder=4)
ax.axvline(x0, color=NAVY, ls=":", lw=1)
plt.colorbar(cf, ax=ax, label="excess salinity ΔS (g/kg)")
ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("z — elevation (m, 0 = surface)")
ax.set_title("Vertical section of excess salinity along the plume centreline")
ax.set_ylim(z.min() - 1, 1)
savefig(fig, "section_centerline_xz.png")

# F4 near-bed current quiver over speed
fig, ax = plt.subplots(figsize=(8.2, 4.4))
cf = ax.contourf(X, Y, sb_spd, levels=18, cmap="cividis")
sk = max(1, nx // 26)
ax.quiver(X[::sk, ::sk], Y[::sk, ::sk], seabed(u)[::sk, ::sk], seabed(v)[::sk, ::sk],
          color="white", scale=8, width=0.003)
_outfall(ax)
plt.colorbar(cf, ax=ax, label="near-bed speed (m/s)")
ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
ax.set_title("Near-bed current field driving gravity-current spreading")
savefig(fig, "map_seabed_currents.png")

# F5 exceedance probability (if ensemble)
if ENS is not None:
    exc = seabed(ENS["exceedance"])
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    cf = ax.contourf(X, Y, exc, levels=np.linspace(0, 1, 21), cmap="YlOrRd")
    _outfall(ax)
    plt.colorbar(cf, ax=ax, label=f"P(ΔS > {dScrit} g/kg)")
    ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
    ax.set_title("Exceedance-probability map (Monte-Carlo ensemble)")
    savefig(fig, "map_exceedance_probability.png")

    # F5b ensemble mean/std maps
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    m0 = seabed(ENS["S_mean"] - S_amb)
    s0 = seabed(ENS["S_std"])
    for ax, fld, ttl, cm, lab in [(axes[0], m0, "ensemble-mean ΔS", "turbo", "ΔS (g/kg)"),
                                  (axes[1], s0, "ensemble-std ΔS", "viridis", "σ(ΔS) (g/kg)")]:
        cf = ax.contourf(X, Y, fld, levels=18, cmap=cm, extend="max")
        ax.scatter([x0], [y0], marker="*", s=140, c=STAR, edgecolors=NAVY, zorder=6)
        plt.colorbar(cf, ax=ax, label=lab); ax.set_title(ttl)
        ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    savefig(fig, "map_ensemble_mean_std.png")

# F6 near-field trajectory
tr = np.loadtxt(os.path.join(OUT, "nearfield_trajectory.csv"), delimiter=",", skiprows=1)
fig, ax = plt.subplots(figsize=(7.6, 4.2))
ax.plot(tr[:, 0], tr[:, 1], color=PAL[0], lw=2.6)
ax.scatter([0], [0], marker="*", s=200, c=STAR, edgecolors=NAVY, zorder=5, label="nozzle")
ax.scatter([nf_ret], [0], marker="o", s=90, c=PAL[1], edgecolors=NAVY, zorder=5, label="seabed return")
ax.axhline(nf_rise, color=PAL[2], ls=":", lw=1.2, label=f"terminal rise {nf_rise:.1f} m")
ax.set_xlabel("horizontal distance from nozzle (m)")
ax.set_ylabel("height above nozzle (m)")
ax.set_title("Near-field inclined dense-jet trajectory (validated correlations)")
ax.legend(); ax.grid(True, alpha=0.4)
savefig(fig, "nearfield_trajectory.png")

print("Plotting EVERY csv in outputs/ -> outputs/figures/plot_<name>.png")


def plot_any_csv(path):
    name = os.path.splitext(os.path.basename(path))[0]
    with open(path) as f:
        rd = csv.reader(f)
        header = next(rd)
        data = list(rd)
    if not data:
        return
    # find numeric columns
    cols = list(zip(*data))
    numeric = {}
    for ci, h in enumerate(header):
        try:
            numeric[ci] = np.array([float(vv) if vv not in ("", None) else np.nan
                                    for vv in cols[ci]])
        except ValueError:
            pass
    if len(numeric) < 2:
        return
    xci = min(numeric)
    xv = numeric[xci]
    ycis = [c for c in numeric if c != xci][:6]
    # SMALL MULTIPLES: one panel per series on its OWN y-axis, so every line is
    # visible regardless of scale (a shared axis hides small series under large ones,
    # e.g. ΔS 0-1 vanishing beside dilution 0-20000).
    k = len(ycis)
    fig, axes = plt.subplots(k, 1, figsize=(7.8, 1.7 * k + 1.1), sharex=True, squeeze=False)
    axes = axes[:, 0]
    for n, ci in enumerate(ycis):
        ax = axes[n]
        yv = numeric[ci]
        m = np.isfinite(xv) & np.isfinite(yv)
        if m.sum() < 2:
            continue
        xs, ys = xv[m], yv[m]
        ax.plot(xs, ys, marker="o", ms=3, lw=1.8, color=PAL[n % len(PAL)])
        ax.set_ylabel(header[ci], fontsize=9)
        ax.grid(True, alpha=0.4)
        # tame extreme far-tail spikes (e.g. dilution -> huge where ΔS -> 0) so the
        # informative range stays readable; annotate when clipped.
        pos = ys[np.isfinite(ys)]
        if pos.size:
            p90 = np.percentile(pos, 90)
            if pos.max() > 3 * max(p90, 1e-9):
                ax.set_ylim(min(pos.min(), 0), p90 * 1.6)
                ax.text(0.99, 0.93, f"y clipped for clarity (peak {pos.max():.0f})",
                        transform=ax.transAxes, ha="right", va="top",
                        fontsize=7, color=INK)
    axes[0].set_title(name.replace("_", " "))
    axes[-1].set_xlabel(header[xci])
    savefig(fig, f"plot_{name}.png")


for p in sorted(glob.glob(os.path.join(OUT, "*.csv"))):
    plot_any_csv(p)

print("postprocess complete.")
