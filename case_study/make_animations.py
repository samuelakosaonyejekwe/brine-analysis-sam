#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_animations.py  --  Generate the GIF animation suite for the SDP case study.

Two families:
  SPATIAL sweeps of the steady production field (case_study/outputs/fields_final.npz):
    anim_depth_slices.gif          plan-view ΔS from surface down to seabed
    anim_cross_sections.gif        vertical x-z ΔS sections swept alongshore (y)
    anim_footprint_threshold.gif   seabed ΔS map with footprint contour, threshold 1.0->0.1
  TIME evolution from a reduced-resolution snapshot run
  (case_study/outputs/_animrun/snapshots/snap_*.npz):
    anim_time_plume.gif            depth-max ΔS plan view vs simulated time

No pure black (dark-teal ink; turbo/plasma/YlOrRd maps). Frames are written with
Pillow (no ffmpeg needed). Output: case_study/outputs/animations/.
"""
import glob
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

INK = "#13343b"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10,
    "text.color": INK, "axes.labelcolor": INK, "axes.titlecolor": INK,
    "axes.edgecolor": INK, "xtick.color": INK, "ytick.color": INK,
    "figure.facecolor": "white", "savefig.facecolor": "white",
})
NAVY = "#0B3D5C"; STAR = "#e63946"; SEA = "#5a3e2b"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
ANIM = os.path.join(OUT, "animations")
os.makedirs(ANIM, exist_ok=True)


def fig_to_img(fig):
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(h, w, 4)
    plt.close(fig)
    return Image.fromarray(buf[:, :, :3].copy())


def save_gif(frames, name, duration=140):
    if not frames:
        print(f"  (skip {name}: no frames)"); return
    p = os.path.join(ANIM, name)
    frames[0].save(p, save_all=True, append_images=frames[1:], loop=0,
                   duration=duration, disposal=2)
    print(f"  gif  {name:34s} {len(frames):3d} frames")


# ---------------------------------------------------------------- production field
d = np.load(os.path.join(OUT, "fields_final.npz"))
x, y, z, fluid, H = d["x"], d["y"], d["z"], d["fluid"], d["H"]
# excess salinity is physically non-negative; clip tiny sub-ambient numerical noise
# to 0 so undisturbed far-field cells render as the darkest map colour, not white NaN.
excess = np.clip(d["excess"], 0.0, None)
S_amb = d["S_amb"]
src = d["src_xyz"]
nx, ny, nz = excess.shape
with open(os.path.join(OUT, "metrics_summary.json")) as f:
    MS = json.load(f)
S0 = MS["config"]["S0"]; dScrit = MS["config"]["dS_crit"]
X, Y = np.meshgrid(x, y, indexing="ij")
zbig = np.where(fluid, z[None, None, :], np.inf)
bottom_k = np.argmin(zbig, axis=2)
x0, y0 = src[0], src[1]
emax = float(excess[fluid].max())

print("Building spatial animations -> outputs/animations/")

# A1 depth-slice sweep (surface -> seabed)
order = np.argsort(-z)      # from shallowest (surface) to deepest
frames = []
for k in order:
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    fld = np.where(fluid[:, :, k], excess[:, :, k], np.nan)
    cf = ax.contourf(X, Y, fld, levels=np.linspace(0, max(emax, 0.2), 20),
                     cmap="turbo", extend="max")
    ax.scatter([x0], [y0], marker="*", s=150, c=STAR, edgecolors=NAVY, zorder=6)
    plt.colorbar(cf, ax=ax, label="ΔS (g/kg)")
    ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
    ax.set_title(f"Excess salinity — horizontal slice at depth {-z[k]:.1f} m")
    fig.tight_layout()
    frames.append(fig_to_img(fig))
save_gif(frames, "anim_depth_slices.gif", duration=200)

# A2 vertical x-z cross-section swept alongshore (y)
Xz, Zz = np.meshgrid(x, z, indexing="ij")
frames = []
for j in range(ny):
    fig, ax = plt.subplots(figsize=(7.8, 3.9))
    ex = np.where(fluid[:, j, :], excess[:, j, :], np.nan)
    cf = ax.contourf(Xz, Zz, ex, levels=np.linspace(0, max(emax, 0.2), 20),
                     cmap="plasma", extend="max")
    ax.fill_between(x, -H[:, j], z.min() - 1, color=SEA, zorder=4)
    ax.axvline(x0, color=NAVY, ls=":", lw=1)
    plt.colorbar(cf, ax=ax, label="ΔS (g/kg)")
    ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("z — elevation (m)")
    ax.set_ylim(z.min() - 1, 1)
    ax.set_title(f"Vertical section — alongshore offset {y[j]-y0:+.0f} m")
    fig.tight_layout()
    frames.append(fig_to_img(fig))
# ping-pong so the sweep returns
save_gif(frames + frames[::-1], "anim_cross_sections.gif", duration=130)

# A3 seabed footprint vs sweeping threshold
sb = np.take_along_axis(excess, bottom_k[:, :, None], axis=2)[:, :, 0]
frames = []
for thr in np.round(np.arange(1.0, 0.09, -0.05), 2):
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    cf = ax.contourf(X, Y, sb, levels=np.linspace(0, max(emax, 0.2), 20),
                     cmap="turbo", extend="max")
    area = float((sb > thr).sum() * MS["config"]["dx"] * MS["config"]["dy"])
    cs = ax.contour(X, Y, sb, levels=[thr], colors=[NAVY], linewidths=2.0)
    ax.scatter([x0], [y0], marker="*", s=150, c=STAR, edgecolors=NAVY, zorder=6)
    plt.colorbar(cf, ax=ax, label="seabed ΔS (g/kg)")
    ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
    ax.set_title(f"Seabed footprint — threshold ΔS = {thr:.2f} g/kg  →  {area:.0f} m²")
    fig.tight_layout()
    frames.append(fig_to_img(fig))
save_gif(frames, "anim_footprint_threshold.gif", duration=220)

# ---------------------------------------------------------------- time evolution
snaps = sorted(glob.glob(os.path.join(OUT, "_animrun", "snapshots", "snap_*.npz")))
if len(snaps) >= 25:
    print(f"Building time-evolution animation from {len(snaps)} snapshots ...")
    # reconstruct coarse-run plan axes
    with open(os.path.join(OUT, "_animrun", "metrics_summary.json")) as f:
        cc = json.load(f)["config"]
    cnx, cny = cc["nx"], cc["ny"]
    cx = (np.arange(cnx) + 0.5) * (cc["Lx"] / cnx)
    cy = (np.arange(cny) + 0.5) * (cc["Ly"] / cny)
    CX, CY = np.meshgrid(cx, cy, indexing="ij")
    # global colour scale from the last frame
    last = np.clip(np.load(snaps[-1])["excess"], 0.0, None)
    vmax = max(float(np.nanpercentile(last.max(axis=2), 99)), 0.3)
    frames = []
    for sp in snaps:
        z0 = np.load(sp)
        pv = np.clip(z0["excess"], 0.0, None).max(axis=2)   # depth-max ΔS (plan view)
        fig, ax = plt.subplots(figsize=(7.6, 3.9))
        cf = ax.contourf(CX, CY, pv, levels=np.linspace(0, vmax, 20),
                         cmap="turbo", extend="max")
        ax.scatter([cc["Lx"] * cc["x_src_frac"]], [cc["Ly"] * cc["y_src_frac"]],
                   marker="*", s=150, c=STAR, edgecolors=NAVY, zorder=6)
        plt.colorbar(cf, ax=ax, label="depth-max ΔS (g/kg)")
        ax.set_xlabel("x — cross-shelf (m)"); ax.set_ylabel("y — alongshore (m)")
        ax.set_title(f"Plume development — t = {float(z0['t']):.0f} s")
        fig.tight_layout()
        frames.append(fig_to_img(fig))
    save_gif(frames, "anim_time_plume.gif", duration=140)
else:
    print("  (no snapshot run found — skipping time-evolution animation)")

print("animations complete.")
