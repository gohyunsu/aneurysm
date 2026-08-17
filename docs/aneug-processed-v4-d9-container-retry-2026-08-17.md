# D9 container execution retry

## Scope

The original D9 R0 stopped before every data, model and metric read because PBS
allocated a TGPU node without NVIDIA UVM. Runtime revalidation R4 proved a
working introai9 route: `coss_a6gpu`, explicit `Qlist=a6000`, and the exact
pinned Torch 2.5.1+cu118 container.

This execution retry does not rename or modify the scientific method. The
original D9 config and implementation are pinned by SHA-256. The D5
406/51/51 component split, 70 sealed auxiliary cases, mesh-canonicalized target,
three-level scalar-vector backbone, direct/moment comparison, seed 1103,
optimization, validation selection and development thresholds are unchanged.

## Runtime and data boundary

R0 binds the processed data root read-only, verifies the passing R4 result and
container hash before access, and writes a new private cache and result record.
The public checkout is read-only inside the container. Only D5 train and
validation components may enter the cache; outer and auxiliary values remain
sealed.

R1 becomes executable only when the new cache contains a passing R0 manifest.
Direct-cycle and moment-POD runs consume the same read-only cache and exact
container in separate append-only result directories. R0 is bounded to four
hours and each R1 variant to twelve hours on one A6000 GPU.

All numeric results, checkpoints, cache contents and raw logs remain private.
This single-seed validation pilot is development evidence, not confirmation,
outer-test evidence or a paper claim.
