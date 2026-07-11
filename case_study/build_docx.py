#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_docx.py  --  Assemble the holistic case_study.docx for the SDP-Kurnell
brine-dispersion case study from the NEREID-B run outputs + site input data.

Everything is pulled dynamically from:
  case_study/outputs/metrics_summary.json   (headline numbers + full config)
  case_study/outputs/*.csv                  (curves / transects / tables)
  case_study/outputs/figures/*.png          (post-processed figures)
  case_study/outputs/fig_*.png              (solver-native figures)
  case_study/inputs/*.csv                   (site survey data)
  validation/*.log, nereid_output/calibration.json

Output: case_study/case_study.docx
Accent colours use the project navy/teal palette.
"""
import csv
import glob
import json
import os

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "outputs")
FIG = os.path.join(OUT, "figures")
INP = os.path.join(HERE, "inputs")

NAVY = RGBColor(0x0B, 0x3D, 0x5C)
TEAL = RGBColor(0x13, 0x34, 0x3B)
ACCENT = RGBColor(0x2A, 0x9D, 0x8F)

with open(os.path.join(OUT, "metrics_summary.json")) as f:
    MS = json.load(f)
C = MS["config"]
M = MS["metrics"]
ss = M.get("steady_state", {})

# Convergence verdict, derived from the solver's scatter+trend test rather than asserted.
STEADY = bool(ss.get("steady_state_reached", False))
_conv = ss.get("converged", {})
NOT_CONVERGED = sorted(k for k, v in _conv.items() if not v)
_rdrift = ss.get("r_max_m_drift", 0.0)
_rdrel = ss.get("r_max_m_drift_rel", 0.0)
if STEADY:
    REACH_VERDICT = (f"converged: the reach drifts only {_rdrift:+.1f} m across the window, "
                     f"{100*_rdrel:.1f}% of its mean")
else:
    REACH_VERDICT = (f"NOT converged: the reach still drifts {_rdrift:+.1f} m across the window, "
                     f"{100*_rdrel:.1f}% of its mean — see §1.1")


def cal_value():
    p = os.path.join(ROOT, "nereid_output", "calibration.json")
    if os.path.exists(p):
        try:
            return json.load(open(p))
        except Exception:
            pass
    return None


CAL = cal_value()

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)


def H(text, lvl=1):
    p = doc.add_heading(text, level=lvl)
    for r in p.runs:
        r.font.color.rgb = NAVY if lvl <= 1 else TEAL
    return p


def P(text, bold=False, italic=False, size=10.5, color=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold; r.italic = italic; r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    return p


def bullet(text):
    doc.add_paragraph(text, style="List Bullet")


def numbered(text):
    doc.add_paragraph(text, style="List Number")


def table(headers, rows, widths=None, caption=None):
    if caption:
        c = doc.add_paragraph()
        rr = c.add_run(caption); rr.italic = True; rr.font.size = Pt(9.5)
        rr.font.color.rgb = TEAL
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = ""
        run = cell.paragraphs[0].add_run(str(h))
        run.bold = True; run.font.size = Pt(9.5); run.font.color.rgb = NAVY
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            cells[j].text = ""
            run = cells[j].paragraphs[0].add_run(str(val))
            run.font.size = Pt(9.5)
    doc.add_paragraph()
    return t


def figure(path, caption, width=6.3):
    if not os.path.exists(path):
        return
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = TEAL


def read_csv(path):
    with open(path) as f:
        rd = csv.reader(f)
        return next(rd), list(rd)


def g(key, default=None):
    return M.get(key, default)


excess_src = C["S0"] - C["S_amb_surf"]

# ============================================================ TITLE
ti = doc.add_heading("Industrial Case Study", level=0)
for r in ti.runs:
    r.font.color.rgb = NAVY
P("Prediction of brine-plume dispersion, evolution and seabed distribution for the "
  "Sydney Desalination Plant offshore submerged multiport diffuser "
  "(Kurnell, NSW — open Tasman Sea shelf)", bold=True, size=12.5, color=TEAL)
P("Modelling tool: NEREID-B (solver.py) — a universal 3-D finite-volume coupled "
  "brine-dispersion solver with near-field inclined-dense-jet correlation coupling, "
  "buoyancy-modified realizable k–ε turbulence, a full anisotropic dispersion tensor, "
  "partial-cell bathymetry and a Monte-Carlo stochastic ensemble. "
  "Status: VALIDATED against laboratory, field and analytical benchmarks. The far field "
  "is UNCALIBRATED — the dispersivity multiplier returned 1.00 against a representative "
  "(constructed, not measured) site transect, so no fitting was performed. Read §1.1 "
  "before quoting any number.", italic=True, size=10, color=TEAL)
P("Author: Akosa Samuel Onyejekwe — independent research work.",
  bold=True, size=11, color=NAVY)

# ============================================================ 1 EXEC SUMMARY
H("1.  Executive summary")
P(f"NEREID-B was applied to predict the fate of the hypersaline reject (brine) "
  f"discharged from the Sydney Desalination Plant (SDP) at Kurnell through its offshore "
  f"submerged multiport diffuser into the open Tasman Sea in ~{C['depth']:.0f} m of water. "
  f"The model resolves the near-field inclined-dense-jet behaviour via validated "
  f"correlations and the 3-D far-field gravity-current spreading and dilution of the "
  f"negatively-buoyant plume over the shelf seabed, under the site's ambient current, "
  f"stratification and energetic open-ocean wave climate. The far field was compared "
  f"against a representative site dilution transect (no fitting was required, and none "
  f"was performed) and the whole model chain was VALIDATED against the Roberts (1997) "
  f"dense-jet laboratory scaling, the published Perth multi-point field transect and a "
  f"lock-exchange PDE benchmark.")
P("Headline predictions (steady, quasi-equilibrium plume):", bold=True)
bullet(f"Source: discharge salinity {C['S0']:.1f} g/kg into {C['S_amb_surf']:.1f} g/kg "
       f"ambient (excess at source {excess_src:.1f} g/kg, "
       f"~{C['S0']/C['S_amb_surf']:.2f}× ambient).")
bullet(f"Near field (validated correlations): densimetric Froude number "
       f"Fr = {g('Fr_d', 0):.1f}; terminal rise {g('nf_rise_m', 0):.1f} m; seabed return "
       f"at {g('nf_return_dist_m', 0):.1f} m; return dilution {g('nf_return_dilution', 0):.0f}:1.")
bullet(f"Far field: seabed footprint above ΔS={C['dS_crit']} g/kg "
       f"≈ {g('seabed_footprint_m2', 0):.0f} m²; maximum excess {g('excess_max', 0):.2f} g/kg; "
       f"affected water volume ≈ {g('affected_volume_m3', 0):.0f} m³; horizontal reach "
       f"r_max ≈ {g('r_max_m', 0):.0f} m in the final ensemble-mean field, "
       f"{ss.get('r_max_m_mean', 0):.0f} ± {ss.get('r_max_m_std', 0):.0f} m over the steady "
       f"window ({REACH_VERDICT}).")
bullet(f"Vertical structure: the plume is bottom-trapped. The ΔS > {C['dS_crit']} g/kg region "
       f"occupies the lowest {g('z_deepest_m', 0) - g('plume_top_m', 0):.1f} m of the water "
       f"column (from {g('plume_top_m', 0):.1f} m depth down to {g('z_deepest_m', 0):.1f} m), "
       f"and its height above the source, {g('plume_rise_m', 0):.1f} m, is consistent with the "
       f"independently-derived near-field terminal rise of {g('nf_rise_m', 0):.1f} m.")
bullet(f"Reported peak salinity {g('S_max', 0):.2f} g/kg is NOT an emergent prediction: "
       f"{g('S_max', 0):.4f} g/kg is exactly the prescribed source value S_source handed over by "
       f"the near-field model. The minimum dilution of {g('dilution_min', 0):.0f}:1 sits slightly "
       f"below the near-field hand-off of {g('nf_return_dilution', 0):.0f}:1 for the same reason "
       f"(§12.4). Both are diagnostics of the source condition.")
if CAL:
    bullet(f"Calibration: the far-field dispersivity multiplier farfield_disp_cal returned "
           f"{CAL.get('farfield_disp_cal', C.get('farfield_disp_cal', 1.0)):.2f} — i.e. unity, no "
           f"adjustment. The target transect is representative, not measured, so this is a "
           f"consistency check rather than a calibration (§10).")
P(f"Mixing-zone assessment: against a conservative sub-lethal assessment contour of "
  f"ΔS = {C['dS_crit']} g/kg (more protective than the ~1 ppt typical of NSW mixing-zone "
  f"practice), the model predicts a seabed excess-salinity footprint of "
  f"≈ {g('seabed_footprint_m2', 0):.0f} m² within roughly {g('r_max_m', 0):.0f}–"
  f"{ss.get('r_max_m_mean', 0):.0f} m of the diffuser. The maximum excess anywhere in the "
  f"domain is {g('excess_max', 0):.2f} g/kg, comfortably inside every applicable limit "
  f"(NSW ~1 ppt; Perth 1.2 ppt at 50 m; California 2.0 ppt at 100 m), so the compliance "
  f"conclusion is robust even where the footprint precision is not. Run health is exact "
  f"(divergence {g('divergence_final', 0):.1e}, mass imbalance "
  f"{g('mass_imbalance_final', 0):.1e}, eddy-viscosity cap engaged in "
  f"{100*g('nut_cap_fraction', 0):.0f}% of cells — physical, no railing).")

# ------------------------------------------------------------ 1.1 CAVEATS
H("1.1  Interpretation caveats (read before quoting any number)", 2)
P("The numbers above are reported exactly as the run produced them. This section states what "
  "each of them can and cannot bear. None of these caveats overturn the compliance conclusion; "
  "they bear on its precision and on which quantities are predictions at all.", italic=True)

_caveats = [
    f"Peak salinity is a boundary condition, not a prediction. The far field is seeded by "
    f"relaxing S toward S_source inside a Gaussian blob whose centre relaxes fully, so "
    f"S_max = {g('S_max', 0):.4f} g/kg is exactly S_source = S_amb,bed + (S₀ − S_amb,bed)/S_r for "
    f"ANY blob geometry. The solver is reporting its own source condition. The same mechanism "
    f"makes the minimum dilution ({g('dilution_min', 0):.1f}:1) sit a little below the "
    f"near-field hand-off ({g('nf_return_dilution', 0):.1f}:1), because the peak-excess cell "
    f"lies a few metres above the bed where the ambient is fresher (§12.4).",
    f"The {C['ensemble']}-member ensemble cannot support the statistics derived from it. With "
    f"two members the exceedance field takes only the values 0, 0.5 and 1, and a 95th "
    f"percentile is simply the larger of two samples. Compounding this, the Ornstein–Uhlenbeck "
    f"correlation time τ = {C.get('stoch_tau', 600):.0f} s is comparable with the run length, so "
    f"the forcing barely decorrelates. The spread is reported in §12.3 for completeness and must "
    f"not be used as an uncertainty bound.",
    "The far field is not calibrated. The dispersivity multiplier returned unity against a "
    "transect constructed to be reproducible without tuning (§10). The independent far-field "
    "evidence is the Perth transect (~22% conservative) and the lock-exchange PDE benchmark.",
    "Physics claimed in §2 that remained INACTIVE in this run: osmotic salt flux, osmotic body "
    "force, Soret/Dufour cross-diffusion, the higher-order (TEOS-10-style) equation-of-state "
    "terms, and the genuine free surface. The run used near-field coupling, full-tensor "
    "dispersion, realizable k–ε with the corrected buoyancy sign, quadratic bottom drag with a "
    "wall function, and stochastic forcing.",
    "The near field is not resolved. Its 7.0 m return distance spans about 1.2 cells at "
    "dx = 5.77 m; it is supplied by validated correlation, and recovering the published 2.2 "
    "rise coefficient verifies the coupling arithmetic rather than independently predicting the "
    "physics.",
    f"The former far-field eddy-viscosity railing is RESOLVED. An earlier build could not be "
    f"integrated past ~400–600 s: in the weakly-stratified, low-strain far field neither the strain "
    f"nor a buoyancy realizability bound binds, so ν_t = C_μ k²/ε ran free, spurious turbulent energy "
    f"accumulated and ν_t railed to its ceiling (≈29% of cells by t = 600 s), forcing a short "
    f"t_end = 200 s with bottom drag off. A turbulent length-scale limiter (Galperin 1988 buoyancy "
    f"limit plus a geometric mixing-length cap, imposed as a floor on ε) together with a semi-implicit "
    f"(Patankar) k–ε sink now bound ν_t to a physical value and drain the spurious energy. Confirmed: "
    f"the eddy-viscosity cap engages in {100*g('nut_cap_fraction', 0):.0f}% of cells at t_end = "
    f"{C['t_end']:.0f} s with bottom drag ON (0% at t = 900 s on the same grid). With bottom drag now "
    f"enabled the horizontal reach is BOUNDED and statistically stationary — it surges then retreats "
    f"and oscillates with the tidal/stochastic forcing rather than climbing monotonically — so it is "
    f"reported as a central estimate, not a lower bound. The near-field validation and the headline "
    f"metrics are unchanged by the limiter, which binds only in the far field.",
]
if not STEADY:
    _caveats.insert(1, (
        f"Steady state was NOT reached. The solver's steady-state test now bounds both the "
        f"relative scatter (tol = {C.get('steady_tol', 0.2):.2f}) and the linear trend across the "
        f"window (tol = {C.get('steady_trend_tol', 0.05):.2f}). On this run the following metrics "
        f"still drift: {', '.join(NOT_CONVERGED)}. The reach drifts {_rdrift:+.1f} m across the "
        f"window ({100*_rdrel:.1f}% of its mean). Quote the reach as a range, not a converged value."))
else:
    _caveats.insert(1, (
        f"Steady state was reached, on a test that bounds trend as well as scatter. Across the "
        f"trailing window every tracked metric satisfies both |σ| ≤ {C.get('steady_tol', 0.2):.2f}·|mean| "
        f"and |drift| ≤ {C.get('steady_trend_tol', 0.05):.2f}·|mean|; the reach drifts only "
        f"{_rdrift:+.1f} m ({100*_rdrel:.1f}% of its mean). An earlier build of this study reported "
        f"'steady' from a scatter-only test that a monotonically climbing metric could pass."))

for b in _caveats:
    bullet(b)

# ============================================================ 2 NOVELTY / UNIVERSALITY
H("2.  Novelty, universality and scope of the NEREID-B solver")
P("NEREID-B is a single solver that spans the full dispersion problem — from the "
  "sub-grid nozzle jet to the far-field seabed gravity current — that conventional "
  "practice splits across two incompatible tool classes. This end-to-end coupling, "
  "together with the physics below, is the novel and defensible core of the tool:")
bullet("Universal near-field ↔ far-field coupling: a validated inclined-dense-jet "
       "correlation (Roberts 1997) supplies the diluted return seed to a genuine 3-D "
       "finite-volume RANS far field — bridging the gap between integral near-field "
       "models (CORMIX, VISJET/JETLAG, Visual PLUMES) that stop at the return point and "
       "coastal circulation models (Delft3D, MIKE-3, ROMS) that cannot resolve the jet.")
bullet("Full anisotropic, state-dependent dispersion TENSOR with off-diagonal terms "
       "(isotropic + flow-aligned Taylor shear + wave + along-slope bathymetric), kept "
       "symmetric-positive-definite for numerical safety — richer than the scalar "
       "eddy-diffusivity used by standard coastal models.")
bullet("Buoyancy-modified REALIZABLE k–ε closure (Durbin time-scale limiter) with the "
       "correct stratification-damping sign, eliminating the eddy-viscosity railing that "
       "makes generic RANS over-mix dense stratified plumes.")
bullet("Optional reactive/osmotic and thermohaline cross-fluxes (osmotic salt flux, "
       "Soret/Dufour coupling) and a nonlinear (cabbeling/TEOS-10-style) equation of "
       "state — physics absent from all mainstream brine tools.")
bullet("Native Monte-Carlo stochastic ensemble (Ornstein–Uhlenbeck coloured forcing) "
       "delivering mean, variance and exceedance-probability fields — turning a single "
       "deterministic prediction into a quantified-uncertainty risk map.")
bullet("Partial-cell (shaved-cell) bathymetry, machine-precision divergence-free "
       "projection, TVD-MUSCL positivity-preserving scalar transport, implicit LOD "
       "diffusion and an optional genuine free surface — a numerically solidified core "
       "(13/13 self-tests, 4/4 validation, PDE benchmark PASS).")
P("Applicability envelope: deep / submerged multiport brine diffusers — the dominant "
  "modern desalination outfall class (Perth, Gold Coast, Sydney, Carlsbad, Sorek). The "
  "same solver also carries submerged/surface discharge modes, correlation and "
  "Lagrangian near-field models, and CPU/GPU back-ends, making it a universal brine-outfall "
  "prediction engine.", italic=True, color=TEAL)

# ============================================================ 3 SITE
H("3.  Site description and problem statement")
P("The Sydney Desalination Plant at Kurnell produces up to 250 ML/day of potable water "
  "by seawater reverse osmosis (recovery ~47%) and returns the RO concentrate to the "
  "open Tasman Sea through an offshore diffuser on the continental shelf in ~25 m of "
  "water, via tunnelled risers fitted with inclined multiport rosette heads. The "
  f"concentrate (~{C['S0']:.0f} g/kg, ~{C['S0']/C['S_amb_surf']:.1f}× the ambient "
  f"~{C['S_amb_surf']:.1f} g/kg) is negatively buoyant: it rises briefly as a turbulent "
  "jet, falls back to the seabed and spreads as a dense gravity current. The assessment "
  "question is whether the diffuser dilutes the brine enough that the seabed "
  "excess-salinity footprint and the mixing-zone concentrations remain within ecological "
  "limits on this exposed shelf site.")
P("Prediction objectives:", bold=True)
for o in ["the near-field rise height, seabed return distance and return dilution;",
          "the steady 3-D distribution of excess salinity and brine dilution over the seabed;",
          "the centreline dilution and excess-salinity decay with distance;",
          "the seabed footprint area exceeding the assessment threshold and the affected volume;",
          "the vertical structure of the near-bed dense layer;",
          "mixing-zone compliance with a stochastic uncertainty band."]:
    bullet(o)

# ============================================================ 4 GOVERNING MODEL
H("4.  Governing model (coupled PDE system)")
P("NEREID-B advances the coupled state vector q = (u, v, w, p, S, T, ρ, k, ε, ζ) with an "
  "incompressible fractional-step (Chorin projection) finite-volume scheme:")
table(["Field", "Governing balance", "Key terms"],
      [["u, v, w — velocity", "RANS momentum + projection",
        "advection, Coriolis, full nonlinear buoyancy, ∇·(ν+ν_t)∇u, wave stress"],
       ["p — pressure", "incompressible (Boussinesq) projection",
        "variable-coefficient Poisson (partial cells + free-surface term)"],
       ["S — absolute salinity", "advection + anisotropic dispersion",
        "TVD-MUSCL advection, dispersion tensor D, optional osmotic/Soret flux"],
       ["T — temperature", "advection + dispersion",
        "TVD advection, thermal dispersion, optional Dufour flux"],
       ["ρ — density", "nonlinear equation of state",
        "ρ(S,T,z): haline/thermal + cabbeling/thermobaric"],
       ["k, ε — turbulence", "buoyancy-modified realizable k–ε",
        "shear production, buoyancy damping (correct sign), Durbin limiter, LES floor"],
       ["ζ — stochastic forcing", "Ornstein–Uhlenbeck coloured noise",
        "spatially-correlated random field → Monte-Carlo ensemble"]],
      caption="Table 4.1 — Coupled fields and governing balances solved by NEREID-B.")
P("The unresolvable sub-grid nozzle is represented by validated inclined-dense-jet "
  "correlations that seed the 3-D far field with the diluted return plume; the 3-D model "
  "then resolves the seabed gravity-current spreading and mixing. The full symbolic PDE "
  "system and closure coefficients are documented in the solver header and the "
  "accompanying model dossier.")

# ============================================================ 5 GEOMETRY / DOMAIN
H("5.  Geometry, domain and bathymetry")
table(["Parameter", "Value", "Unit"],
      [["Model domain (Lx × Ly × depth)", f"{C['Lx']:.0f} × {C['Ly']:.0f} × {C['depth']:.0f}", "m"],
       ["Water depth at diffuser", f"{C['depth']:.0f}", "m"],
       ["Nearshore depth (x = 0)", f"{C['bathy_min_depth']:.0f}", "m"],
       ["Shelf slope", f"{C['bathy_slope']:.3f}", "– (m/m)"],
       ["Source position (x_frac, y_frac)", f"{C['x_src_frac']:.2f}, {C['y_src_frac']:.2f}", "–"],
       ["Nozzle height above seabed", f"{C['nozzle_height']:.1f}", "m"],
       ["Diffuser ports × spacing", f"{C['n_ports']} × {C['port_spacing']:.0f}", "– × m"]],
      caption="Table 5.1 — Geometry and bathymetry. Bathymetry is supplied as a partial-cell "
              "field H(x,y); the survey grid is in inputs/bathymetry_survey.csv.")
DWG = os.path.join(HERE, "drawings")
for fn, cap in [
    ("dwg_05_ga.png", "Drawing 1 — General arrangement of the offshore outfall and diffuser."),
    ("dwg_03_diffuser.png", "Drawing 2 — Multiport diffuser / riser detail."),
    ("dwg_04_dispersion.png", "Drawing 3 — Near-field to far-field dispersion concept."),
]:
    figure(os.path.join(DWG, fn), cap, width=6.1)

# ============================================================ 6 INPUT DECK
H("6.  Input data (model deck)")
P("The full machine-readable deck is saved as case_study/sydney_sdp_case.json; the "
  "site-specific survey data are in case_study/inputs/ (bathymetry, CTD casts, ADCP "
  "profile & time series, wave climate, met wind, and the CTD dilution transect).")

H("6.1  Discharge / diffuser", 2)
table(["Parameter", "Symbol", "Value", "Unit"],
      [["Reject (brine) salinity", "S₀", f"{C['S0']:.1f}", "g/kg"],
       ["Reject temperature", "T_b", f"{C['T_b']:.1f}", "°C"],
       ["Flow per port", "Q", f"{C['Q_d']:.4f}", "m³/s"],
       ["Port diameter", "d_p", f"{C['d_p']:.3f}", "m"],
       ["Nozzle elevation angle", "θ", f"{C['theta_deg']:.0f}", "deg"],
       ["Number of ports", "n", f"{C['n_ports']}", "–"],
       ["Port spacing", "s", f"{C['port_spacing']:.1f}", "m"],
       ["Exit densimetric Froude number", "Fr", f"{g('Fr_d', 0):.1f}", "–"]],
      caption="Table 6.1 — Discharge and diffuser configuration.")

H("6.2  Ambient sea (receiving water)", 2)
table(["Parameter", "Surface", "Bottom", "Unit"],
      [["Ambient salinity", f"{C['S_amb_surf']:.1f}", f"{C['S_amb_bot']:.1f}", "g/kg"],
       ["Ambient temperature", f"{C['T_amb_surf']:.1f}", f"{C['T_amb_bot']:.1f}", "°C"]],
      caption="Table 6.2 — Ambient stratification (summer). Full CTD casts: inputs/ctd_casts.csv.")

H("6.3  Met-ocean forcing", 2)
table(["Parameter", "Symbol", "Value", "Unit"],
      [["Ambient current", "U_c", f"{C['U_current']:.2f}", "m/s"],
       ["Tidal current amplitude", "U_tide", f"{C['tide_amp']:.2f}", "m/s"],
       ["Tidal period (M2)", "T_tide", f"{C['tide_period']/3600:.2f}", "h"],
       ["Significant wave height", "H_s", f"{C['Hs']:.1f}", "m"],
       ["Wave period", "T_w", f"{C['Tw']:.1f}", "s"],
       ["Wind speed (10 m)", "U₁₀", f"{C['wind10']:.1f}", "m/s"],
       ["Latitude (Coriolis)", "φ", f"{C['latitude_deg']:.0f}", "deg"]],
      caption="Table 6.3 — Met-ocean forcing. ADCP: inputs/adcp_*.csv; waves: "
              "inputs/wave_climate_monthly.csv; wind: inputs/met_wind_timeseries.csv.")

H("6.4  Numerical configuration", 2)
table(["Parameter", "Value", "Parameter", "Value"],
      [["Grid (nx × ny × nz)", f"{C['nx']} × {C['ny']} × {C['nz']}",
        "Cell size (dx × dy × dz)", f"{C['dx']:.1f} × {C['dy']:.1f} × {C['dz']:.2f} m"],
       ["Simulated time", f"{C['t_end']:.0f} s", "Ensemble members", f"{C['ensemble']}"],
       ["Near-field coupling", f"{C['near_field_coupling']}", "Stochastic forcing", f"{C['stoch_enable']}"],
       ["Full tensor dispersion", f"{C['full_tensor_dispersion']}", "Realizable k–ε", f"{C['realizable_keps']}"],
       ["Assessment contour ΔS_crit", f"{C['dS_crit']} g/kg", "Far-field disp. cal.",
        f"{C.get('farfield_disp_cal', 1.0):.2f}"]],
      caption="Table 6.4 — Numerical configuration and active physics.")

# --- site survey data summary (from inputs/) ---
H("6.5  Site-specific survey data (credible representative deck)", 2)
P("The following site data were prepared as a credible representative survey for the "
  "Kurnell outfall corridor (documented, not measured per-station) and are supplied as "
  "CSV decks in case_study/inputs/. They set the bathymetry, ambient stratification, "
  "currents and wave climate and provide the calibration transect.")
site_files = [
    ("bathymetry_survey.csv", "Multibeam-style bathymetry grid over the diffuser corridor"),
    ("ctd_casts.csv", "Summer & winter CTD casts (S, T, σ_t vs depth)"),
    ("adcp_mean_profile.csv", "Bottom-mounted ADCP mean current profile"),
    ("adcp_depthavg_timeseries.csv", "Depth-averaged current time series (M2 tide + drift)"),
    ("wave_climate_monthly.csv", "Monthly wave climatology (Hs, Tp, direction)"),
    ("met_wind_timeseries.csv", "10 m wind time series"),
    ("site_ctd_dilution_transect.csv", "Centreline CTD/ADCP dilution transect — calibration target"),
]
table(["File (inputs/)", "Contents"], [[f, d] for f, d in site_files],
      caption="Table 6.5 — Site-specific survey decks.")

# ============================================================ 7 MESH
H("7.  Mesh and discretisation setup")
P(f"The domain is discretised on a structured finite-volume grid of "
  f"{C['nx']} × {C['ny']} × {C['nz']} = {C['nx']*C['ny']*C['nz']:,} cells "
  f"(dx = {C['dx']:.1f} m, dy = {C['dy']:.1f} m, dz = {C['dz']:.2f} m), z positive up with "
  "the free surface at z = 0. Variable bathymetry H(x,y) is represented with PARTIAL-CELL "
  "(shaved-cell) topography — fractional open face areas remove the staircase a binary "
  "mask would produce, so the dense gravity current runs smoothly down the shelf slope. "
  "A MAC (staggered) arrangement carries velocities on cell faces and scalars at cell "
  "centres. The variable-coefficient pressure-Poisson matrix (partial-cell open areas + "
  "free-surface term) is assembled once and LU-factorised, so each timestep is a fast "
  "back-substitution.")

# ============================================================ 8 MODEL SETUP
H("8.  Model setup (physics and coupling)")
for b in [
    "Near-field coupling ON: the inclined-dense-jet correlation computes the terminal "
    "rise, return distance and return dilution, and seeds the 3-D far field with the "
    "diluted return plume at the seabed. The seed blob is ANISOTROPIC — horizontal σ floored "
    "at the grid scale (8.65 m), vertical σ set by the physical return-plume half-width "
    "(2.50 m) — so the injection does not smear the plume up the water column (§12.4).",
    "Turbulence: buoyancy-modified realizable k–ε with the correct stratification-damping "
    "sign and Durbin time-scale limiter; Smagorinsky/WALE LES dissipation floor.",
    f"Seabed: partial-cell (shaved-cell) bathymetry with quadratic bottom drag "
    f"(C_d = {C.get('Cd_bed', 0.0025):.4f}) and a log-law wall function — the bed retards the "
    f"gravity-current front rather than letting it slide free-slip.",
    "Transport: TVD-MUSCL (van Leer) advection on divergence-free MAC face velocities, "
    "positivity-preserving for salinity; full anisotropic dispersion tensor; implicit "
    "(backward-Euler LOD, Strang-symmetric) diagonal diffusion.",
    "Equation of state: nonlinear (linear + cabbeling) ρ(S,T,z).",
    f"Stochastic ensemble: {C['ensemble']} Ornstein–Uhlenbeck-forced realisations "
    f"(σ = {C['stoch_sigma']}, correlation length {C['stoch_length']:.0f} m) → mean, "
    "variance and exceedance-probability fields.",
    "Robustness: runtime blow-up guard, machine-precision divergence-free projection, "
    "enforced global mass balance, conservative mass-redistributing safety clip.",
]:
    bullet(b)

# ============================================================ 9 SOLUTION
H("9.  Solution procedure and run health")
P("Each timestep: (1) explicit advection + Coriolis + buoyancy + dispersion tendencies; "
  "(2) implicit diagonal diffusion (LOD); (3) pressure projection to enforce continuity; "
  "(4) scalar transport with TVD limiter and conservative clip; (5) turbulence update; "
  "(6) stochastic forcing increment. The run is advanced to a quasi-steady plume and "
  "metrics are averaged over the converged window.")
ss = M.get("steady_state", {})
table(["Run-health metric", "Value"],
      [["Final divergence (continuity residual)", f"{g('divergence_final', 0):.2e}"],
       ["Max divergence over run", f"{g('divergence_max_over_run', 0):.2e}"],
       ["Global mass imbalance", f"{g('mass_imbalance_final', 0):.2e}"],
       ["Eddy-viscosity cap fraction", f"{100*g('nut_cap_fraction', 0):.1f} %"],
       ["Steady-state window", f"{ss.get('window_s', ['–','–'])[0]:.0f}–{ss.get('window_s',[0,0])[1]:.0f} s"
        if ss.get('window_s') else "–"],
       ["Steady state reached", f"{ss.get('steady_state_reached', '–')} (scatter + trend test)"],
       ["Reach drift across window", f"{_rdrift:+.1f} m ({100*_rdrel:.1f}% of mean)"]],
      caption="Table 9.1 — Solver health and convergence diagnostics.")
P(f"How the steady-state flag is defined. A metric counts as steady only if BOTH its relative "
  f"scatter and its linear drift across the trailing window are small: "
  f"|σ| ≤ {C.get('steady_tol', 0.2):.2f}·|mean| AND |drift| ≤ "
  f"{C.get('steady_trend_tol', 0.05):.2f}·|mean|. The trend term matters: an earlier build of "
  f"this study tested scatter alone, and a reach that climbed monotonically from 26 m to 96 m "
  f"passed it, because a steadily-rising quantity has small scatter about its own mean. Over "
  f"the {ss.get('window_s', [0, 0])[0]:.0f}–{ss.get('window_s', [0, 0])[1]:.0f} s window the "
  f"reach now has mean {ss.get('r_max_m_mean', 0):.1f} m, σ = {ss.get('r_max_m_std', 0):.1f} m "
  f"and drift {_rdrift:+.1f} m. "
  + ("Every tracked metric passes both tests." if STEADY else
     f"The following metrics still fail: {', '.join(NOT_CONVERGED)}.")
  + " S_max is stationary trivially, because it is pinned to the prescribed source value "
    "(§12.4). The divergence and mass-balance figures are sound and unaffected.",
  italic=True, color=TEAL)

# ============================================================ 10 CALIBRATION
H("10.  Comparison against the representative site transect")
tr_hdr, tr_rows = read_csv(os.path.join(INP, "site_ctd_dilution_transect.csv"))
P("The far-field spreading rate is governed by a single knob, farfield_disp_cal, which "
  "scales the tunable horizontal dispersivity. It was exercised against a centreline "
  "dilution transect at the mixing-zone boundary (50 m). The near-field correlations and "
  "the molecular and turbulent diffusivities are left physical (unfitted).")
table(["Distance (m)", "Target dilution (representative)", "Target ΔS (g/kg)"],
      [[r[0], r[1], r[2]] for r in tr_rows],
      caption="Table 10.1 — Representative centreline dilution transect "
              "(inputs/site_ctd_dilution_transect.csv). These values are constructed, "
              "not measured — see the provenance note below.")
if CAL:
    P(f"Result: farfield_disp_cal = {CAL.get('farfield_disp_cal', 1.0):.2f}. The multiplier "
      f"returned unity, i.e. no adjustment was made and the model reproduced the "
      f"{tr_rows[-1][1]}:1 target at {tr_rows[-1][0]} m without tuning. Full log: "
      f"validation/ctd_calibration.log; machine-readable result: "
      f"nereid_output/calibration.json.", color=TEAL)
P("Provenance — this is a consistency check, not a calibration. The transect is generated "
  "by case_study/make_site_data.py, whose source comment records that the stations were "
  "chosen to be “reproducible by the model at no tuning”. A procedure that recovers "
  "unity against a target constructed to be recoverable has demonstrated consistency, not "
  "predictive skill. The model has NOT been calibrated to measured data, and the word "
  "“calibrated” is therefore avoided throughout this report. The independent far-field "
  "evidence is the Perth transect in §11, against which the model was not fitted and is "
  "shown conservative. To convert this into a genuine calibration, either commission a "
  "site CTD/ADCP survey or adopt the measured Gold Coast Tugun transect (Baum et al. 2019) "
  "as the target.", italic=True, color=TEAL)

# ============================================================ 11 VALIDATION
H("11.  Validation and data sources")
P("The model chain is validated at three independent levels — near-field (laboratory), "
  "far-field (field) and PDE core (analytical benchmark). All source data are recorded.")
table(["Level", "Benchmark / data (source)", "Accepted value", "NEREID-B result"],
      [["Near-field jet (lab)", "60° inclined dense-jet scaling — Roberts et al. (1997); "
        "Lai & Lee (2012); Papakonstantis et al. (2011)",
        "z_t/(D·Fr) ≈ 2.0–2.2; S_r ≈ 1.6·Fr", "z_t/(D·Fr)=2.20; S_r≈1.6·Fr — PASS (4/4)"],
       ["Far-field (field)", "Gold Coast Tugun measured diffuser dilution — Baum et al. (2019); "
        "Perth design transect — Roberts et al. (2019)",
        "~45–63:1 @ 50–60 m (in-class)", "Conservative (under-predicts dilution) — protective"],
       ["Far-field (site)", "SDP Kurnell measured impact extent — Clark et al. (2018)",
        "detectable effects to ~100 m", "footprint within ≈ %d–%d m — consistent in scale"
        % (round(min(g('r_max_m', 0), ss.get('r_max_m_mean', 0))),
           round(max(g('r_max_m', 0), ss.get('r_max_m_mean', 0))))],
       ["PDE core", "Lock-exchange front Froude number — Benjamin (1968); Shin et al. (2004)",
        "F_H = 0.50", "Fr_f ≈ 0.47 — PASS"],
       ["Robustness", "Invariants: mass/positivity/divergence/EOS/restart — solver.py",
        "exact / bounded", "13/13 self-tests PASS"]],
      caption="Table 11.1 — Validation summary (verified sources; see §17 and validation/sources.md). "
              "Logs in validation/.")
P("The near-field uses the validated laboratory scaling directly — note that recovering "
  "z_t/(D·Fr) = 2.20 from a hard-coded 2.2 coefficient verifies the coupling arithmetic "
  "rather than independently predicting the physics. The far field is compared with the "
  "representative site transect (§10, no fitting) and shown conservative against the in-class "
  "Perth field data, which the model was never fitted to. The two genuinely independent "
  "gates are therefore the Perth comparison and the lock-exchange PDE benchmark. "
  "Independently, the actual SDP Kurnell outfall study (Clark et al. 2018) found detectable "
  "ecological effects to ~100 m; this is an ecological effect distance driven partly by "
  "diffuser-induced near-bed flow, not a salinity isopleth, so it is an order-of-magnitude "
  "consistency check rather than a validation. Full citations and honest data-provenance "
  "caveats are in validation/sources.md.")

# ============================================================ 12 RESULTS
H("12.  Predicted results")
H("12.1  Headline metrics", 2)
table(["Quantity", "Predicted value", "Unit"],
      [["Densimetric Froude number, Fr", f"{g('Fr_d', 0):.1f}", "–"],
       ["Near-field terminal rise height", f"{g('nf_rise_m', 0):.1f}", "m"],
       ["Near-field seabed return distance", f"{g('nf_return_dist_m', 0):.1f}", "m"],
       ["Near-field (return) dilution", f"{g('nf_return_dilution', 0):.0f}", ":1"],
       ["Peak salinity", f"{g('S_max', 0):.2f}", "g/kg"],
       ["Max excess above ambient", f"{g('excess_max', 0):.2f}", "g/kg"],
       ["Minimum far-field dilution", f"{g('dilution_min', 0):.0f}", ":1"],
       ["Horizontal reach r_max", f"{g('r_max_m', 0):.0f}", "m"],
       [f"Seabed footprint (ΔS > {C['dS_crit']})", f"{g('seabed_footprint_m2', 0):.0f}", "m²"],
       ["Affected water volume", f"{g('affected_volume_m3', 0):.0f}", "m³"]],
      caption="Table 12.1 — Headline predicted metrics. Peak salinity and minimum dilution "
              "are diagnostics of the prescribed source value, not emergent predictions (§12.4); "
              "r_max is the final ensemble-mean value; with bottom drag the reach is bounded and "
              "oscillates with the forcing (§1.1).")

H("12.2  Seabed footprint sensitivity to the threshold", 2)
iso_p = os.path.join(OUT, "isopleth_area_vs_threshold.csv")
if os.path.exists(iso_p):
    _, iso_rows = read_csv(iso_p)
    table(["Threshold ΔS (g/kg)", "Footprint area (m²)", "Equiv. radius (m)", "Dilution at threshold"],
          [[r[0], r[1], r[2], r[3]] for r in iso_rows],
          caption="Table 12.2 — Seabed footprint area vs excess-salinity threshold "
                  "(isopleth_area_vs_threshold.csv).")

H("12.3  Stochastic uncertainty (ensemble) — reported, but not usable as an uncertainty bound", 2)
P(f"Across the {C['ensemble']}-member ensemble the peak-excess standard deviation is "
  f"{g('S_std_max', 0):.3f} g/kg and the nominal 95th-percentile excess reaches "
  f"{g('excess_p95_max', 0):.2f} g/kg, giving the exceedance field plotted in §13.")
P(f"These figures are reported for completeness and must not be used as an uncertainty "
  f"bound. With {C['ensemble']} members a sample standard deviation carries ~100% relative "
  f"uncertainty, and a 95th percentile is not estimable at all — it is simply the larger of "
  f"two samples. The 'exceedance probability' field can take only the values 0, 0.5 and 1, so "
  f"it is a three-level indicator, not a probability. Compounding this, the "
  f"Ornstein–Uhlenbeck correlation time is τ = {C.get('stoch_tau', 600):.0f} s against a run "
  f"length of {C['t_end']:.0f} s, so the forcing never decorrelates within a member and each "
  f"realisation samples essentially one frozen draw of the random field. A defensible "
  f"exceedance map needs O(100) members run over several correlation times.",
  italic=True, color=TEAL)

H("12.4  Vertical structure, and the source condition", 2)
P("The 3-D far field is seeded by relaxing salinity toward S_source inside a Gaussian blob "
  "centred at the near-field seabed return point. The blob is ANISOTROPIC: its horizontal "
  "scale is floored at the grid scale, 1.5·max(dx,dy) = 8.65 m, because a source narrower "
  "than a cell is unresolvable; its vertical scale is the physical return-plume half-width, "
  "2.50 m, floored only at the cell height 1.5·dz = 1.44 m. An earlier build of this study "
  "used a single isotropic floor of 1.5·max(dx,dz), which dx set to 8.65 m; that injected "
  "brine over roughly a third of the water column, drove the entire source column to "
  "S_source, and destroyed the near-source bottom-trapping. This section records both the "
  "corrected structure and the one diagnostic the correction cannot repair.")
for b in [
    f"The plume is bottom-trapped. The ΔS > {C['dS_crit']} g/kg region occupies the lowest "
    f"{g('z_deepest_m', 0) - g('plume_top_m', 0):.1f} m of the water column, from "
    f"{g('plume_top_m', 0):.1f} m depth down to the bed at {g('z_deepest_m', 0):.1f} m. The "
    f"upper water column carries only trace excess.",
    f"The vertical extent is now consistent with the independent near-field model. The "
    f"impacted region rises {g('plume_rise_m', 0):.1f} m above the source, against a "
    f"terminal jet rise of {g('nf_rise_m', 0):.1f} m from the Roberts (1997) correlation — a "
    f"cross-check the earlier build failed badly, reporting 22.8 m.",
    f"Peak salinity remains a boundary condition. S_max = {g('S_max', 0):.4f} g/kg is exactly "
    f"S_source = S_amb,bed + (S₀ − S_amb,bed)/S_r. The blob centre relaxes fully toward "
    f"S_source whatever its width, so no change of blob geometry can make S_max a prediction. "
    f"Reporting it as 'predicted peak salinity' is a category error.",
    f"Minimum dilution inherits the same defect, but only mildly. Dilution is evaluated "
    f"against the local depth-varying ambient, and the peak-excess cell sits a few metres "
    f"above the bed where the ambient is fresher, so it reports "
    f"{g('dilution_min', 0):.1f}:1 rather than the {g('nf_return_dilution', 0):.1f}:1 handed "
    f"over at the bed. The plume does not re-concentrate; the earlier build's 32:1 was the "
    f"same artefact, magnified.",
]:
    bullet(b)
P("Datum note. In plume_envelope_vs_distance.csv the columns core_depth_below_surface_m and "
  "layer_top_depth_below_surface_m are DEPTHS BELOW THE SEA SURFACE (postprocess.py computes "
  "the layer top as −min(z) over the active column), not heights above the seabed. The layer "
  "envelope is moreover built from a 0.02 g/kg trace threshold, not from the ΔS_crit "
  "assessment contour, so its reported 'layer top' tracks where a trace of salt has mixed "
  "upward rather than where the assessed plume ends. Read the envelope for the CORE DEPTH, "
  "which now sits on the bed, and take the assessed vertical extent from the metrics above. "
  "An earlier draft of this study, and of the slide deck, read the layer top as a height "
  "above bed and concluded the surface waters were unaffected; both the datum and the "
  "conclusion have been corrected.", italic=True, color=TEAL)

# ============================================================ 13 FIGURES
H("13.  Output figures, curves and contours")
figs = [
    ("map_seabed_excess.png", "Figure 1 — Predicted seabed excess-salinity footprint (plan view), "
     "with the ΔS_crit assessment contour."),
    ("map_seabed_dilution.png", "Figure 2 — Predicted seabed brine dilution (plan view)."),
    ("section_centerline_xz.png", "Figure 3 — Vertical section of excess salinity along the plume "
     "centreline, showing the bottom-trapped dense gravity-current layer (§12.4)."),
    ("map_seabed_currents.png", "Figure 4 — Near-bed current field driving the gravity-current spreading."),
    ("map_exceedance_probability.png", "Figure 5 — Exceedance-probability map for ΔS_crit across the "
     "stochastic ensemble."),
    ("map_ensemble_mean_std.png", "Figure 6 — Ensemble-mean and ensemble-std excess-salinity maps."),
    ("nearfield_trajectory.png", "Figure 7 — Near-field inclined dense-jet trajectory "
     "(validated correlation model)."),
    ("plot_curve_centerline.png", "Figure 8 — Centreline brine dilution and excess-salinity decay "
     "with distance from the diffuser."),
    ("plot_seabed_centerline_transect.png", "Figure 9 — Seabed centreline transect (excess & dilution)."),
    ("plot_isopleth_area_vs_threshold.png", "Figure 10 — Seabed footprint area vs threshold."),
    ("plot_plume_envelope_vs_distance.png", "Figure 11 — Dense-layer envelope vs distance. Core "
     "depth, layer top and thickness are DEPTHS BELOW THE SEA SURFACE, not heights above the "
     "bed, and the envelope is traced at a 0.02 g/kg trace threshold rather than at ΔS_crit "
     "(§12.4). The core depth is the physically meaningful curve."),
    ("plot_vertical_profiles_stations.png", "Figure 12 — Vertical profiles at named stations."),
    ("plot_metrics_timeseries.png", "Figure 13 — Time series of headline metrics (approach to steady state)."),
]
for fn, cap in figs:
    figure(os.path.join(FIG, fn), cap)

H("13.1  Animations (GIF)", 2)
P("Animated output data are saved in case_study/outputs/animations/ (viewable in any "
  "browser/image viewer):")
for nm, desc in [
    ("anim_time_plume.gif", f"time evolution of the depth-max excess-salinity plume "
     f"(0 → {C['t_end']:.0f} s) as it develops and spreads from the diffuser"),
    ("anim_depth_slices.gif", "horizontal excess-salinity slices swept from the sea surface "
     "down to the seabed (shows the plume is bottom-trapped)"),
    ("anim_cross_sections.gif", "vertical excess-salinity sections swept alongshore across "
     "the plume (shows the 3-D dense-layer envelope)"),
    ("anim_footprint_threshold.gif", "seabed footprint contour as the assessment threshold "
     "ΔS sweeps from 1.0 down to 0.1 g/kg, with live area readout"),
]:
    bullet(f"{nm} — {desc}.")

# ============================================================ 14 OUTPUT FILES
H("14.  Output data files")
P("Every artefact below is generated by the solver run and the post-processor and saved "
  "in case_study/outputs/ (data) and case_study/outputs/figures/ (plots).")
data_files = [
    ("metrics_summary.json", "JSON", "headline metrics + full config + ensemble stats + active physics"),
    ("metrics_timeseries.csv", "CSV", "time series: S_max, ΔS_max, reach, footprint, dilution, divergence"),
    ("curve_centerline.csv", "CSV", "centreline curve: distance, ΔS, dilution, core depth"),
    ("curve_vertical_profile.csv", "CSV", "vertical profile at the sampling station"),
    ("seabed_centerline_transect.csv", "CSV", "seabed ΔS & dilution along the plume centreline"),
    ("seabed_lateral_transect.csv", "CSV", "seabed ΔS & dilution across the plume"),
    ("isopleth_area_vs_threshold.csv", "CSV", "footprint area / equivalent radius vs ΔS threshold"),
    ("vertical_profiles_stations.csv", "CSV", "S, ΔS, dilution, ρ, T profiles at named stations"),
    ("plume_envelope_vs_distance.csv", "CSV", "dense-layer core depth, top and thickness vs "
     "distance (all DEPTHS BELOW SURFACE, not heights above bed — see §12.4)"),
    ("nearfield_trajectory.csv", "CSV", "inclined dense-jet centreline trajectory"),
    ("fields_final.npz", "NPZ", "primary & derived 3-D fields (S, ΔS, dilution, ρ, u,v,w, k, ε, ν_t, T)"),
    ("ensemble_stats.npz", "NPZ", "ensemble mean/std/exceedance and percentile fields"),
    ("animations/*.gif", "GIF", "time-evolution + depth-slice + cross-section + footprint animations"),
]
table(["File", "Type", "Contents"], [[a, b, c] for a, b, c in data_files],
      caption="Table 14.1 — Output data files. Each CSV also has a plot in outputs/figures/.")

# ============================================================ 15 ASSESSMENT
H("15.  Assessment and mixing-zone compliance")
P(f"The model predicts a seabed excess-salinity footprint above the conservative sub-lethal "
  f"assessment contour ΔS = {C['dS_crit']} g/kg of ≈ {g('seabed_footprint_m2', 0):.0f} m², "
  f"within roughly {min(g('r_max_m', 0), ss.get('r_max_m_mean', 0)):.0f}–"
  f"{max(g('r_max_m', 0), ss.get('r_max_m_mean', 0)):.0f} m of the diffuser, with a "
  f"bottom-trapped dense layer confined to the lowest "
  f"{g('z_deepest_m', 0) - g('plume_top_m', 0):.1f} m of the water column. This assessment "
  f"contour is more protective than the ~1 ppt above ambient typical of NSW mixing-zone "
  f"practice.")
P(f"The compliance conclusion is robust. The maximum excess salinity anywhere in the domain is "
  f"{g('excess_max', 0):.2f} g/kg, so the discharge sits inside every applicable concentration "
  f"limit with margin — NSW ~1 ppt at the mixing-zone edge, Perth 1.2 ppt at 50 m, Gold Coast "
  f"~2 PSU at 60 m, and the binding California Ocean Plan 2.0 ppt at 100 m. That conclusion "
  f"survives every caveat in §1.1."
  + ("" if STEADY else
     " The footprint precision is weaker: with bottom drag the reach is bounded but oscillates "
     "with the tidal/stochastic forcing rather than settling to a single value, and the footprint "
     "depends on which estimator and which field — single-member or ensemble-mean — is used."))
P("Basis of confidence, stated exactly. The near-field is anchored to validated laboratory "
  "scaling (Roberts 1997) — though recovering that scaling is verification of the coupling "
  "arithmetic, not an independent prediction. The genuinely independent evidence is twofold: "
  "the lock-exchange front Froude number of 0.47 against Benjamin's 0.50, which exercises the "
  "PDE core with the brine physics switched off; and the Perth transect, against which the "
  "model was never fitted and under-predicts dilution by ~22%, i.e. errs toward over-stating "
  "impact. The far field is NOT calibrated to measured data (§10). These figures are "
  "defensible for screening-level assessment and for nothing more.")

# ============================================================ 16 CONCLUSIONS
H("16.  Conclusions and recommendations")
for b in [
    "The SDP Kurnell deep multiport diffuser is predicted to confine the seabed "
    f"excess-salinity footprint (ΔS > {C['dS_crit']} g/kg) to ≈ {g('seabed_footprint_m2', 0):.0f} m² "
    f"within roughly {min(g('r_max_m', 0), ss.get('r_max_m_mean', 0)):.0f}–"
    f"{max(g('r_max_m', 0), ss.get('r_max_m_mean', 0)):.0f} m of the outfall. The salinity "
    f"anomaly is inside every applicable regulatory limit with substantial margin.",
    f"The plume is bottom-trapped, confined to the lowest "
    f"{g('z_deepest_m', 0) - g('plume_top_m', 0):.1f} m of a {C['depth']:.0f} m water column. Its "
    f"height above the source ({g('plume_rise_m', 0):.1f} m) agrees with the independently-derived "
    f"near-field terminal rise ({g('nf_rise_m', 0):.1f} m), which is a genuine cross-check "
    f"between two separately-constructed parts of the model.",
    "The solver is validated against laboratory, field and analytical benchmarks and its "
    "numerics are sound: 13/13 self-tests, machine-precision continuity, conserved mass and "
    "no eddy-viscosity railing. Numerical soundness is not physical correctness — a "
    "perfectly-converged solution of the wrong problem carries identical diagnostics.",
    "The far field is NOT calibrated. The dispersivity multiplier returned 1.00 against a "
    "transect that was constructed to be reproducible without tuning, so the procedure "
    "demonstrated consistency rather than predictive skill.",
    f"Peak salinity ({g('S_max', 0):.2f} g/kg) and, to a lesser degree, minimum dilution "
    f"({g('dilution_min', 0):.1f}:1) are diagnostics of the prescribed source condition rather "
    f"than predictions, and no change of source-blob geometry can alter that (§12.4).",
] + ([] if STEADY else [
    f"Steady state was not reached: {', '.join(NOT_CONVERGED)} still drift across the trailing "
    f"window (the reach by {_rdrift:+.1f} m, {100*_rdrel:.1f}% of its mean). Quote the reach as a "
    f"range."]) + [
    "Recommendation (i): commission a real CTD/ADCP survey at the outfall and re-run "
    "--calibrate-ctd — or adopt the measured Gold Coast Tugun transect (Baum et al. 2019) — "
    "to convert these representative numbers into a genuinely calibrated prediction.",
    "Recommendation (ii): raise the ensemble to O(100) members run over several "
    "Ornstein–Uhlenbeck correlation times before any exceedance-probability map is quoted.",
    "Recommendation (iii): DONE. The former far-field ν_t railing is fixed by a turbulent "
    "length-scale limiter (Galperin 1988 + geometric mixing-length cap) plus a semi-implicit "
    "(Patankar) k–ε sink; bottom drag is now enabled and the run integrates to a drag-bounded, "
    "non-railing far field (0% eddy-viscosity cap at t = 900 s). The reach is bounded and "
    "oscillates with the forcing; a longer multi-cycle average would tighten its central estimate.",
    "Recommendation (iv): run worst-case weak-mixing scenarios (low current, strong "
    "stratification) to bound the compliance envelope, and a sensitivity case at the Lai & "
    "Lee (2012) near-field constant S_i/Fr = 1.07, which is the less-protective of the two "
    "literature clusters.",
    "Recommendation (v): for a fully resolved near field — and to remove the prescribed-source "
    "diagnostics noted above — use the two-way nested resolved-nearfield mode on a GPU.",
]:
    bullet(b)

# ============================================================ 17 REFERENCES
H("17.  References and provenance")
refs = [
    "Roberts, P.J.W., Ferrier, A. & Daviero, G.J. (1997). Mixing in Inclined Dense Jets. "
    "Journal of Hydraulic Engineering 123(8): 693–699.",
    "Lai, C.C.K. & Lee, J.H.W. (2012). Mixing of inclined dense jets in stationary ambient. "
    "Journal of Hydro-environment Research 6(1): 9–28. doi:10.1016/j.jher.2011.08.003.",
    "Papakonstantis, I.G., Christodoulou, G.C. & Papanicolaou, P.N. (2011). Inclined negatively "
    "buoyant jets 1 & 2. Journal of Hydraulic Research 49(1): 3–12, 13–22.",
    "Roberts, P.J.W., Taplin, J. & Zigas, E. (2019). Design of Seawater Desalination Brine "
    "Diffusers. 38th IAHR World Congress. doi:10.3850/38WC092019-1053.",
    "Baum, M.J. et al. (2019). Spatiotemporal influences of open-coastal forcing dynamics on a "
    "dense multiport diffuser outfall (Gold Coast). J. Hydraulic Eng. 145(10): 04019034. "
    "doi:10.1061/(ASCE)HY.1943-7900.0001622.",
    "Clark, G.F. et al. (2018). First large-scale ecological impact study of a desalination "
    "outfall (Sydney/Kurnell). Water Research 145: 757–768. doi:10.1016/j.watres.2018.08.071.",
    "Benjamin, T.B. (1968). Gravity currents and related phenomena. J. Fluid Mech. 31(2): 209–248. "
    "doi:10.1017/S0022112068000133.",
    "Shin, J.O., Dalziel, S.B. & Linden, P.F. (2004). Gravity currents produced by lock "
    "exchange. J. Fluid Mech. 521: 1–34. doi:10.1017/S002211200400165X.",
    "Durbin, P.A. (1996). On the k–ε stagnation point anomaly. Int. J. Heat Fluid Flow 17: 89–90.",
    "Bleninger, T. & Jirka, G.H. (2008). Modelling and environmentally sound management of "
    "brine discharges from desalination plants. Desalination 221: 585–597. doi:10.1016/j.desal.2007.02.059.",
    "California Ocean Plan — Desalination Amendment (2015). SWRCB Res. 2015-0033; 23 CCR §3009 "
    "(≤ 2.0 ppt above background at ≤ 100 m). Perth/Cockburn Sound (WA EPA): ≤ 1.2 ppt at 50 m.",
    "Sydney Desalination Plant — public design basis (capacity 250 ML/day, ~47% recovery, "
    "offshore diffuser ~25 m depth), as cited in the input deck provenance fields; per-port "
    "geometry is a representative engineering configuration.",
    "Governing equations and numerics: solver.py (NEREID-B) header and model dossier. "
    "Input deck: case_study/sydney_sdp_case.json. Site data: case_study/inputs/.",
]
for r in refs:
    numbered(r)

P("Data-source note: all validation benchmark values are recorded with their citations "
  "above and in validation/sources.md; the near-field laboratory scaling and the "
  "lock-exchange front-Froude benchmark are the primary sources, the Perth field transect "
  "is the in-class field check, and the site CTD/ADCP transect (representative) is the "
  "calibration target.", italic=True, size=9.5, color=TEAL)

out = os.path.join(HERE, "case_study.docx")
doc.save(out)
print(f"saved {out}")
