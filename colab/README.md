# Running NEREID-B on a GPU (Google Colab)

The CPU/NumPy path is the validated default. `solver.py` also carries a **CuPy GPU port**
(`cfg.gpu=True` / `--gpu`) that runs the per-step field kernels on an NVIDIA GPU; the sparse
pressure solve stays on the host LU (one host↔device round-trip per step). The port is
designed to be numerically identical to the CPU path — verify that on a real device before
trusting GPU runs.

## Quick start

1. Open `nereid_gpu_verify.ipynb` in Colab (Runtime ▸ Change runtime type ▸ **GPU**).
2. Run the install cell, **restart the session**, then run the rest.
3. The key check is `--gpu-verify`: it runs the *same* short simulation on CPU and GPU and
   reports `max|CPU-GPU|` per field. **VERIFIED** (relative diffs ~1e-9–1e-6) means the port
   is correct.

## Dependency pins (important)

| package | version | why |
|---|---|---|
| numpy | **1.26.4** | numpy 2.x breaks scipy 1.11.4's sparse import → the pressure solver dies |
| scipy | 1.11.4 | sparse LU pressure solver |
| cupy | cupy-cuda12x | matches Colab's CUDA 12 runtime (use `cupy-cuda11x` if `nvidia-smi` shows CUDA 11) |
| gsw | optional | TEOS-10 `eos_mode="teos10"`; declares numpy>=2 but works on 1.26.4 — install with `--no-deps` only if needed |

## CLI

```bash
python solver.py --gpu-check     # report CuPy/CUDA device status
python solver.py --gpu-verify    # CPU-vs-GPU equivalence check (needs a CUDA device)
python solver.py --gpu ...       # run any prediction on the GPU (falls back to CPU if no GPU)
python solver.py --selftest      # 13/13 invariant checks (backend-agnostic)
```

A correct `--gpu-verify` is the green light to use `--gpu` for the large/fine-grid runs that
are too expensive on CPU.
