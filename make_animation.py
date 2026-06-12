#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_animation.py — build a high-resolution time-lapse animation (GIF) of the
NEREID-B brine plume from a --snapshots run.

Three synchronized panels (fixed colour scales, light spatial smoothing):
    A  seabed plan-view excess salinity ΔS
    B  vertical section through the outfall ΔS, with the validated near-field
       jet trajectory overlaid (the near field the 3-D grid does not resolve)
    C  free-surface elevation η (rigid lid removed)

Reads:
    <outdir>/fields_final.npz       grid coords (x,y,z,fluid,H,src_xyz)
    <outdir>/metrics_summary.json   config (for the near-field overlay)
    <outdir>/snapshots/snap_*.npz   per-frame fields (t,S,excess,u,w,eta)

Writes:
    <outdir>/plume_evolution.gif

Usage:
    python3 make_animation.py [outdir]          (default outdir: nereid_anim)
"""
import glob
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

try:
    from scipy.ndimage import gaussian_filter
except Exception:
    gaussian_filter = None

SIGMA = 0.8        # light smoothing (cells) to suppress speckle for presentation

outdir = sys.argv[1] if len(sys.argv) > 1 else "nereid_anim"
outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), outdir)


def smooth(a):
    return gaussian_filter(a, SIGMA, mode="nearest") if gaussian_filter else a


# ---- grid ----
g = np.load(os.path.join(outdir, "fields_final.npz"))
xc, yc, zc = g["x"], g["y"], g["z"]
fluid = g["fluid"]; H = g["H"]
nx, ny, nz = fluid.shape
klow = np.argmax(fluid, axis=2)                 # lowest fluid cell per column

# ---- frames ----
snaps = sorted(glob.glob(os.path.join(outdir, "snapshots", "snap_*.npz")))
if not snaps:
    raise SystemExit(f"No snapshots in {outdir}/snapshots (run with --snapshots N)")
frames = [np.load(s) for s in snaps]
times = [float(f["t"]) for f in frames]


def seabed(ex):
    return np.take_along_axis(ex, klow[:, :, None], axis=2)[:, :, 0]


# ---- colour scales (global, no flicker) ----
vmax = max(1e-3, max(np.nanmax(f["excess"]) for f in frames))
emax = max(1e-3, max(np.nanmax(np.abs(f["eta"])) for f in frames if "eta" in f.files))

# ---- vertical-section row = the injection (return-point) column ----
if "src_xyz" in g.files:
    sx, sy = float(g["src_xyz"][0]), float(g["src_xyz"][1])
    i_src = int(np.argmin(np.abs(xc - sx))); j0 = int(np.argmin(np.abs(yc - sy)))
else:
    agg = sum(seabed(f["excess"]) for f in frames)
    i_src, j0 = map(int, np.unravel_index(np.nanargmax(agg), agg.shape))

# ---- near-field trajectory overlay (recomputed from the saved config) ----
nf_arc = None
try:
    cfgd = json.load(open(os.path.join(outdir, "metrics_summary.json")))["config"]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from solver import nearfield_jet, equation_of_state, Config
    cfg = Config()
    for k, v in cfgd.items():
        if hasattr(cfg, k):
            setattr(cfg, k, v)
    U_d = cfg.Q_d / (np.pi * (cfg.d_p / 2) ** 2)
    rho_amb = equation_of_state(cfg, cfg.S_amb_bot, cfg.T_amb_bot)
    rho_b = equation_of_state(cfg, cfg.S0, cfg.T_b)
    gp0 = cfg.g * (rho_amb - rho_b) / rho_amb
    nf = nearfield_jet(U_d, cfg.d_p, gp0, cfg.theta_deg, alpha=cfg.entrain_alpha)
    nx0 = cfg.x_src_frac * cfg.Lx
    Hn = float(np.clip(cfg.bathy_min_depth + cfg.bathy_slope * nx0, 1.0, cfg.depth))
    nz0 = -Hn + cfg.nozzle_height
    tr = np.array(nf["trajectory"])
    nf_arc = (nx0 + tr[:, 0], nz0 + tr[:, 1], nx0, nz0)
except Exception as e:
    print(f"(near-field overlay skipped: {e})")

# ---- figure (3 panels, high resolution) ----
fig, (axA, axB, axC) = plt.subplots(1, 3, figsize=(21, 5.4))
lvE = np.linspace(0, vmax, 25)
lvH = np.linspace(-emax, emax, 25)


def draw(fi):
    for ax in (axA, axB, axC):
        ax.clear()
    fr = frames[fi]
    ex = fr["excess"]
    # A: seabed plan view (smoothed)
    sb = smooth(seabed(ex))
    cfA = axA.contourf(xc, yc, sb.T, levels=lvE, cmap="viridis", extend="max")
    axA.scatter([xc[i_src]], [yc[j0]], c="red", marker="*", s=130, edgecolors="k", zorder=5)
    axA.set(xlabel="x (m)", ylabel="y (m)",
            title=f"Seabed excess ΔS (g/kg)    t = {times[fi]:6.1f} s")
    # B: vertical section through injection (smoothed) + near-field arc
    sec = smooth(ex[:, j0, :])
    sec = np.ma.masked_where(~fluid[:, j0, :], sec)
    cfB = axB.contourf(xc, zc, sec.T, levels=lvE, cmap="magma", extend="max")
    axB.fill_between(xc, -H[:, j0], zc[0] - 1, color="0.4", zorder=4)
    axB.plot(xc, -H[:, j0], "k-", lw=1.2)
    if nf_arc is not None:
        # clip the (deep-water) near-field arc to the water column; where it
        # exceeds the local depth the jet impinges the surface (shallow site)
        az = np.where(nf_arc[1] <= 0.02, nf_arc[1], np.nan)
        axB.plot(nf_arc[0], az, "--", color="deepskyblue", lw=1.8, zorder=6)
        axB.scatter([nf_arc[2]], [nf_arc[3]], c="lime", marker="^", s=70,
                    edgecolors="k", zorder=7)        # nozzle
    axB.scatter([xc[i_src]], [zc[klow[i_src, j0]]], c="cyan", marker="v", s=70,
                edgecolors="k", zorder=7)            # 3-D injection (return) point
    axB.set(xlabel="x (m)", ylabel="z (m)", ylim=(zc[0], 0.5),
            title=f"Vertical section + near-field jet    t = {times[fi]:6.1f} s")
    # C: free-surface elevation (smoothed)
    eta = smooth(fr["eta"]) if "eta" in fr.files else np.zeros((nx, ny))
    cfC = axC.contourf(xc, yc, eta.T, levels=lvH, cmap="RdBu_r", extend="both")
    axC.scatter([xc[i_src]], [yc[j0]], c="k", marker="*", s=110, zorder=5)
    axC.set(xlabel="x (m)", ylabel="y (m)",
            title=f"Free-surface elevation η (m)    t = {times[fi]:6.1f} s")
    return cfA, cfB, cfC


cf0 = draw(0)
fig.colorbar(cf0[0], ax=axA, label="ΔS (g/kg)")
fig.colorbar(cf0[1], ax=axB, label="ΔS (g/kg)")
fig.colorbar(cf0[2], ax=axC, label="η (m)")
fig.tight_layout()

ani = FuncAnimation(fig, draw, frames=len(frames), interval=120, blit=False)
out = os.path.join(outdir, "plume_evolution.gif")
ani.save(out, writer=PillowWriter(fps=10), dpi=130)
plt.close(fig)
print(f"Wrote {out}  ({len(frames)} frames, ΔS_max={vmax:.2f} g/kg, "
      f"η_max={emax:.2f} m, section row j={j0}, smoothing σ={SIGMA} cells, "
      f"near-field overlay={'yes' if nf_arc is not None else 'no'})")
