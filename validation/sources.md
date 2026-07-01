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
`F_H = U/√(g′H) = 0.50` (half-depth energy-conserving current).
**NEREID-B:** `Fr_f ≈ 0.47` → **PASS** (`--benchmark`).

- **Benjamin (1968)** *Gravity currents and related phenomena.* J. Fluid Mech. 31(2):209–248.
  **doi:10.1017/S0022112068000133 (verified)**. F_H=0.50.
- **Shin, Dalziel & Linden (2004)** *Gravity currents produced by lock exchange.* J. Fluid
  Mech. 521:1–34. **doi:10.1017/S002211200400165X (verified)**. Confirms F_H=0.50.
- **Huppert & Simpson (1980)** J. Fluid Mech. 99(4):785. **doi:10.1017/S0022112080000894
  (verified)** — deep-ambient F_h=1.19 (different scaling; do not conflate).

## 4. Turbulence-closure basis (MODEL)

- **Durbin (1996)** *On the k–ε stagnation point anomaly.* Int. J. Heat Fluid Flow
  17(1):89–90 (realizable time-scale limiter).
- **Munk & Anderson (1948)** *Notes on a theory of the thermocline.* J. Marine Res. 7:276–295.

## 5. Site calibration — SDP Kurnell CTD/ADCP transect (CALIBRATION)

Representative (credible, not measured per-station) survey — `case_study/inputs/
site_ctd_dilution_transect.csv`. Stations/dilution: 7 m→37:1, 15 m→40:1, 25 m→42:1,
50 m→44:1. **Result:** model reproduces 44:1 at the mixing-zone boundary at
`farfield_disp_cal = 1.0` (no hand-tuning; 2% error) — see `validation/ctd_calibration.log`
and `nereid_output/calibration.json`. Consistent with the Perth ~45:1 @50 m design value
and the Gold Coast measured range.

## 6. Regulatory mixing-zone limits (context)

- **California Ocean Plan — Desalination Amendment (2015) [BINDING]** — ≤ 2.0 ppt above
  natural background, daily max, ≤ 100 m from discharge (SWRCB Res. 2015-0033; 23 CCR §3009).
- **Perth / Cockburn Sound (WA) [BINDING]** — ≤ 1.2 ppt within 50 m; ≤ 0.8 ppt within 1,000 m.
- **Gold Coast (QLD) [BINDING]** — ≤ ~2 PSU above background at 60 m.
- **Sydney (Kurnell, NSW) [BINDING]** — within ~1 ppt of background at the near-field
  mixing-zone edge (~50–100 m; exact EPL distance *unverified*).
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
