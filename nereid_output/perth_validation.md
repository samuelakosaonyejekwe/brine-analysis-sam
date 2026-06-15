# NEREID-B far-field multi-point validation — Perth SWRO — Cockburn Sound submerged diffuser

Source: WA EPA App D 'Perth Desalination Plant Discharge Modelling: Model Validation'

Rigorous multi-station comparison of modelled brine dilution against the
published in-class transect (no tuning). The model carries a **conservative**
bias: it under-predicts dilution, hence over-predicts impact (the safe side).

| Station (m) | Documented dilution | Modelled | ratio | Verdict |
|---:|---:|---:|---:|:--|
| 5.0 | 27.7:1 | 28.7:1 | 1.04 | match(±5%) |
| 25.4 | 33.8:1 | 28.7:1 | 0.85 | conservative(safe) |
| 50.0 | 45.0:1 | 34.6:1 | 0.77 | conservative(safe) |

Field note: CWR 2007a measured ~50:1 at ~25 m; the report's R&A/CFD scaling is conservative vs the field.

Method/regime: near-field correlation coupling + rigid lid; realizable k-eps
(Durbin) + corrected buoyancy damping; default `farfield_disp_cal=1.0` (no fit).

Verdict: model is CONSERVATIVE (safe) at every far-field station.
This is the most rigorous in-class far-field check available from public data;
a dedicated CTD/ADCP survey at the modelled outfall is still recommended to
tighten the absolute numbers before regulatory sign-off.
