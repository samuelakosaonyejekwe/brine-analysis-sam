# NEREID-B — Validation & calibration data sources

Provenance of every dataset used to calibrate and validate NEREID-B for the Sydney
Desalination Plant (SDP, Kurnell) brine-dispersion case study. DOIs are flagged
**verified** (Crossref-checked) or **format/unverified** where the primary PDF was
paywalled; numbers that could not be independently confirmed are marked *unverified*.
Conventions: `Fr = U_j/√(g′₀D)`; `z_t` terminal rise; `X_i` return distance;
`S_i` return dilution. ppt ≈ psu ≈ g/kg.

## 1. Near-field — inclined dense-jet laboratory scaling (VALIDATION)

Accepted 60° bands (multi-study): `z_t/(D·Fr) ≈ 2.0–2.2` (consensus ≈ 2.07);
`X_i/(D·Fr) ≈ 2.3–2.8`; return dilution `S_i/Fr ≈ 1.6` (Roberts, Papakonstantis cluster)
with a lower cluster ≈ 1.07 (Lai & Lee).
**NEREID-B:** `z_t/(D·Fr) = 2.20`, `S_i ≈ 1.6·Fr` → **4/4 PASS** (`--validate`), inside band.

- **Roberts, Ferrier & Daviero (1997)** *Mixing in Inclined Dense Jets.* J. Hydraulic
  Eng. 123(8):693–699. doi:10.1061/(ASCE)0733-9429(1997)123:8(693) *(ASCE format string;
  high-confidence, not page-verified)*. 60°: z_t/(D·Fr)=2.2, X_i/(D·Fr)=2.4, S_i/Fr=1.6±12%.
  → **primary 60° design reference.**
- **Lai & Lee (2012)** *Mixing of inclined dense jets in stationary ambient.* J.
  Hydro-environ. Res. 6(1):9–28. **doi:10.1016/j.jher.2011.08.003 (verified)**. Best
  full-angle dataset; 60°: z_t 2.08, X_i 2.84, S_i/Fr 1.07. Asymptotic S_t/Fr→0.45,
  S_i/Fr→1.06 (Fr≥20).
- **Shao & Law (2010)** *30°/45° inclined dense jets.* Environ. Fluid Mech. 10(5):521–553.
  **doi:10.1007/s10652-010-9171-2 (verified)**. 45°: S_i/Fr=1.26, X_i/(FrD)=3.33.
- **Papakonstantis et al. (2011)** Parts 1 & 2, J. Hydraulic Res. 49(1):3–12 / 13–22.
  **doi:10.1080/00221686.2010.537153** and **10.1080/00221686.2010.542617 (both verified)**.
  60°: z_t 2.15, S_i/Fr 1.68 (clusters with Roberts).
- Corroborating: Cipollina et al. (2005) JHE 131(11):1017 *(format DOI)*; Kikkert, Davidson
  & Nokes (2007) JHE 133(5):545; Abessi & Roberts (2014/2015) multiport JHE
  doi:10.1061/(ASCE)HY.1943-7900.0000882 / .0001032 (verified; impact dilution insensitive
  ~45–65°, highest near-field dilution at 60°); Palomar et al. (2012) model-vs-experiment
  review, Desalination 290 doi:10.1016/j.desal.2011.11.037.

## 2. Far-field — full-scale desalination outfall field data (VALIDATION)

- **Gold Coast (Tugun, QLD) — MEASURED** — Baum et al. (2019) *Spatiotemporal Influences
  of Open-Coastal Forcing on a Dense Multiport Diffuser Outfall.* J. Hydraulic Eng.
  145(10):04019034. **doi:10.1061/(ASCE)HY.1943-7900.0001622 (verified)**. Boundary dilution
  at 60 m ≈ 62.6 (full capacity), 15.8–67.9 across cases (low value = crossflow advection);
  impact distance ~10–30 m; permit <2 PSU at 60 m. → best exposed-coast diffuser field case.
- **Sydney (Kurnell, NSW) — MEASURED impact extent** — Clark et al. (2018) *First
  large-scale ecological impact study of a desalination outfall.* Water Research
  145:757–768. **doi:10.1016/j.watres.2018.08.071 (verified)**. Detectable effects to
  ~100 m, driven largely by diffuser-induced near-bed flow. → the actual SDP outfall.
- **Perth (Cockburn Sound) — DESIGN/PERMIT** — criterion <1.2 ppt at 50 m / <0.8 ppt at
  1,000 m; near-field ~45:1 @50 m is the widely-restated design value (WA EPA / Roberts et
  al. 2019). Measured near-field transect *unverified*. NEREID-B `--validate-farfield perth`
  is conservative at every station.
- **Israel (Sorek/Hadera) — MEASURED** — Kress et al. (2020) Water Research 171:115402.
  **doi:10.1016/j.watres.2019.115402 (verified)**. Bottom excess salinity 4.3–9.1% (~1.7–3.5 psu).
- **Carlsbad (CA) — MEASURED (channel, not diffuser)** — Petersen et al. (2019) Water
  11(2):208. **doi:10.3390/w11020208 (verified)**. Bottom plume to ~600 m.
- Generic design anchor — **Roberts, Taplin & Zigas (2019)** *Design of Seawater
  Desalination Brine Diffusers.* 38th IAHR World Congress. **doi:10.3850/38WC092019-1053
  (open)**. 60° multiport near-field S≈15:1–40:1 over tens of metres; S_a=1.4·S_m.

## 3. PDE core — lock-exchange gravity-current benchmark (VALIDATION)

Accepted full-depth Boussinesq high-Re value: front Froude number
`F_H = U/√(g′H) = 0.500` (half-depth energy-conserving current).
**NEREID-B:** `Fr_f = 0.51` → **PASS** (`--benchmark`), i.e. ~2% FAST — see the caveat below.

**TARGET VERIFIED AT SOURCE, INCLUDING THE NORMALISATION.** Benjamin's front condition is

    U / √(g′H)  =  √[ h(1−h)(2−h) / (1+h) ]      (h = current depth as a fraction of H)

At the energy-conserving depth `h = H/2` this evaluates to **exactly 0.5000**. It is normalised
on the **FULL depth H**, which is the same convention the solver uses (`Fr_f = U_f/√(g′H)`), so
the comparison is like-for-like. This matters because the usual failure mode with this benchmark
is a convention mismatch: the other constants in this literature — the √2 thin-current limit, and
the deep-ambient value of **1** that Shin et al. (2004) derive *in place of* √2 — belong to
different normalisations and regimes and must **not** be compared against ours.

**CAVEAT — the model is on the fast side, and the sign is worth recording.** Shin et al. (2004)
show the energy-conserving theory holds at high Re but that dissipation reduces the front speed
by *a few per cent below* the energy-conserving value. A physical current should therefore sit
slightly **under** 0.500. NEREID-B sits ~2% **over** it. The magnitude is small and inside any
sensible band for a finite grid, and it changes no conclusion — but it is the *opposite* sign to
the expected dissipative bias, and the solver's own note that "turbulent damping lowers it" is
not what its own number does.

- **Benjamin (1968)** *Gravity currents and related phenomena.* J. Fluid Mech. 31(2):209–248.
  doi:10.1017/S0022112068000133. F_H = 0.500 at h = H/2 (front condition above, evaluated).
- **Shin, Dalziel & Linden (2004)** *Gravity currents produced by lock exchange.* J. Fluid
  Mech. 521:1–34. doi:10.1017/S002211200400165X. Confirms the energy-conserving theory; finds
  dissipation reduces the front speed a few % below it; derives deep-ambient front Fr = 1
  (not √2) — a different regime, do not conflate.
- **Huppert & Simpson (1980)** J. Fluid Mech. 99(4):785. doi:10.1017/S0022112080000894 —
  deep-ambient F_h ≈ 1 (different scaling; do not conflate).

## 4. Turbulence-closure basis (MODEL)

- **Durbin (1996)** *On the k–ε stagnation point anomaly.* Int. J. Heat Fluid Flow
  17(1):89–90 (realizable time-scale limiter).
- **Munk & Anderson (1948)** *Notes on a theory of the thermocline.* J. Marine Res. 7:276–295.

## 5. Near-field calibration — MEASURED Gold Coast field data (CALIBRATION)

**Source (primary, read directly).** Baum, M.J. (2019). *Dense Jet Behaviour in Dynamic
Receiving Environments.* PhD thesis, School of Civil Engineering, University of Queensland.
Chapter 2, Tables 2.2–2.3. Peer-reviewed as **Baum, Gibbes, Grinham, Albert, Fisher & Gale
(2018)**, *Near-Field Observations of an Offshore Multiport Brine Diffuser under Various
Operating Conditions*, J. Hydraul. Eng. 144(11), doi:10.1061/(ASCE)HY.1943-7900.0001524.
Diffuser configuration independently corroborated by **Baum et al. (2017)**, Int. J. Civil &
Environmental Engineering 11(6):711–717.

**Site (in-class with Kurnell).** Gold Coast Desalination Plant offshore multiport diffuser,
Tugun QLD: 203 m diffuser, 14 ports at 13.9 m spacing, internal port diameter 0.238 m, ports
inclined at 60°, discharge elevation 2.5 m above the seabed, mean depth 17.7 m, open coast.
Regulatory mixing zone at 60 m. Config self-check: Q₀ = 2.30/14 = 0.164 m³/s → U₀ = 3.69 m/s,
g′ = 0.108 m/s² → **Fr = 23.0 against the published 23.4** (2% — confirms the table was read
correctly).

**MEASURED boundary dilution at 60 m** (thesis Table 2.3, "Field"):

| Case | Capacity | Fr | Measured S @ 60 m | NEREID-B @ 60 m (cal = 1.0) | model ÷ measured |
|------|----------|------|-------|-------|-------|
| 2-2  | 33%      | 10.7 | 67.7:1 | 24.0:1 | 0.35 |
| 3-1  | **100%** | 23.4 | **48.4:1** | 58.2:1 | 1.20 |
| 4-1  | 66%      | 24.1 | 22.4:1 | 75.8:1 | 3.38 |
| 4-2  | 66%      | 16.6 | 66.6:1 | 35.6:1 | 0.53 |

**Result — CALIBRATED:** `nf_dilution_cal = 0.871`, fitted to Case 3-1 (the only case with a
clean signal: full capacity, ambient drift −0.10 g/kg). Fitted **field** return-dilution
coefficient **S_r = 1.39·Fr**, against the quiescent-**laboratory** 1.6·Fr of Roberts et al.
(1997) — a real diffuser in crossflow/waves/shear entrains ~13% less than a still tank, which
is the central finding of Baum (2019). Sweep: nf_dilution_cal 0.40→1.30 spans 18.5:1→83.4:1,
so the target is properly bracketed. See `validation/nf_calibration.log`,
`nereid_output/nf_calibration.json`, `case_study/inputs/gcdp_baum_case*_transect.csv`.

**NOT calibrated — far field. This was investigated properly and is not a shortcut.**

`farfield_disp_cal` is **unidentifiable from any data that exists**, for two compounding reasons.

*(i) Where the knob has leverage.* Sweeping it 0.5→2.0 (4×) on the Kurnell configuration moves
the modelled dilution by:

| station | Δ dilution over a 4× sweep | identifiable? |
|---------|---------------------------|---------------|
| 60 m (mixing zone) | **3.5%** (57.7 → 59.3) | no — near-field-dominated (`x_n = 9·Fr·d`) |
| 150 m (far field)  | **15%** (1185 → 1010) | yes |

So a far-field calibration needs measured stations **beyond ~100 m**. The Gold Coast dataset
(the only in-class *measured* multi-case dilution data) stops at 60 m — inside the near field.

*(ii) Why no such measurement exists — the signal is below the instrument noise floor.* The WA
EPA's Perth model-validation report is the most thorough far-field brine study available
(BMT/Oceanica, *Perth Desalination Plant Discharge Modelling: Model Validation*, App. D of the
PSDP2 referral documents, epa.wa.gov.au). Its far-field near-bed salinity increases across the
monitoring rings are **0.0–0.45 units** (A stations 0.05–0.45; B 0.05–0.30; C 0.0–0.30;
D 0.0–0.30; CT 0.0–0.25) — and those figures are **model-derived** (from *"comparisons between
simulations with and without the discharge"*, which cannot be measured). The report states of
them: *"These increase values are close to the accuracy and precision of the most accurate
salinity measurements undertaken with CTDs"*, noting Seabird's *"dynamic accuracy of their CTD
probes are at best 0.02 units"*.

**Conclusion.** By the distance at which far-field dispersion controls the plume, the brine
anomaly has decayed to the CTD noise floor and into natural background variability. There is
therefore no credible measured dataset — at this site, at an in-class site, or in the wider
literature accessible here — capable of constraining a far-field dispersion coefficient for a
deep 60° diffuser. Calibrating it is **not realistic and not typical practice**; the far field
of such models is characterised, not fitted. `farfield_disp_cal` stays at its physical default
of **1.0 — a default, not a fit**, and this repo does not describe the far field as calibrated.

This also means the far field does **not** control the regulatory verdict: EPL 12904 condition
O5.1 sets the compliance point at the edge of the **near-field** mixing zone (≈26 m), which is
governed by the near-field coefficient — the parameter that *is* calibrated (above).

**Caveats, stated plainly.** (i) The three non-fitted cases are ambient-noise-limited: the
brine signal at 60 m is ≤0.53 g/kg while the *ambient* background varies by ±2 g/kg, and the
source authors caution against reading dilutions from the low-capacity cases. They are reported
as a **validation spread**, not fit targets — across them the model errs by 0.35×–3.4× in both
directions, so it is **not demonstrably conservative**. (ii) Gold Coast is **not Kurnell**: its
crossflow, wave climate and diffuser geometry differ. This is an in-class calibration, the best
available substitute for a site survey — not a site calibration.

**WITHDRAWN.** A prior revision calibrated against `site_ctd_dilution_transect.csv`, a synthetic
transect whose own generator comment recorded that its stations were chosen to be *"reproducible
by the model at no tuning"*. The `farfield_disp_cal = 1.00` it "returned" was not a fit but the
routine falling back to its default after failing to find leverage. That file and its generator
are **deleted**. The associated claim that the model is *"conservative, under-predicting dilution
by ~16–25%"* rested on Perth's 45:1 @ 50 m — a **design/compliance target, not a measurement** —
and is **withdrawn** from all documents.

## 6. Regulatory mixing-zone limits (context)

- **California Ocean Plan — Desalination Amendment (2015) [BINDING]** — ≤ 2.0 ppt above
  natural background, daily max, ≤ 100 m from discharge (SWRCB Res. 2015-0033; 23 CCR §3009).
- **Perth / Cockburn Sound (WA) [BINDING]** — ≤ 1.2 ppt within 50 m; ≤ 0.8 ppt within 1,000 m.
- **Gold Coast (QLD) [BINDING]** — ≤ ~2 PSU above background at 60 m.
- **Sydney (Kurnell, NSW) [BINDING] — VERIFIED at source.** Environment Protection Licence
  **EPL 12904** (NSW EPA), condition **O5.1**, quoted verbatim in the operator's own annual
  report: *"…at the edge of the near field mixing zone of the discharge plume the salinity of
  the seawater concentrate is within 1 part per thousand (ppt) of background salinity."*
  Condition **O5.2**: the dilution requirement does not apply when the concentrate salinity is
  at or below background.
  **The condition specifies NO DISTANCE IN METRES.** The compliance point is the edge of the
  **near-field** mixing zone — which for this discharge is `x_n = 9.0·Fr·d ≈ 26 m`
  (Roberts et al. 1997), NOT the 50–100 m an earlier revision of this repo assumed. Assuming a
  distant compliance point flattered the margin badly (ΔS ≈ 0.21 g/kg at 50 m vs ΔS ≈ 0.71 g/kg
  at 26 m). Source: Veolia, *Sydney Desalination Plant Annual Performance Report (EPL 12904),
  2024–25*, §5.7 "Salinity Difference – O5.1".
  Note the operator's report also records an actual exceedance: on 22/07/2025 *"the calculated
  'Edge of the near field mixing zone of the discharge plume' was greater than 1 ppt … of
  background salinity."* The limit is not academic.
- Guidance: **Bleninger & Jirka (2008)** Desalination 221:585–597
  **doi:10.1016/j.desal.2007.02.059 (verified)**; ANZECC (2000)/ANZG (2018) mixing-zone
  framework. The case adopts a more protective sub-lethal contour ΔS = 0.5 g/kg.

## Honest caveats
- Category-1 primary coefficients (Roberts/Cipollina/Kikkert) are frequently reported via
  the peer-reviewed Lai & Lee (2012) and Wood & Mead (2008, HR Wallingford HRPP 391)
  tabulations; cite the primary DOI but note the tabulation route.
- Best clean validation targets: dense-jet return distance & dilution (§1); Gold Coast field
  dilutions (§2); F_H = 0.50 lock-exchange (§3); California 2.0 ppt/100 m limit (§4).
- Items marked *unverified* should be confirmed against primary text before quoting a precise
  number. The SDP per-port nozzle geometry is a representative engineering configuration.
