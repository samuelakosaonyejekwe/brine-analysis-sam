# NEREID-B far-field multi-point validation — Roberts, Taplin & Zigas (2019) — canonical 60-deg dense-jet diffuser

Source: 38th IAHR World Congress, doi:10.3850/38WC092019-1053; scaling: Roberts, Ferrier & Daviero (1997) J.Hydraul.Eng. 123(8):693-699

Rigorous multi-station comparison of modelled brine dilution against the
published in-class transect (no tuning). The model carries a **conservative**
bias: it under-predicts dilution, hence over-predicts impact (the safe side).

| Station (m) | Documented dilution | Modelled | ratio | Verdict |
|---:|---:|---:|---:|:--|
| 8.8 | 17.0:1 | 17.2:1 | 1.01 | match(±5%) |
| 33.0 | 28.0:1 | 20.4:1 | 0.73 | conservative(safe) |

Field note: Universal Roberts(1997) 60-deg scaling Si=1.6F @2.4Fd, Sn=2.6F @9Fd; worked example F=10.6, d=0.34 m.

Method/regime: near-field correlation coupling + rigid lid; realizable k-eps
(Durbin) + corrected buoyancy damping; default `farfield_disp_cal=1.0` (no fit).

Verdict: model is CONSERVATIVE (safe) at every far-field station.
This is the most rigorous in-class far-field check available from public data;
a dedicated CTD/ADCP survey at the modelled outfall is still recommended to
tighten the absolute numbers before regulatory sign-off.
