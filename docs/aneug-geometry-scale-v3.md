# Size-preserving geometry inputs

## Why a new input profile is needed

The legacy common reader centers each decoded mesh and divides it by that
mesh's RMS radius. Normals and normalized vertex areas also remain unchanged
under positive uniform dilation. A model consuming only these inputs cannot
distinguish geometrically similar objects of different size. Supplying GHD
descriptors changes the information condition; it does not establish parity
with the six-channel coordinate/normal sequence comparator.

[Sheng et al., III-F/III-G](https://arxiv.org/html/2601.19876v2) describe a
complete-sequence model with optional predicted-steady FiLM and normalize
coordinates using a dataset-level reference. Our earlier per-case adaptation
discarded size instead. This is an input-fidelity issue, not evidence of the
prior architecture's weakness or proof that a correction improves accuracy.

## Explicit, training-only correction

The original reader remains the default. With `retain_coordinate_scale=True`,
transient and eligible steady decoding additionally retain one scalar radius
in decoded source coordinate units. Every pre-existing tensor is unchanged.

For admitted transient training meshes only, fit a single isotropic reference
radius `r_train = sqrt(mean(r_case ** 2))`. Replace legacy coordinates with
`x_case * r_case / r_train`. This retains relative physical size without
changing mesh topology, normals, field labels, area weights, GHD normalization,
or the WSS evaluator. No coordinate unit such as metres is assumed. Translation
centering is still per mesh; this is an explicit train-only isotropic adaptation,
not the author's exact dataset-wide per-axis normalization.

Validation, eligible steady, and any later evaluation use the stored training
reference. They never refit it. The wrapper preserves the original steady-row
exclusions and sampling. Reapplying the transform is rejected. Model shapes and
parameter counts need not change; this introduces no architectural novelty.

## Evidence and use

Tests reproduce dilation erasure through the actual steady decoder and restore
it through the new transform. The full13902-node transient decoder retains
byte-identical legacy values. Target-access traps and an extreme nontraining
geometry check the fitted reference boundary. These tests do not quantify the
real cohort's size distribution, CFD sensitivity, or a trained accuracy gain.

Existing deployed sources/checkpoints must retain their old identity. Future
sequence/FiLM and other headline comparisons must explicitly agree on the
size-preserving input profile, with a fresh training run when inputs change.
Keep earlier curves as declared input ablations/development history; do not
silently relabel them as this corrected input condition.
