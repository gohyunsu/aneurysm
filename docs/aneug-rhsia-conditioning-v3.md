# RHSIA conditioning-scale control

This is an explicit optimization adaptation of the direct comparator, not a
proposed architecture or an exact author-recipe reproduction. The original
`conditioning_normalization="none"` remains the default. Existing deployment
snapshots, learning curves and scientific identities must remain unchanged.
The implementation and prospective comparison axes are recorded in
`configs/aneug_rhsia_conditioning_control_v3.json`; that file does not activate
training or establish improved stability or accuracy.

## The intervention and its limits

The native temporal encoder concatenates an eight-channel learned time
feature and an eight-channel learned waveform feature. The optional
`separate_layer_norm` mode independently centers and variance-normalizes each
branch over its channels, for each requested snapshot, before concatenation.
It uses epsilon 1e-5 without learned affine parameters. There are no cross-case,
cross-phase or target-dependent statistics in this added operation. The
pre-existing waveform BatchNorm and all other native layers are retained.

Normalization accumulates in FP32 outside autocast (retaining FP64 when the
input is FP64), then returns the branch's incoming dtype. It therefore does
not undo prior low-precision rounding or make BF16 equivalent to FP32. Steady
masking is still last: phase -1 produces exactly zero temporal conditioning,
even after learned biases; phase 79 remains a genuine transient snapshot.
An all-steady call skips waveform processing as before.

The two spectral encoders, eight GPS blocks, eight bias-free injections and
all 80 native phase passes remain. Both modes have 3,071,337 trainable
parameters with the production-sized default core. No extra dummy parameters
or reduced spectral/feedforward widths are used to make the comparison match.

This control constrains the scale of finite branch outputs, not the subsequent
learned injection weights, GPS states or upstream derivatives. It does not
repair NaNs, guarantee useful gradients, convergence or better accuracy.
It also removes within-branch offset and amplitude information, which can be
useful: this is a real inductive-bias change, not a numerically equivalent
refactoring. A possible trade-off must be evaluated, particularly before
claiming anything about different inlet waveforms.

## Comparison rather than a new pass gate

Compare original/stabilized conditioning and FP32/BF16 training as separate
factors, with common FP32 full-cycle evaluation. Keep the same admitted
geometry inputs, split, waveform, physical objective, native core, phase
schedule, graph batch and seed-paired initialization. Pin each actual setting
and its budget before execution. Measure injection scale and geometry-gradient
behavior together with learning curves and actual cost, not only finite loss.
Such measurements can diagnose optimization but do not independently establish
the cause of field error on real surfaces.

A diagnosed unstable partial trajectory remains evidence, not a completed weak
baseline. It need not be blindly repeated to fill a factorial table; a repeat
must answer a new, recorded diagnostic question. Resource-related adaptations
or early investigation stops must be disclosed. Give a viable recipe adequate
learning and comparable tuning opportunities before headline comparison;
do not turn a short synthetic test into a performance admission threshold.

Development ranking uses validation physical field-rL2 point estimates, with
uncertainty, TAWSS/OSI and computational costs reported separately. An interval
containing zero is not a disqualification, nor is a point-estimate lead alone
statistically established superiority. No final recipe or scientific benefit
is selected by the implementation tests.

## Identity and verification

The opt-in setting adds no tensors, buffers or RNG draws at construction.
Consequently, equal checkpoint keys or parameter counts CANNOT identify which
equations produced a checkpoint. A fresh runtime must record and validate
`conditioning_normalization`, training/evaluation precision and source/config
hashes in provenance. Loading an old state into the normalized mode is an
intervention, not unchanged continuation. Existing activation validators must
not silently accept the new mode under an old exact architecture contract.

Synthetic regressions cover default behavior, independent branch statistics,
large finite features, post-bias steady masking, FP32/BF16 arithmetic, FP64
gradients, unchanged full parameter/state/RNG inventory, native backward
connectivity and all 80 phase passes. These are CPU implementation checks,
not allocated-CUDA, full-surface or dataset-performance evidence. See also
[the native comparator identity](aneug-rhsia-comparator-v3.md),
[snapshot training](aneug-rhsia-snapshot-training-v3.md) and
[precision execution](aneug-rhsia-execution-v3.md).
