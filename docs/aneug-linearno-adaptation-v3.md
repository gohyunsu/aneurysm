# LinearNO complete-cycle development baseline

This is a task adaptation of the official [LinearNO](https://github.com/HiPRL/LinearNO)
ShapeNetCar implementation at `3f2b80df13c17a09e250f2ebe4d4ecdfd4acf269`.
The private loader imports the actual original module and verifies both source
files against their Git objects and SHA-256 values. No author code is vendored
here. This is not a reproduction of its original benchmark or a new architecture.

## What remains original, and what changes

The linear-attention equations, five attention/MLP blocks, layer normalization,
initialization, width 256, eight heads and key ratio four remain in the author's
module. The 2-D unified-position grid and unused time-input branch are disabled.

The explicit WSS adaptation changes the input to the common geometry information:
three normalized coordinates, three mesh-derived normals, log relative vertex
area, and broadcast train-standardized 432-D GHD. This avoids withholding GHD
from LinearNO while giving it to the existing GHD/GPS comparator. A geometry-only
seven-channel variant is supported but must be separately identified.

The output has 240 channels per node, reshaped to 80 × nodes × 3. One forward
predicts the entire cycle, with the existing train-only physical output scale.
No target field, true steady CFD, time-varying input or node identifier enters
inference. No tangent projection, Fourier truncation or endpoint equality is
imposed. Complete-cycle readout is an adaptation, not an author-reported result.

## Initial execution, not a final strong-baseline verdict

`configs/aneug_linearno_development_v3.json` fixes a first 50-epoch learning-curve
run on the existing 584/73 train/validation cases, seed 20260901. AdamW uses
3e-4 learning rate, 1e-4 weight decay, two-case accumulation and field-only
relative squared error. The run has 29,200 cycle exposures, **2,336,000 phase-field
exposures**, and 14,600 optimizer updates. Validation chooses the lowest physical
field rL2, breaking ties toward the earliest epoch. OSI uses the existing
train-derived support rule. No absolute pass threshold or early stopping is used.

This first budget is not evidence that LinearNO is fully converged. Learning
curves, stability and actual compute guide a recorded extension or further
tuning before a final comparison. Current historical 251-epoch GHD results are
not equal-budget counterparts of this initial run. Parameter count, full-cycle
exposures, updates, validation cost, GPU model/time and peak memory are retained.

New source has synthetic adapter/trainer tests and an optional private test of
the actual upstream module. No synthetic result is a WSS performance result.
The v3 runtime is separate from all historical v2 runs and checkpoint paths.
The old test was already opened; this execution accesses train/validation only.
