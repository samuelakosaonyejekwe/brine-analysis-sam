# Running NEREID-B on a GPU (Google Colab)

The CPU/NumPy path is the validated default. `solver.py` also carries a **CuPy GPU port**
(`cfg.gpu=True` / `--gpu`) that runs the per-step field kernels on an NVIDIA GPU. As of
**Rev 2.0** the sparse pressure solve can **also stay on the device** (`--gpu-poisson`) — no
per-step host↔device round-trip — for BOTH the free-surface AND rigid-lid cases.
`--gpu-poisson-direct` factorises the SPD operator ONCE on the device and reuses it (the
single-solve speedup), falling back to warm-started device PCG if the installed CuPy has no
sparse direct solver. The port is designed to be numerically identical to the CPU path —
verify that on a real device before trusting GPU runs.

## Quick start

1. Open `nereid_gpu_verify.ipynb` in Colab (Runtime ▸ Change runtime type ▸ **GPU**).
2. Run the install cell, **restart the session**, then run the rest.
3. Get `solver.py` into the working dir — clone your branch
   (`!git clone --branch solidify-solver <repo-url> nereid; %cd nereid`) or Files ▸ upload.
4. The checks:
   - `--gpu-verify` — same short sim on CPU and GPU (pressure solve on the host LU in both);
     **VERIFIED** at relative diffs ~1e-9–1e-6 means the field-kernel port is correct.
   - `--gpu-verify --gpu-poisson` — the **Rev 2.0 on-device pressure solve**; matches the host
     LU only to the CG tolerance, so the PASS band is **rel < 1e-4**. Add
     `--gpu-poisson-direct` to also verify the factorise-once device LU (or its PCG fallback).

This is a **one-time** trust check per environment, **not** a per-run prerequisite. Once it is
VERIFIED here, go straight to `--gpu --gpu-poisson` runs; re-verify only if you change the
CUDA/CuPy/numpy stack, the GPU type, or any GPU code path. CPU runs never need it.

## Dependency pins (important)

| package | version | why |
|---|---|---|
| numpy | **1.26.4** | numpy 2.x breaks scipy 1.11.4's sparse import → the pressure solver dies |
| scipy | 1.11.4 | sparse LU pressure solver |
| cupy | cupy-cuda12x | matches Colab's CUDA 12 runtime (use `cupy-cuda11x` if `nvidia-smi` shows CUDA 11) |
| gsw | optional | TEOS-10 `eos_mode="teos10"`; declares numpy>=2 but works on 1.26.4 — install with `--no-deps` only if needed |

## CLI

```bash
python solver.py --gpu-check                                  # report CuPy/CUDA device status
python solver.py --gpu-verify                                 # CPU-vs-GPU equivalence (host-LU Poisson)
python solver.py --gpu-verify --gpu-poisson                   # + on-device pressure solve (rel < 1e-4)
python solver.py --gpu-verify --gpu-poisson --gpu-poisson-direct  # + factorise-once device LU
python solver.py --gpu --gpu-poisson ...                      # run a prediction fully on the GPU
python solver.py --resolved-nearfield --gpu --gpu-poisson     # #7: fine-mesh two-way resolved near field
python solver.py --selftest                                   # 13/13 invariant checks (backend-agnostic)
```

A correct `--gpu-verify` (and `--gpu-verify --gpu-poisson` for the on-device solve) is the green
light to use `--gpu --gpu-poisson` for the large/fine-grid runs — including the `--resolved-nearfield`
near-field refinement — that are too expensive on CPU.
