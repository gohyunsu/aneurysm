# Spatial-kernel transfer: candidate and matched-backbone controls

Status: implementation development, not a selected final method or trained
result. Existing LinearNO and RHSIA deployments are unchanged. The current
candidate is in `aneug_surface_transfer.py`; dimensions are recorded in
`configs/aneug_surface_transfer_model_v3.json`.

## What is shared, and what is not

The fresh encoder is the existing full-width GHD-conditioned mesh U-Net, with
its obsolete output head removed. It uses coordinates, normals, relative area,
GHD coefficients and the supplied three-level mesh hierarchy. No target or
case-identifier feature is admitted. The encoder's multiscale spatial features
are shared across regimes, as in ordinary multi-task models.

The additional bank contains R geometry-conditioned spatial kernels. For an
existing directed mesh edge j -> i, each positive weight is learned from
`[x_j - x_i, distance(i,j), dot(normal_i,normal_j)]`. Neighbor weights are
normalized separately for every destination and kernel. Kernel r aggregates
its learned projection of h_j and includes a pointwise h_i term. The R outputs
are computed once per geometry, not once per phase.

The steady path averages these bank outputs, lifts them to the encoder width,
and uses an ordinary steady adapter and a separate steady field head. It trains
the encoder, bank, lift, adapter and steady head. It does not train a temporal
router or constrain any transient output coefficient.

The transient path mixes the same bank with node- and frequency-dependent
softmax weights, then uses a transient adapter and the common coefficient
readout. Its effective kernel is `sum_r alpha(i,k,r) * K_r(i,j)`. The weights
depend on destination features and frequency, not separately on every edge.
This is an explicit kernel-mixture hypothesis, not proof of a new operator class.
The bank is learned jointly, not necessarily frozen after steady pretraining.

The temporal basis is the existing real, full-spectrum basis: 80 coefficients
for 80 nominal uniformly spaced phases, including one Nyquist cosine. Cosine
and sine of the same frequency share routing but have independent readout
weights. The DC coefficient remains free and is not the steady field. There is
no forced first/last-sample equality, truncated temporal spectrum, tangent
projection or separate TAWSS/OSI prediction. The candidate currently represents
the dataset's fixed waveform; it is not a variable-BC operator.

## Controls and initialization

| Variant | Ordinary task adapters | Extra spatial bank | Temporal routing |
|---|---|---|---|
| Fourier-only | None | None | None |
| Task adapters | Separate steady/transient | None | None |
| Always shared | Separate steady/transient | Same R kernels | Uniform, fixed |
| Geometry routing | Separate steady/transient | Same R kernels | Node-dependent, one mixture for all frequencies |
| Selective transfer | Separate steady/transient | Same R kernels | Node/frequency learned |

The Fourier-only transient path is exactly the preexisting full-width
`FourierCycleDecoder` algebra, with equivalent weights. It is not a reduced
decoder substituted to favor the candidate. Both output heads use the same
physical scaling; there is no true steady CFD inference input.

Within an information condition, all variants initialize the encoder and cycle
head identically under the same seed. Always-shared and selective also have
identical shared bank, adapters and steady head initialization: routing modules
are constructed last. Forcing that router to uniform recovers the always-shared
forward to numerical precision. The always-shared control computes its common
hidden features once, rather than repeating the same work for every mode.
T-only models do not retain unused steady modules. The new scientific runner
uses `build_paired_surface_transfer_model`: construct the common T+S layout
under the same seed, then remove steady-only heads/adapters for T. All common
parameters therefore initialize identically when their shapes match. The
shape-changing wide-adapter controls are explicitly separate information-
condition-specific capacity choices, not a claim of identical adapter weights.

The basic ladder matches backbone, information and coefficient head, NOT total
capacity or compute. The additional wide-adapter control is selected by nearest
parameter count alone: hidden199 for T-only (95 more parameters), hidden115
for T+S (162 fewer parameters), without a data/performance-based choice.
T+S counts are 2,170,076 (Fourier), 2,186,780 (ordinary adapter),
2,224,032 (always shared), 2,229,604 (selective) and 2,229,442 (wide adapter).
These are model-construction counts, not GPU cost or accuracy measurements.
Widened adapters need their own actual training/compute comparison before
attributing an advantage to selection. Ordinary feature/MoE routing is a relevant challenge;
gate visualization is not causal evidence of physical transferability.

### Isolating temporal-frequency conditioning

Uniform-versus-selective changes both location and frequency dependence. It
cannot, by itself, identify a frequency-specific benefit. The additional
`geometry_routing` control retains the selective model's geometry router,
spatial bank, adapters and all 80 independent coefficient readouts. It replaces
41 learned frequency offsets with one active shared offset. Therefore
`alpha(i,k,r) = alpha(i,r)` without forcing a constant output cycle. Steady
supervision follows exactly the same uniform-bank path and cannot train this
router. This is an attribution control, not another proposed novelty.

Common modules retain the selective model's seeded initialization; the single
offset starts from its DC row. The other 40 rows are discarded before an
optimizer is constructed, not retained as dummy capacity. With the production
width-32 router this removes 1,280 parameters in either information condition.
The comparison is consequently near-capacity, not exactly parameter-matched.
It is not compute-matched: the frequency-independent hidden path is computed
once, while the selective model keeps its bounded per-frequency computations.
Actual training cost and complete-cycle latency must be measured separately.

`configs/aneug_surface_routing_ablation_v3.json` records this prospective
contrast without changing the original four-variant recipe or any deployed
source. Synthetic tied-frequency and uniform-logit interventions establish
the expected algebra and gradient paths, not a trained accuracy result.
Fresh T and T+S training must share the existing split, admitted inputs,
train-only scaling, losses, exposures and selection policy. Retain completed
valid controls; select no checkpoint or threshold to favor frequency routing.

## Training and execution boundary

Both `forward_cycle` and `forward_single_field` are connected for real
backpropagation, and T-only exposes no unused auxiliary parameters. Unit tests
perform actual mixed updates with the existing physical cycle and steady losses,
including positive and negative gradient-path checks. A T-only synthetic run
also exercises the existing full cycle trainer and verifies its phase/cycle
exposure, optimizer, selection and artifact path. Production defaults retain
width128/heads4, four width32 kernels and width32 adapters. Smaller test fixtures
are only synthetic CPU tests, never a proposed full-resolution benchmark.

Mode chunks avoid materializing one giant forward temporary; they do not
guarantee constant training memory because autograd retains required activations.
Within each chunk, the deterministic routing/lift/adapter/hidden path is now
computed once per distinct frequency, then gathered for the independent
cosine/sine coefficient readouts. With80 coefficients and chunk8 this uses50
hidden frequency states instead of80 (chunk-boundary repetitions remain).
This is algebra-preserving reuse, not a new architecture or a measured GPU
speedup. An independent old-path float64 test checks full outputs and every
parameter gradient; no parameter, model-state key or input condition changes.
The actual full-resolution memory, training time and full-cycle latency are
unmeasured. There is no persistent geometry/learned-feature cache.

The admitted steady stream and common evaluator are now connected to an
explicit mixed trainer and separate private runtime. Read
[the training contract](aneug-surface-transfer-training-v3.md). Actual lazy-
reader tests and dropout/optimizer continuation tests exercise this path. No
private real-data mixed activation or proposed-model GPU result is implied.
Continue the running direct baselines and queued native measurement; do not
overwrite their pinned source with this candidate.

## Novelty boundary and required evidence

[Sheng/RHSIA](https://arxiv.org/html/2601.19876v2) already studies masked steady
augmentation and a predicted-steady FiLM sequence comparator. The transfer
object here is a learned spatial-kernel bank, not a predicted steady output.
[GNOT](https://proceedings.mlr.press/v202/hao23c.html) already uses geometric
gating, and [F-Adapter](https://arxiv.org/abs/2509.23173) allocates adaptation
capacity across frequency. Kernel sharing, adapters and routing remain prior art.
Our frequency index is temporal, not the spatial Fourier basis in every prior.

Only sufficiently trained direct baselines, ordinary-adapter/capacity controls,
selection interventions and paired multiseed/label-efficiency evidence can
establish a useful task-specific contribution. There is no proof of PDE
consistency, E(3) equivariance, mesh-independent operator convergence, clinical
utility or architectural superiority. Registered connectivity and fixed-waveform
limitations remain. A simpler winner is an acceptable scientific outcome.
