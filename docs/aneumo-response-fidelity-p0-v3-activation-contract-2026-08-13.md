# Aneumo response-fidelity P0 v3 activation contract

Status: **execution code ready · private activation manifest absent · current
container verdict absent · real P0 0/12**

## Why this layer is necessary

The immutable P0 v3 config is deliberately non-executable. It contains no
private server path and cannot be edited after registration. The historical
PBS wrapper calls P0 v2 and therefore cannot serve as v3 authority. A verified
server recovery alone would not solve this: an execution needs a separate,
prospectively frozen binding among one public source commit, the immutable v3
bytes, one private cache, one container and one output ledger.

The new activation runner and PBS wrapper close that operational gap without
creating such a binding now. They do not change a metric, threshold, family,
split, seed or P0 evaluator byte.

## Three distinct states

| State | What is known | What is allowed |
|---|---|---|
| Inventory | The privately reported cache digest matches the registered digest | No field-array access |
| Activation code ready | A public validator can check a future private manifest | Still no field-array access or submission |
| Activated after verified change | A private manifest pins all required bytes before a first P0-v3 attempt | Exactly one CPU-only train-field P0-v3 PBS attempt |

The project is currently in the second row. No private activation manifest has
been registered.

## Prospective private manifest contract

Only after independently verified introai9 operational change and readability
evidence may a private manifest be created. Its bytes must be frozen before
submission and must contain:

1. an external-change evidence identifier and UTC registration time;
2. affirmative container and cache readability checks performed without an
   HDF5 field-array read;
3. zero prior P0-v3 scientific attempts;
4. one exact public commit and the immutable v3 config/evaluator hashes;
5. the activation-runner hash and the separately pinned manifest hash;
6. exact private cache path, byte count and registered digest;
7. exact base-container path and digest plus the exact `h5py==3.12.1` wheel
   path and digest used as a network-free job-local runtime layer;
8. private output root; and
9. the fixed introai9 PBS envelope: queue `coss_agpu`, 4 CPU, 16 GB, 0 GPU,
   one hour, no network and one shot.

Unknown or extra keys fail. Any path outside the introai9 scope, changed cache
or container, dirty/different public source, prior same-version attempt, GPU,
pressure, validation/test field, model, architecture, outer test or paper-claim
authority also fails before HDF5 field access.

## Execution and evidence flow

```text
verified operational change
        ↓
readability evidence without field-array access
        ↓
private manifest registered and SHA-256 pinned
        ↓
introai9 PBS wrapper validates source/container/manifest/cache envelope
        ↓
network-free pinned wheel install in job-local temporary storage
        ↓
immutable P0 v3 reads train coordinates + velocity only
        ↓
private aggregate + minimal attempt status
        ↓
12/12 → permission to register a fresh baseline-only P1 version
<12/12 → close P0 v3; no repair or rerun
```

An execution-incomplete status is not a scientific failure or pass. It also
cannot be retried under the same source and contract. A completed failure is
preserved and closes the direction. A completed 12/12 pass does not authorize a
model, GPU, validation/test field, outer test or manuscript claim.

## Current evidence boundary

The originally documented base image is readable and pins NumPy 2.1.2 and CPU
PyTorch 2.5.1, but does not contain `h5py`. The activation layer therefore
requires a separately hashed `h5py==3.12.1` wheel, verifies it before data
access and installs it with `--no-index --no-deps` into job-local temporary
storage. This dependency closure does not change a scientific byte or permit a
second attempt.

The validator's synthetic fixtures show only that valid authority is accepted
and path, container, manifest, compute and scientific-authority drift are
rejected. They are code tests, not Aneumo evidence. This update performs no
server query, transfer, scheduler access, PBS submission, cache read, field
read, monitoring or GPU work. The current status remains 0/12.
