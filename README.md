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

The input deck now carries the grid (52×32×26), ensemble (2) and `t_end` (200 s) that actually
produced `case_study/outputs/`. Note that `metrics_summary.json → footprint_vs_threshold` in the
committed outputs was written with the solver's default thresholds `[1.0, 1.5, 2.0]` (all zero,
since the seabed peak excess is 0.84 g/kg); the authoritative threshold table is
`outputs/isopleth_area_vs_threshold.csv`.

## Status of the case-study numbers — read before quoting them

The solver is validated and its numerics are sound. The Kurnell case study is **screening-grade**,
and four of its reported quantities are artefacts rather than predictions. This is stated in full in
§1.1 and §12.4 of `case_study/case_study.docx`.

- **Not calibrated.** `farfield_disp_cal` returned 1.00 against a transect that `make_site_data.py`
  constructed to be "reproducible by the model at no tuning". That is a consistency check, not a
  calibration. The independent far-field evidence is the Perth transect (~22% conservative) and the
  lock-exchange benchmark.
- **The source blob is grid-limited.** `solver.py:1012` floors the seed width at
  `1.5*max(dx, dz)` = 8.65 m against a physical return-plume width of 2.50 m, injecting brine over
  ~⅓ of the water column. Consequently `S_max` is exactly the injected `S_source`, the 32:1 minimum
  dilution is a datum artefact, the affected volume is inflated, and the plume is **not**
  bottom-trapped near the source (it is, beyond ~30 m). Fix: make the floor anisotropic (`1.5*dz`
  vertically) and re-run.
- **Steady state was not reached for the reach.** `r_max` grows monotonically 26 → 96 m and is still
  rising at `t_end`. It passes the steady-state test only because that test bounds relative scatter
  (`steady_tol = 0.20`), not trend. The domain flush time is ≈2,500 s.
- **The 2-member ensemble cannot support statistics.** The exceedance field takes only {0, 0.5, 1},
  and the OU correlation time (600 s) exceeds the run length (200 s).
- **Inactive physics.** Osmotic flux, osmotic body force, Soret/Dufour, the TEOS-10-style EOS terms,
  the free surface, bottom drag and the wall function were all **off** in the reported run.

What survives all of this: the maximum excess salinity is 0.99 g/kg (0.84 g/kg on the seabed), inside
every applicable regulatory limit with margin, and the seabed footprint of ≈5,127 m² is among the
least affected quantities because the source-blob error is predominantly vertical.

**Datum warning.** In `outputs/plume_envelope_vs_distance.csv`, `core_depth_*` and `layer_top_depth_*`
are **depths below the sea surface**, not heights above the seabed. A layer top of 0.48 m means the
impacted layer reaches to within 0.48 m of the *surface*.
