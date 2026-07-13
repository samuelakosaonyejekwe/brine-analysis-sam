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
| PDE core benchmark | `python3 solver.py --benchmark` | **PASS** (lock-exchange Fr_f ≈ 0.51 vs theoretical 0.50) |
| Near-field calibration (measured field data) | `python3 solver.py --calibrate-nf case_study/inputs/gcdp_baum_case3-1_transect.csv` | **CALIBRATED** `nf_dilution_cal = 0.871` |
| Far-field vs measured field data | 4 measured Gold Coast cases (§10 of the report) | benchmark only — error spans 0.35×–3.4×; **not** systematically conservative |

## Reproduce the case study

```bash
python3 case_study/make_site_data.py                                   # site data
python3 solver.py --calibrate-nf case_study/inputs/gcdp_baum_case3-1_transect.csv   # near-field calibration
python3 solver.py --config case_study/sydney_sdp_case.json             # run the case
python3 case_study/postprocess.py                                      # full output suite
python3 case_study/build_docx.py                                       # build case_study.docx
```

The input deck carries the grid (52×32×26), ensemble (2), `t_end` (600 s) and the calibrated
`nf_dilution_cal` (0.871) that actually produced `case_study/outputs/`. Note that
`metrics_summary.json → footprint_vs_threshold` in the committed outputs was written with the
solver's default thresholds `[1.0, 1.5, 2.0]` (all zero, since the seabed peak excess is
0.96 g/kg); the authoritative threshold table is `outputs/isopleth_area_vs_threshold.csv`.

## Status of the case-study numbers — read before quoting them

The solver is validated and its numerics are sound. The Kurnell case study is **screening-grade**,
and four of its reported quantities are artefacts rather than predictions. This is stated in full in
§1.1 and §12.4 of `case_study/case_study.docx`.

- **Near field: CALIBRATED to measured field data.** `nf_dilution_cal = 0.871`, fitted to the measured
  48.4:1 dilution at the 60 m mixing-zone boundary of the Gold Coast Desalination Plant diffuser
  (Case 3-1, 100% capacity) — Baum (2019), PhD thesis, Univ. of Queensland, Tables 2.2–2.3;
  peer-reviewed as Baum, Gibbes, Grinham, Albert, Fisher & Gale (2018), *J. Hydraul. Eng.* 144(11),
  doi:10.1061/(ASCE)HY.1943-7900.0001524. The fitted **field** return-dilution coefficient is
  `S_r = 1.39·Fr`, 13% below the quiescent-**laboratory** `1.6·Fr` of Roberts et al. (1997) — a real
  diffuser in crossflow, waves and shear entrains less than a still lab tank. This *lowers* dilution and
  therefore *raises* the predicted footprint: calibrating against reality made the assessment more
  conservative, not less.
- **Far field: NOT calibrated — and it cannot realistically be calibrated by anyone.** `farfield_disp_cal`
  is *unidentifiable* where the data is: a 4× sweep moves the modelled dilution by **3.5% at 60 m**
  (near-field-dominated, `x_n = 9·Fr·d`) but **15% at 150 m** — so a fit needs stations beyond ~100 m.
  Out there the signal is gone: the WA EPA's Perth validation report gives far-field near-bed salinity
  increases of 0.0–0.45 units, states they are *model-derived* (simulations with vs without the
  discharge), and notes they are *"close to the accuracy and precision of the most accurate salinity
  measurements undertaken with CTDs"* (Seabird accuracy *"at best 0.02 units"*). By the distance at which
  far-field dispersion controls the plume, the brine anomaly is at the CTD noise floor. The far field of
  such models is **characterised, not fitted**. It stays at its physical default of 1.0 — a default, not
  a fit. This does not weaken the compliance verdict, because the licence's compliance point is inside
  the **near** field (below), which *is* calibrated.
- **Compliance point corrected — this moved the margin threefold.** The binding condition is
  **NSW EPL 12904, condition O5.1** (verified verbatim in the operator's annual report): salinity within
  **1 ppt of background at *the edge of the near-field mixing zone*** — the licence gives **no distance in
  metres**. That edge is `x_n = 9·Fr·d ≈ 26 m` — it is *not* the 50–100 m nominal mixing zone that is
  often assumed for such outfalls, and the difference is decisive. Modelled
  ΔS there is **0.71 g/kg → compliant, 29% margin**. The distance the condition is assessed at matters by
  a factor of three: at 50 m the excess is only ~0.2 g/kg, which would flatter the margin to ~80%. The
  operator's report also records a real O5.1 exceedance on 22/07/2025 — the limit is not academic, and a
  29% screening margin is not a consent case.
- **The model is NOT demonstrably conservative.** Against the four *measured* Gold Coast cases its
  dilution error spans 0.35×–3.4×, with no consistent sign, so no uniform conservative bias can be
  claimed. (The Perth 45:1 @ 50 m figure sometimes quoted for such a claim is a **design/compliance
  target, not a measurement**, and cannot support one.)
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
  and the OU correlation time (600 s) is as long as the run itself (600 s), so the forcing barely
  decorrelates.
- **Inactive physics.** Osmotic flux, osmotic body force, Soret/Dufour, the TEOS-10-style EOS terms
  and the free surface were **off** in the reported run. (Bottom drag and the wall function are now
  **on** — see the length-scale-limiter fix.)

What survives all of this: the maximum excess salinity is 0.99 g/kg (0.96 g/kg on the seabed) and the
seabed footprint is ≈2,859 m² — among the least affected quantities, because the source-blob error is
predominantly vertical. The discharge is compliant with EPL 12904 O5.1 (ΔS ≈ 0.71 g/kg at the ~26 m
near-field mixing-zone edge, against a 1 ppt limit), but with a **29% margin, not a comfortable one** —
and the plume core clears the 1.0 g/kg line by only 0.01 g/kg. Screening-grade: this is a case for
commissioning a site CTD/ADCP survey, not a consent case.

**Datum warning.** In `outputs/plume_envelope_vs_distance.csv`, `core_depth_*` and `layer_top_depth_*`
are **depths below the sea surface**, not heights above the seabed. A layer top of 0.48 m means the
impacted layer reaches to within 0.48 m of the *surface*.
