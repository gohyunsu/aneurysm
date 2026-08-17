# D9 GPU runtime revalidation

## Why this is a retry, not a new scientific method

D9 job `116549.ECE-util1` stopped before source hashing, tensor loading, model
construction and metric evaluation. The record is preserved, but this does not
justify discarding the D9 dataset, split or architecture. The current policy
therefore permits a new-ID retry after a data-free runtime diagnosis.

The failed job invoked `/home/introai9/miniconda3/bin/python`, yet the imported
Torch package came from the user site at
`/home/introai9/.local/lib/python3.9/site-packages`. Disabling the user site
leaves that interpreter without Torch. This is evidence of an unisolated
runtime, not proof that the user-site package caused the CUDA failure.

An existing 3,204,870,144-byte pinned Singularity image has SHA-256
`2da7b186ba8fc25efb1a5ffcbb5251974d11a57198a7c0970a61ae05b88681f2` and
independently imports Python 3.11.10, Torch 2.5.1+cu118 and CUDA runtime 11.8.

## Diagnostic

One short `introai9` PBS allocation records three independent checks:

1. scheduler-visible driver/device state through `nvidia-smi`;
2. the original host/user-site Torch CUDA smoke as a diagnostic comparator;
3. the pinned container under `singularity exec --nv --cleanenv`.

Each Python smoke requires CUDA visibility and a finite 2048×2048 matrix
multiplication. Host failure is nonblocking when the driver and pinned
container pass. Container pass selects the pinned image for a new-ID D9 R0
retry. Container failure triggers scheduler/driver/bind diagnosis before any
dataset or training access.

All logs and runtime results remain private. The diagnostic contains no AneuG
data path, field read, model, metric or scientific endpoint and does not update
the public site.

## R1 outcome and R2 diagnostic delta

R1 completed with scheduler device visibility but both host and pinned-
container Torch CUDA initialization failed. This rejects only the narrow
host-package explanation; it is still compatible with a bad inherited device
variable, missing/inaccessible UVM nodes, scheduler binding or low-level driver
initialization failure.

R2 therefore adds information rather than repeating R1. It records only
selected CUDA/NVIDIA environment keys and `/dev/nvidia*` metadata, calls
`cuInit` and `cuDeviceGetCount` without Torch, and compares inherited,
`CUDA_VISIBLE_DEVICES=0` and unset conditions in both runtimes. A matching
low-level and Torch pass in the pinned container selects the exact environment
normalization for D9 R0. If every condition fails, the records provide a
specific administrator/scheduler-level CUDA report and training remains paused.
