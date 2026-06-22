"""
cad_lib.py  --  Lightweight CAD sheet / dimensioning engine (matplotlib)
Produces A3-landscape engineering drawing sheets with border, title block,
ISO dimension lines, graphic scale bars, north arrows, hatching and leaders.
Used by build_dwg_docx.py for the SDP / NEREID-B marine-outfall drawing set.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Polygon, Circle, Ellipse, PathPatch, Arc
from matplotlib.path import Path
import matplotlib.font_manager as fm
import numpy as np

# ---- global style: clean technical sans -------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.linewidth": 0.8,
    "lines.antialiased": True,
    "path.simplify": True,
})

INK   = "#101418"     # primary line ink
INK2  = "#3a4148"     # secondary / thin
ACCENT= "#0B3D5C"     # project navy (matches report)
WATER = "#D9ECF6"     # sea tint
WATER2= "#BFE0F0"
GROUND= "#E7DCC6"     # soil tint
ROCK  = "#CFC4AC"
CONC  = "#C8CCD0"     # concrete fill
PLUME = "#F2C9C2"     # brine plume tint
PLUME2= "#E79A8C"
GRID  = "#9aa3ab"

SHEET_W, SHEET_H = 420.0, 297.0      # A3 landscape, mm

# ============================================================================
#  SHEET FRAME + TITLE BLOCK
# ============================================================================
def new_sheet(title, dwg_no, scale, sheet_no="1 OF 1", rev="0"):
    """Create an A3 landscape sheet. Returns (fig, sheet_ax)."""
    fig = plt.figure(figsize=(16.54, 11.69), dpi=170)
    sax = fig.add_axes([0, 0, 1, 1])
    sax.set_xlim(0, SHEET_W); sax.set_ylim(0, SHEET_H)
    sax.set_aspect("equal"); sax.axis("off")

    # twin borders
    sax.add_patch(Rectangle((7, 7), SHEET_W-14, SHEET_H-14, fill=False, lw=2.2, ec=INK))
    sax.add_patch(Rectangle((11, 11), SHEET_W-22, SHEET_H-22, fill=False, lw=0.7, ec=INK))

    _title_block(sax, title, dwg_no, scale, sheet_no, rev)
    return fig, sax


def _tb_text(ax, x, y, s, size=8, bold=False, color=INK, ha="left", va="bottom"):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va,
            fontweight=("bold" if bold else "normal"))


def _title_block(ax, title, dwg_no, scale, sheet_no, rev):
    # title block bottom-right
    tbw, tbh = 168.0, 50.0
    x0, y0 = SHEET_W-11-tbw, 11
    ax.add_patch(Rectangle((x0, y0), tbw, tbh, fill=False, lw=1.3, ec=INK))

    # left identity strip
    sw = 40.0
    ax.add_patch(Rectangle((x0, y0), sw, tbh, fill=True, fc=ACCENT, ec=INK, lw=1.0))
    _tb_text(ax, x0+sw/2, y0+tbh-9, "NEREID‑B", size=13, bold=True,
             color="white", ha="center", va="center")
    _tb_text(ax, x0+sw/2, y0+tbh-19, "Brine Outfall", size=7.5, color="#cfe3f0",
             ha="center", va="center")
    _tb_text(ax, x0+sw/2, y0+tbh-26, "Modelling Suite", size=7.5, color="#cfe3f0",
             ha="center", va="center")
    _tb_text(ax, x0+sw/2, y0+9, "A.S. ONYEJEKWE", size=6.3, color="white",
             ha="center", va="center")
    _tb_text(ax, x0+sw/2, y0+5, "Env. Fluid Mechanics", size=5.6, color="#cfe3f0",
             ha="center", va="center")

    # ruled rows in main panel
    px = x0+sw
    pw = tbw-sw
    # horizontal rules
    ax.plot([px, px+pw], [y0+tbh-13, y0+tbh-13], color=INK, lw=0.8)
    ax.plot([px, px+pw], [y0+tbh-24, y0+tbh-24], color=INK, lw=0.7)
    ax.plot([px, px+pw], [y0+16, y0+16], color=INK, lw=0.7)
    # vertical rules in lower band
    c1 = px + pw*0.42
    c2 = px + pw*0.70
    ax.plot([c1, c1], [y0, y0+16], color=INK, lw=0.7)
    ax.plot([c2, c2], [y0, y0+16], color=INK, lw=0.7)
    ax.plot([px, px], [y0, y0+tbh], color=INK, lw=0.8)

    # project / client
    _tb_text(ax, px+3, y0+tbh-6.5, "PROJECT", size=5.6, color=INK2)
    _tb_text(ax, px+3, y0+tbh-11.5, "Sydney Desalination Plant — Kurnell, NSW", size=8, bold=True)
    _tb_text(ax, px+3, y0+tbh-20, "Offshore Submerged Multiport Brine Diffuser — Tasman Shelf",
             size=6.6, color=INK2)

    # drawing title
    _tb_text(ax, px+3, y0+18.5, "DRAWING TITLE", size=5.6, color=INK2)
    for i, line in enumerate(_wrap(title, 46)):
        _tb_text(ax, px+3, y0+13.5-i*4.6, line, size=8.2, bold=True)

    # bottom data cells
    _tb_text(ax, px+3, y0+11.5, "SCALE (A3)", size=5.4, color=INK2)
    _tb_text(ax, px+3, y0+4.5, scale, size=7.4, bold=True)
    _tb_text(ax, c1+3, y0+11.5, "DRAWING No.", size=5.4, color=INK2)
    _tb_text(ax, c1+3, y0+4.5, dwg_no, size=7.4, bold=True, color=ACCENT)
    _tb_text(ax, c2+3, y0+11.5, "REV", size=5.4, color=INK2)
    _tb_text(ax, c2+3, y0+4.5, rev, size=7.4, bold=True)
    _tb_text(ax, c2+pw*0.15, y0+11.5, "SHEET", size=5.4, color=INK2)
    _tb_text(ax, c2+pw*0.15, y0+4.5, sheet_no, size=6.6, bold=True)
    # date strip (top right corner of panel)
    _tb_text(ax, px+pw-2, y0+tbh-6.5, "DATE  2026‑06‑18", size=6.2,
             color=INK2, ha="right")
    _tb_text(ax, px+pw-2, y0+tbh-20, "STATUS  ISSUED FOR DESIGN", size=6.0,
             color=INK2, ha="right")

    # revision note strip above title block
    ax.add_patch(Rectangle((x0, y0+tbh), tbw, 6.5, fill=False, lw=0.7, ec=INK))
    _tb_text(ax, x0+2, y0+tbh+3.2, "REV 0  —  ISSUED FOR DESIGN  —  2026‑06‑18",
             size=5.8, color=INK2, va="center")
    _tb_text(ax, x0+tbw-2, y0+tbh+3.2,
             "Indicative — derived from NEREID‑B simulation (public design basis)",
             size=5.6, color=INK2, va="center", ha="right")


def _wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if len(cur)+len(w)+1 <= n:
            cur = (cur+" "+w).strip()
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out[:2]


def sheet_note(ax, lines, x=14, y=None, title="NOTES:", w=78):
    """General notes block (sheet-mm coords)."""
    if y is None:
        y = 11
    _tb_text(ax, x, y+ (len(lines)*3.6)+5, title, size=7, bold=True, color=ACCENT)
    for i, ln in enumerate(lines):
        for j, sub in enumerate(_wrap_n(ln, w)):
            _tb_text(ax, x+(0 if j == 0 else 4), y+(len(lines)-i)*3.6 - j*3.2,
                     sub, size=5.9, color=INK2)


def _wrap_n(s, n):
    out, cur = [], ""
    for w in s.split():
        if len(cur)+len(w)+1 <= n:
            cur = (cur+" "+w).strip()
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out


# ============================================================================
#  DRAWING AREA (real-world coordinates inside the sheet)
# ============================================================================
def add_area(fig, x_mm, y_mm, w_mm, h_mm):
    """Add an inset axes positioned in sheet-mm; returns a clean equal-aspect ax."""
    ax = fig.add_axes([x_mm/SHEET_W, y_mm/SHEET_H, w_mm/SHEET_W, h_mm/SHEET_H])
    ax.set_aspect("equal")
    ax.axis("off")
    return ax


def view_label(ax, text, sub=None, loc="lower"):
    """Underlined view title in data coords (placed via axes fraction)."""
    y = -0.04 if loc == "lower" else 1.03
    t = ax.text(0.5, y, text, transform=ax.transAxes, fontsize=10.5,
                fontweight="bold", color=INK, ha="center", va="top")
    ax.plot([0.30, 0.70], [y-0.035, y-0.035], transform=ax.transAxes,
            color=INK, lw=1.0)
    if sub:
        ax.text(0.5, y-0.05, sub, transform=ax.transAxes, fontsize=7.5,
                color=INK2, ha="center", va="top", style="italic")


# ============================================================================
#  DIMENSIONING (data coords)
# ============================================================================
def _arrow(ax, p1, p2, color=INK, lw=0.8):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                mutation_scale=8, shrinkA=0, shrinkB=0))


def hdim(ax, x1, x2, y, text, ext_to=None, off=0.0, tick=None, txt_dy=None,
         color=INK, fs=7.5, above=True):
    """Horizontal dimension between x1,x2 at level y (+off)."""
    yl = y + off
    if tick is None:
        tick = abs(x2-x1)*0.02 + (ax.get_xlim()[1]-ax.get_xlim()[0])*0.004
    # extension lines
    base = ext_to if ext_to is not None else y
    ax.plot([x1, x1], [base, yl + (tick if above else -tick)], color=color, lw=0.5)
    ax.plot([x2, x2], [base, yl + (tick if above else -tick)], color=color, lw=0.5)
    # dimension line with double arrows
    _arrow(ax, (x1, yl), (x2, yl), color=color)
    _arrow(ax, (x2, yl), (x1, yl), color=color)
    if txt_dy is None:
        txt_dy = tick*0.8
    ax.text((x1+x2)/2, yl+txt_dy, text, ha="center", va="bottom",
            fontsize=fs, color=color)


def vdim(ax, y1, y2, x, text, ext_to=None, off=0.0, tick=None, color=INK, fs=7.5,
         right=True, rot=90):
    xl = x + off
    if tick is None:
        tick = (ax.get_ylim()[1]-ax.get_ylim()[0])*0.006
    base = ext_to if ext_to is not None else x
    ax.plot([base, xl + (tick if right else -tick)], [y1, y1], color=color, lw=0.5)
    ax.plot([base, xl + (tick if right else -tick)], [y2, y2], color=color, lw=0.5)
    _arrow(ax, (xl, y1), (xl, y2), color=color)
    _arrow(ax, (xl, y2), (xl, y1), color=color)
    dx = tick*1.1 if right else -tick*1.1
    ax.text(xl+dx, (y1+y2)/2, text, ha=("left" if right else "right"),
            va="center", fontsize=fs, color=color, rotation=rot)


def leader(ax, p_from, p_to, text, fs=7.5, color=INK, ha="left", va="center",
           dot=True, lw=0.7):
    """Annotation leader: dot at p_from, kinked line to text at p_to."""
    ax.annotate("", xy=p_from, xytext=p_to,
                arrowprops=dict(arrowstyle="-", color=color, lw=lw))
    if dot:
        ax.plot([p_from[0]], [p_from[1]], marker="o", ms=2.2, color=color)
    ax.text(p_to[0], p_to[1], text, fontsize=fs, color=color, ha=ha, va=va)


def callout(ax, p_from, p_to, text, fs=7.2, color=ACCENT):
    _arrow(ax, p_to, p_from, color=color, lw=0.8)
    ax.text(p_to[0], p_to[1], text, fontsize=fs, color=color,
            ha="left", va="center", fontweight="bold")


# ============================================================================
#  SYMBOLS
# ============================================================================
def north_arrow(ax, x, y, r=1.0):
    """North arrow in data coords (true north up)."""
    ax.add_patch(Polygon([(x, y+r), (x-r*0.45, y-r*0.7), (x, y-r*0.35)],
                         closed=True, fc=INK, ec=INK))
    ax.add_patch(Polygon([(x, y+r), (x+r*0.45, y-r*0.7), (x, y-r*0.35)],
                         closed=True, fc="white", ec=INK))
    ax.text(x, y+r*1.25, "N", ha="center", va="bottom", fontweight="bold",
            fontsize=9, color=INK)


def scale_bar(ax, x, y, total, n, unit_len, label, h=None, fs=6.5):
    """Graphic scale bar. total metres over n segments, in data coords."""
    if h is None:
        h = total*0.018
    seg = total/n
    for i in range(n):
        fc = INK if i % 2 == 0 else "white"
        ax.add_patch(Rectangle((x+i*seg, y), seg, h, fc=fc, ec=INK, lw=0.6))
    for i in range(n+1):
        ax.text(x+i*seg, y-h*0.6, f"{int(i*unit_len)}", ha="center", va="top",
                fontsize=fs, color=INK)
    ax.text(x+total/2, y+h*1.5, label, ha="center", va="bottom", fontsize=fs+0.5,
            color=INK)


def hatch_rect(ax, x, y, w, h, pattern="////", fc="none", ec=INK, lw=0.6, alpha=1):
    ax.add_patch(Rectangle((x, y), w, h, fill=(fc != "none"), fc=fc, ec=ec,
                           lw=lw, hatch=pattern, alpha=alpha))


def water_body(ax, x0, x1, ztop, zbed_fn, color=WATER):
    """Fill water column between surface ztop and seabed profile zbed_fn(x)."""
    xs = np.linspace(x0, x1, 200)
    zb = zbed_fn(xs)
    ax.fill_between(xs, zb, ztop, color=color, zorder=0)
    return zb


def wavy_surface(ax, x0, x1, z, amp=0.12, n=40, color="#2E6E8E", lw=1.2):
    xs = np.linspace(x0, x1, 300)
    ax.plot(xs, z+amp*np.sin(2*np.pi*n*(xs-x0)/(x1-x0)), color=color, lw=lw)
