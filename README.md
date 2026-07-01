# NEREID-B — Universal Brine-Dispersion Solver & Sydney Case Study

**NEREID-B** (Nonlinear Eulerian Reactive-osmotic Effluent Integro-Dispersion solver)
is a single, universal Python solver for the salinity distribution, evolution,
dispersion and seabed distribution of a negatively-buoyant desalination **brine plume**
discharged from a submerged multiport diffuser / inclined dense jet into a moving,
stratified, wave-/tide-/wind-forced sea.

It bridges the gap that conventional practice splits across two incompatible tool
classes: integral **near-field** jet models (CORMIX, VISJET/JETLAG, Visual PLUMES) that
stop at the seabed return point, and coastal **far-field** circulation models (Delft3D,
MIKE-3, ROMS) that cannot resolve the jet. NEREID-B couples a validated inclined-dense-jet
correlation to a genuine 3-D finite-volume RANS far field with a full anisotropic
dispersion tensor, buoyancy-modified realizable k–ε turbulence, partial-cell bathymetry,
optional osmotic/thermohaline cross-fluxes, an optional free surface, and a native
Monte-Carlo stochastic ensemble for uncertainty.

**Author: Akosa Samuel Onyejekwe.** Independent research work. Licensed under the MIT License (see `LICENSE`).

## Repository layout

```
solver.py               The universal NEREID-B solver (self-contained; numpy+scipy, mpl optional)
cad_lib.py              Engineering drawing-sheet / dimensioning engine (matplotlib)
case_study/             SDP-Kurnell industrial case study (the deliverable)
  sydney_sdp_case.json    Input deck (model configuration)
  make_site_data.py       Reproducible generator of credible site-specific survey data
  postprocess.py          Full engineering output suite (contours, curves, transects, CSVs)
  build_docx.py           Assembles case_study.docx from the run outputs
  case_study.docx         THE holistic case-study document
  inputs/                 Site survey decks (bathymetry, CTD, ADCP, waves, wind, transect)
  outputs/                Solver + derived outputs (npz, csv, json) and outputs/figures/*.png
  drawings/               General-arrangement / diffuser / dispersion drawings
validation/             Gate logs + data-source record (selftest, validate, benchmark, calibration)
```

## Solver validation status (all green)

| Gate | Command | Result |
|------|---------|--------|
| Robustness invariants | `python3 solver.py --selftest` | **13/13 PASS** |
| Near-field lab scaling | `python3 solver.py --validate` | **4/4 PASS** (Roberts 1997) |
| PDE core benchmark | `python3 solver.py --benchmark` | **PASS** (lock-exchange Fr_f ≈ 0.47) |
| Far-field field transect | `python3 solver.py --validate-farfield perth` | conservative at every station |

## Reproduce the case study

```bash
python3 case_study/make_site_data.py                                   # site data
python3 solver.py --calibrate-ctd case_study/inputs/site_ctd_dilution_transect.csv
python3 solver.py --config case_study/sydney_sdp_case.json             # run the case
python3 case_study/postprocess.py                                      # full output suite
python3 case_study/build_docx.py                                       # build case_study.docx
```

## Colour policy

All generated figures use vivid, non-black palettes (turbo / plasma / cividis / YlGnBu
maps; teal/navy/orange line palette). No pure black is used for any fill, line or text.
